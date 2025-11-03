from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .db import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    hard_chores_counter = Column(Integer, nullable=False, default=0)
    outer_partner_counter = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

