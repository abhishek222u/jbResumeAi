import uuid
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Question(Base):
    __tablename__ = "questions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True))
    question = Column(Text)
