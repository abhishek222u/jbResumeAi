import uuid
from sqlalchemy import Column, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Answer(Base):
    __tablename__ = "answers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True))
    answer_text = Column(Text)
    score = Column(Integer)
    feedback = Column(Text)
