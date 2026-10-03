from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User


DEFAULT_SUBJECTS = [
    {"name": "German",           "level": "primary", "grades": "1-6"},
    {"name": "Mathematics",      "level": "primary", "grades": "1-6"},
    {"name": "LNMG",             "level": "primary", "grades": "1-6"},
    {"name": "Art (BG)",         "level": "primary", "grades": "1-6"},
    {"name": "Music",            "level": "primary", "grades": "1-6"},
    {"name": "PE",               "level": "primary", "grades": "1-6"},
    {"name": "Textiles & Crafts","level": "primary", "grades": "1-6"},
    {"name": "French",           "level": "primary", "grades": "3-6"},
    {"name": "English",          "level": "primary", "grades": "5-6"},
    {"name": "Free Play",        "level": "kg",      "grades": "KG"},
    {"name": "Movement",         "level": "kg",      "grades": "KG"},
    {"name": "Crafts",           "level": "kg",      "grades": "KG"},
]


class Subject(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    level: str  # "primary" or "kg"
    grades: str  # e.g. "1-6", "3-6", "KG"

    user_subjects: List["UserSubject"] = Relationship(back_populates="subject")


class UserSubject(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    subject_id: Optional[int] = Field(default=None, foreign_key="subject.id", primary_key=True)

    user: Optional["User"] = Relationship(back_populates="user_subjects")
    subject: Optional["Subject"] = Relationship(back_populates="user_subjects")
