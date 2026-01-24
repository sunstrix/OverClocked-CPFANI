from overclocked_helpdesk.db.session import Base, engine

# Import all models so SQLAlchemy knows them
from overclocked_helpdesk.models.mentor import Mentor
from overclocked_helpdesk.models.team import Team
from overclocked_helpdesk.models.query import Query


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Database tables created")
