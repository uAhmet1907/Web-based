from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlmodel import Session

from database import get_db
from core.dependencies import get_current_user
from models.user import User
from services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=dict)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's full profile including subjects."""
    subjects = profile_service.get_user_subjects(current_user.id, db)
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "bio": current_user.bio,
        "personal_number": current_user.personal_number,
        "role": current_user.role,
        "is_approved": current_user.is_approved,
        "profile_picture": current_user.profile_picture,
        "documents_path": current_user.documents_path,
        "subjects": [{"id": s.id, "name": s.name, "level": s.level} for s in subjects],
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.patch("/", response_model=dict)
def update_my_profile(
    full_name: Optional[str] = Form(default=None),
    phone: Optional[str] = Form(default=None),
    bio: Optional[str] = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update name, phone and/or bio."""
    user = profile_service.update_profile(current_user, full_name, phone, bio, db)
    return {"id": user.id, "full_name": user.full_name, "phone": user.phone, "bio": user.bio}


@router.put("/subjects", response_model=dict)
def update_my_subjects(
    subject_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Replace the current user's subject list."""
    profile_service.update_subjects(current_user, subject_ids, db)
    subjects = profile_service.get_user_subjects(current_user.id, db)
    return {"subjects": [{"id": s.id, "name": s.name} for s in subjects]}


@router.post("/picture", response_model=dict)
async def upload_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload / replace profile picture."""
    user = profile_service.upload_profile_picture(current_user, file, db)
    return {"profile_picture": user.profile_picture}
