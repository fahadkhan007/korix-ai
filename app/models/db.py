from sqlalchemy import Column, String, Boolean, DateTime, Text
from app.core.database import Base


class User(Base):
    __tablename__ = "User"

    id         = Column(String, primary_key=True)
    email      = Column(String, unique=True, nullable=False)
    name       = Column(String, nullable=True)
    isVerified = Column(Boolean, default=False)
    createdAt  = Column(DateTime, nullable=False)


class Task(Base):
    __tablename__ = "Task"

    id          = Column(String, primary_key=True)
    title       = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status      = Column(String, nullable=False)   # TODO | IN_PROGRESS | IN_REVIEW | DONE
    priority    = Column(String, nullable=False)   # LOW | MEDIUM | HIGH | URGENT
    projectId   = Column(String, nullable=False)
    assigneeId  = Column(String, nullable=True)
    reporterId  = Column(String, nullable=False)
    dueDate     = Column(DateTime, nullable=True)
    createdAt   = Column(DateTime, nullable=False)


class ProjectMember(Base):
    __tablename__ = "ProjectMember"

    id        = Column(String, primary_key=True)
    projectId = Column(String, nullable=False)
    userId    = Column(String, nullable=False)
    role      = Column(String, nullable=False)     # ADMIN | MEMBER | VIEWER


class Conversation(Base):
    __tablename__ = "Conversation"

    id        = Column(String, primary_key=True)
    projectId = Column(String, nullable=False)
    name      = Column(String, nullable=True)
    type      = Column(String, nullable=False)     # PROJECT
    createdAt = Column(DateTime, nullable=False)


class Message(Base):
    __tablename__ = "Message"

    id             = Column(String, primary_key=True)
    conversationId = Column(String, nullable=False)
    senderId       = Column(String, nullable=False)
    content        = Column(Text, nullable=False)
    messageType    = Column(String, nullable=False)  # TEXT | SYSTEM | AI
    createdAt      = Column(DateTime, nullable=False)
