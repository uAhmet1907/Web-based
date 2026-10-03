from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_db
from core.dependencies import get_current_user, require_admin
from models.user import User
from models.subject import Subject, DEFAULT_SUBJECTS

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("/", response_model=List[dict])
def list_subjects(
    grade_level: Optional[str] = None,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all subjects.
    Optionally filter by grade_level (e.g. ?grade_level=KG1 returns only KG subjects).
    """
    stmt = select(Subject)
    subjects = db.exec(stmt).all()

    if grade_level:
        subjects = [
            s for s in subjects
            if grade_level in (s.grades or "")
        ]

    return [{"id": s.id, "name": s.name, "level": s.level, "grades": s.grades} for s in subjects]


@router.post("/seed", response_model=dict)
def seed_subjects(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: seed the default subject list (idempotent)."""
    added = 0
    for entry in DEFAULT_SUBJECTS:
        existing = db.exec(select(Subject).where(Subject.name == entry["name"])).first()
        if not existing:
            db.add(Subject(
                name=entry["name"],
                level=entry.get("level"),
                grades=entry.get("grades"),
            ))
            added += 1
    db.commit()
    return {"seeded": added}
