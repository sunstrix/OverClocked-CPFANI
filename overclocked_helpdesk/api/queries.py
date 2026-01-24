from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_

from overclocked_helpdesk.db.session import get_db
from overclocked_helpdesk.models.query import Query
from overclocked_helpdesk.models.mentor import Mentor
from overclocked_helpdesk.services.email_service import send_email_alert

router = APIRouter(prefix="/queries", tags=["queries"])


# -------------------------------------------------
# Get all pending queries (unassigned)
# -------------------------------------------------
@router.get("/pending")
def get_pending_queries(db: Session = Depends(get_db)):
    queries = (
        db.query(Query)
        .filter(
            Query.status == "PENDING",
            Query.mentor_id == None
        )
        .order_by(Query.created_at.asc())
        .all()
    )

    return [
        {
            "id": q.id,
            "team_id": q.team_id,
            "issue": q.issue,
            "created_at": q.created_at.strftime("%H:%M"),
        }
        for q in queries
    ]


# -------------------------------------------------
# Get queries visible to a mentor
# -------------------------------------------------
@router.get("/mentor/{mentor_id}")
def get_active_queries_for_mentor(
    mentor_id: int,
    db: Session = Depends(get_db)
):
    queries = (
        db.query(Query)
        .filter(
            or_(
                and_(
                    Query.status == "PENDING",
                    Query.mentor_id == None
                ),
                and_(
                    Query.status == "ASSIGNED",
                    Query.mentor_id == mentor_id
                )
            )
        )
        .order_by(desc(Query.created_at))
        .all()
    )

    return [
        {
            "id": q.id,
            "team_id": q.team_id,
            "issue": q.issue,
            "status": q.status,
            "created_at": q.created_at.strftime("%H:%M"),
        }
        for q in queries
    ]


# -------------------------------------------------
# Mentor accepts a query
# -------------------------------------------------
@router.patch("/{query_id}/accept/{mentor_id}")
def accept_query(
    query_id: int,
    mentor_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Query).filter(Query.id == query_id).first()
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()

    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    if query.status != "PENDING" or query.mentor_id is not None:
        raise HTTPException(status_code=400, detail="Query already taken")

    if not mentor.is_active:
        raise HTTPException(status_code=400, detail="Mentor not available")

    # assign query
    query.mentor_id = mentor.id
    query.status = "ASSIGNED"

    mentor.current_load += 1
    if mentor.current_load >= mentor.max_load:
        mentor.is_active = False

    db.commit()

    # -------- EMAIL (TEXT + HTML) --------
    text_body = (
        "You have accepted a helpdesk query.\n\n"
        f"Team: {query.team_id}\n"
        f"Issue: {query.issue}\n"
    )

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="color-scheme" content="dark">
  <meta name="supported-color-schemes" content="dark">
  <style>
    /* Force Dark Mode defaults */
    :root {{
      color-scheme: dark;
      supported-color-schemes: dark;
    }}
    body {{ margin: 0; padding: 0; width: 100%; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; background-color: #050505 !important; color: #ededed !important; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; }}
    a {{ text-decoration: none; color: #ededed; }}
  </style>
</head>
<body style="margin:0; padding:0; background-color:#050505 !important; color:#ededed !important; font-family:'Segoe UI', Helvetica, Arial, sans-serif;">

  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#050505; width:100%;">
    <tr>
      <td align="center" style="padding: 40px 10px;">

        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:500px; background-color:#0f0f11; border:1px solid #27272a; border-radius:16px; overflow:hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
          
          <tr>
            <td style="padding: 24px 32px; background-color:#141417; border-bottom:1px solid #27272a;">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="color:#ededed; font-size:18px; font-weight:800; letter-spacing:-0.5px;">
                    OverClocked
                  </td>
                  <td align="right">
                    <span style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2); color:#818cf8; font-family:'Courier New', monospace; font-size:10px; font-weight:700; padding:4px 8px; border-radius:6px; letter-spacing:0.5px;">
                      TICKET CONFIRMED
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td style="padding: 32px;">
              
              <h1 style="margin:0 0 12px 0; font-size:22px; font-weight:700; color:#ededed;">
                Query Assigned Successfully!
              </h1>
              <p style="margin:0 0 24px 0; font-size:14px; color:#a1a1aa; line-height:1.6;">
                You have successfully accepted a new helpdesk query. Please proceed to the location below to assist the team.
              </p>

              <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#18181b; border:1px solid #27272a; border-radius:12px;">
                
                <tr>
                  <td style="padding:20px; border-bottom:1px solid #27272a;">
                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                      <tr>
                        <td width="50%" valign="top" style="padding-right:10px;">
                          <div style="font-family:'Courier New', monospace; font-size:10px; color:#6366f1; font-weight:700; text-transform:uppercase; margin-bottom:6px;">
                            TARGET TEAM
                          </div>
                          <div style="font-size:16px; font-weight:600; color:#ededed;">
                            {query.team_id}
                          </div>
                        </td>
                        <td width="50%" valign="top" style="border-left:1px solid #27272a; padding-left:20px;">
                          <div style="font-family:'Courier New', monospace; font-size:10px; color:#6366f1; font-weight:700; text-transform:uppercase; margin-bottom:6px;">
                            LOCATION
                          </div>
                          <div style="font-size:16px; font-weight:600; color:#ededed;">
                            {query.location}
                          </div>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <tr>
                  <td style="padding:20px;">
                    <div style="font-family:'Courier New', monospace; font-size:10px; color:#ef4444; font-weight:700; text-transform:uppercase; margin-bottom:8px;">
                      REPORTED ISSUE
                    </div>
                    <div style="font-size:14px; line-height:1.5; color:#e4e4e7;">
                      {query.issue}
                    </div>
                  </td>
                </tr>
              </table>

            </td>
          </tr>

          <tr>
            <td align="center" style="padding:20px; border-top:1px solid #27272a; background-color:#0a0a0c;">
              <p style="margin:0; font-family:'Courier New', monospace; font-size:10px; color:#52525b; letter-spacing:1px; text-transform:uppercase;">
                Automated System Notification
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>
"""

    send_email_alert(
        to_email=mentor.email,
        subject="OverClocked Helpdesk - Query Assigned",
        body=text_body,
        html=html_body
    )

    return {
        "ok": True,
        "query_id": query.id,
        "mentor_id": mentor.id,
        "current_load": mentor.current_load
    }


# -------------------------------------------------
# Resolve a query
# -------------------------------------------------
@router.patch("/{query_id}/resolve")
def resolve_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Query).filter(Query.id == query_id).first()

    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    if query.status == "RESOLVED":
        return {"ok": True}

    mentor = None
    if query.mentor_id:
        mentor = db.query(Mentor).filter(Mentor.id == query.mentor_id).first()

    query.status = "RESOLVED"

    if mentor and mentor.current_load > 0:
        mentor.current_load -= 1
        if mentor.current_load < mentor.max_load:
            mentor.is_active = True

    db.commit()

    return {"ok": True, "query_id": query.id}


# -------------------------------------------------
# Get single query
# -------------------------------------------------
@router.get("/{query_id}")
def get_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    query = db.query(Query).filter(Query.id == query_id).first()

    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    return {
        "id": query.id,
        "team_id": query.team_id,
        "mentor_id": query.mentor_id,
        "issue": query.issue,
        "status": query.status,
        "created_at": query.created_at.isoformat(),
    }
