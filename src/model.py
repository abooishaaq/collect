import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import select, func

Base = declarative_base()


class Form(Base):
    __tablename__ = "forms"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))


class FieldType(enum.Enum):
    text = 1
    number = 2


class Field(Base):
    __tablename__ = "fields"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    name = Column(String(255), nullable=False)
    type = Enum(FieldType, nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)


class Meta(Base):
    __tablename__ = "meta"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    queries = Column(Integer, nullable=False)
    submissions = Column(Integer, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)


class Query(Base):
    __tablename__ = "queries"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    query = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)


class ResponseText(Base):
    __tablename__ = "response_text"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    response = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey(
        "fields.id", ondelete="CASCADE"), nullable=False)
    submission_id = Column(UUID(as_uuid=True), ForeignKey(
        "submissions.id", ondelete="CASCADE"), nullable=False)


class ResponseNumber(Base):
    __tablename__ = "response_numbers"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    response = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(UUID(as_uuid=True), ForeignKey(
        "fields.id", ondelete="CASCADE"), nullable=False)
    submission_id = Column(UUID(as_uuid=True), ForeignKey(
        "submissions.id", ondelete="CASCADE"), nullable=False)


class WebHook(Base):
    __tablename__ = "webhooks"
    id = Column(UUID(as_uuid=True), primary_key=True,
                default=func.uuid_generate_v4())
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=select(func.now()))
    query = Column(String(255), nullable=True)
    form_id = Column(UUID(as_uuid=True), ForeignKey(
        "forms.id", ondelete="CASCADE"), nullable=False)
