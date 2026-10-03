from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from models.user import User
    from models.request import SubstituteRequest


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int = Field(foreign_key="substituterequest.id")
    teacher_id: int = Field(foreign_key="user.id")
    status: ApplicationStatus = Field(default=ApplicationStatus.PENDING)
    applied_at: datetime = Field(default_factory=datetime.utcnow)

    request: Optional["SubstituteRequest"] = Relationship(back_populates="applications")
    teacher: Optional["User"] = Relationship(back_populates="applications")
