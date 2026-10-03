import random
import string
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.user import User, Role
from models.subject import UserSubject
from core.security import hash_password, verify_password, create_access_token
from schemas.auth import RegisterRequest, TokenResponse


def generate_personal_number(db: Session) -> str:
    """Generate a unique 6-digit staff number like ES-123456."""
    while True:
        number = "ES-" + "".join(random.choices(string.digits, k=6))
        existing = db.exec(select(User).where(User.personal_number == number)).first()
        if not existing:
            return number


def register_user(data: RegisterRequest, db: Session) -> User:
    # Check email uniqueness
    existing = db.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    personal_number = generate_personal_number(db)

    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=Role.TEACHER,
        personal_number=personal_number,
        is_approved=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Attach selected subjects
    for subject_id in (data.subjects or []):
        link = UserSubject(user_id=user.id, subject_id=subject_id)
        db.add(link)
    db.commit()

    return user


def authenticate_user(email: str, password: str, db: Session) -> TokenResponse:
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.role == Role.TEACHER and not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, role=user.role)


def change_password(user: User, current_password: str, new_password: str, db: Session) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()
