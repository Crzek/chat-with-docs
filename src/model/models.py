import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, ForeignKey, DateTime, LargeBinary, Text
)
from sqlalchemy.dialects.postgresql import UUID, BYTEA
from sqlalchemy.orm import relationship
from src.config.settings import env

from . import Base  # __init__


class UserDB(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))

    files = relationship("FileDB", back_populates="user")
    messages = relationship("MessageDB", back_populates="user")


class FileDB(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True),
                         default=datetime.now(timezone.utc))
    file_metadata = Column(Text, nullable=True)

    user = relationship("UserDB", back_populates="files")
    messages = relationship("MessageDB", back_populates="file")

    def get_abs_path(self) -> str:
        return env.BASE_DIR + self.file_name


class MessageDB(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"))
    message_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))

    user = relationship("UserDB", back_populates="messages")
    file = relationship("FileDB", back_populates="messages")
