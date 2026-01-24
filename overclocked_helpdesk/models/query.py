from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from overclocked_helpdesk.db.session import Base


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=True)

    issue = Column(String, nullable=False)
    location = Column(String, nullable=False)
    # lifecycle: PENDING -> ASSIGNED -> RESOLVED
    status = Column(String, default="PENDING", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", backref="queries")
    mentor = relationship("Mentor", backref="queries")
