from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from overclocked_helpdesk.db.session import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    location = Column(String, nullable=True)

    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)

    mentor = relationship("Mentor")
