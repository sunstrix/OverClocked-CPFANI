from sqlalchemy.orm import Session
from overclocked_helpdesk.models.team import Team
from overclocked_helpdesk.models.mentor import Mentor


def assign_mentor(db: Session, team_id: int) -> Mentor | None:
    """
    ONLY selects a mentor.
    Does NOT modify workload.
    Does NOT commit.
    """

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return None

    primary = team.mentor

    # 1. Try primary mentor
    if primary and primary.is_active and primary.current_load < primary.max_load:
        return primary

    # 2. Fallback to least-loaded active mentor
    mentor = (
        db.query(Mentor)
        .filter(
            Mentor.is_active == True,
            Mentor.current_load < Mentor.max_load
        )
        .order_by(Mentor.current_load.asc())
        .first()
    )

    return mentor
