from sqlalchemy import Column, Integer, String, Boolean

from overclocked_helpdesk.db.session import Base


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    current_load = Column(Integer, default=0)
    max_load = Column(Integer, default=3)

    slack_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
