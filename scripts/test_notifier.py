from overclocked_helpdesk.db.session import SessionLocal
from overclocked_helpdesk.services.notifier import notify_and_create_query

db = SessionLocal()

notify_and_create_query(
    db=db,
    team_id=1,
    issue="Final integrated test issue",
    location="Lab 2"
)

db.close()
