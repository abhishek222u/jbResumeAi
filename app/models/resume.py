import uuid
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text)
