from overclocked_helpdesk.db.session import SessionLocal
from overclocked_helpdesk.models.mentor import Mentor
from overclocked_helpdesk.models.team import Team


def seed_data():
    db = SessionLocal()

    # Clear existing data (safe during dev)
    db.query(Team).delete()
    db.query(Mentor).delete()
    db.commit()

    # Create mentors
    mentors = [
        Mentor(name="Mentor 1", email="mentor1@test.com", slack_id="UXXXX1"),
        Mentor(name="Mentor 2", email="mentor2@test.com", slack_id="UXXXX2"),
        Mentor(name="Mentor 3", email="mentor3@test.com", slack_id="UXXXX3"),
    ]

    db.add_all(mentors)
    db.commit()

    # Refresh to get IDs
    for m in mentors:
        db.refresh(m)

    # Create teams and assign mentors
    teams = [
        Team(name="Team 1", location="Lab 1", mentor_id=mentors[0].id),
        Team(name="Team 2", location="Lab 2", mentor_id=mentors[1].id),
        Team(name="Team 3", location="Lab 3", mentor_id=mentors[2].id),
    ]

    db.add_all(teams)
    db.commit()

    db.close()
    print("Seed data inserted")


if __name__ == "__main__":
    seed_data()
