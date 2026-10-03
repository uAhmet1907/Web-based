import os
import shutil
from typing import List, Optional

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from models.user import User, Role
from models.subject import Subject, UserSubject

PROFILE_PIC_DIR = "uploads/profile_pictures"
os.makedirs(PROFILE_PIC_DIR, exist_ok=True)


def get_user_by_id(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_profile(
    user: User,
    full_name: Optional[str],
    phone: Optional[str],
    bio: Optional[str],
    db: Session,
) -> User:
    if full_name is not None:
        user.full_name = full_name
    if phone is not None:
        user.phone = phone
    if bio is not None:
        user.bio = bio
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_subjects(user: User, subject_ids: List[int], db: Session) -> User:
    # Remove all existing subject links for this user
    existing = db.exec(select(UserSubject).where(UserSubject.user_id == user.id)).all()
    for link in existing:
        db.delete(link)

    # Add new links
    for sid in subject_ids:
        subject = db.get(Subject, sid)
        if subject:
            db.add(UserSubject(user_id=user.id, subject_id=sid))

    db.commit()
    return user


def upload_profile_picture(user: User, file: UploadFile, db: Session) -> User:
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(status_code=400, detail="Only JPG/PNG/WEBP images allowed")

    dest = os.path.join(PROFILE_PIC_DIR, f"{user.id}{ext}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    user.profile_picture = dest
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_teachers(db: Session) -> List[User]:
    return db.exec(select(User).where(User.role == Role.TEACHER)).all()


def get_pending_teachers(db: Session) -> List[User]:
    return db.exec(
        select(User)
        .where(User.role == Role.TEACHER)
        .where(User.is_approved == False)
    ).all()


def approve_teacher(user_id: int, db: Session) -> User:
    user = get_user_by_id(user_id, db)
    if user.role != Role.TEACHER:
        raise HTTPException(status_code=400, detail="User is not a teacher")
    user.is_approved = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def reject_teacher(user_id: int, db: Session) -> None:
    user = get_user_by_id(user_id, db)
    db.delete(user)
    db.commit()


def get_user_subjects(user_id: int, db: Session) -> List[Subject]:
    links = db.exec(select(UserSubject).where(UserSubject.user_id == user_id)).all()
    subjects = []
    for link in links:
        s = db.get(Subject, link.subject_id)
        if s:
            subjects.append(s)
    return subjects
