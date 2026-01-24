from sqlalchemy.orm import Session
from overclocked_helpdesk.models.query import Query
from overclocked_helpdesk.services.slack_service import send_slack_alert


def notify_and_create_query(
    db: Session,
    team_id: int,
    issue: str,
    location: str
) -> Query:

    # 1. Create query ONLY
    query = Query(
        team_id=team_id,
        issue=issue,
        location=location, 
        status="PENDING",
        mentor_id=None
    )

    db.add(query)
    db.commit()
    db.refresh(query)

    # 2. Notify slack only
    send_slack_alert(
        team_name=f"Team {team_id}",
        location=location,
        issue=issue
    )

    return query
