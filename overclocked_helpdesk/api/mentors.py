from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from overclocked_helpdesk.db.session import get_db
from overclocked_helpdesk.models.mentor import Mentor
from overclocked_helpdesk.models.query import Query

router = APIRouter(prefix="/mentors", tags=["mentors"])


# ---------------------------
# Toggle mentor availability
# ---------------------------
@router.patch("/{mentor_id}/toggle-availability")
def toggle_availability(mentor_id: int, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()

    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    mentor.is_active = not mentor.is_active
    db.commit()
    db.refresh(mentor)

    return {
        "mentor_id": mentor.id,
        "is_active": mentor.is_active,
        "current_load": mentor.current_load,
        "max_load": mentor.max_load,
    }


# ---------------------------
# Mentor state polling
# ---------------------------
@router.get("/state")
def mentor_state(db: Session = Depends(get_db)):
    mentors = db.query(Mentor).all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "is_active": m.is_active,
            "current_load": m.current_load,
            "max_load": m.max_load,
        }
        for m in mentors
    ]


# ---------------------------
# Fetch active queries for mentor
# ---------------------------
@router.get("/{mentor_id}/queries")
def mentor_queries(mentor_id: int, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()

    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")

    queries = (
        db.query(Query)
        .filter(
            Query.mentor_id == mentor_id,
            Query.is_resolved == False
        )
        .order_by(Query.created_at.desc())
        .all()
    )

    return [
        {
            "id": q.id,
            "team_id": q.team_id,
            "issue": q.issue,
            "created_at": q.created_at.isoformat(),
        }
        for q in queries
    ]
