from datetime import date as DateType
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session

from database import get_db
from core.dependencies import get_current_user, require_admin, require_teacher
from models.user import User
from models.request import SubstituteRequest, GRADE_LEVELS
from services import request_service

router = APIRouter(prefix="/requests", tags=["requests"])


# ── admin endpoints ───────────────────────────────────────────────────────────

@router.get("/", response_model=List[dict])
def list_all_requests(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: list all requests."""
    return [_serialize(r) for r in request_service.get_all_requests(db)]


@router.post("/", response_model=dict, status_code=201)
def create_request(
    date: DateType,
    grade_level: str,
    subject_id: int,
    time_slot: Optional[str] = None,
    note: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: create a new substitute request."""
    req = request_service.create_request(date, grade_level, subject_id, time_slot, note, admin.id, db)
    return _serialize(req)


@router.delete("/{request_id}", status_code=204)
def delete_request(
    request_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: delete a request."""
    request_service.delete_request(request_id, db)


@router.patch("/{request_id}/close", response_model=dict)
def close_request(
    request_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: manually close a request."""
    req = request_service.close_request(request_id, db)
    return _serialize(req)


@router.delete("/cleanup/expired", response_model=dict)
def cleanup_expired(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin: delete all expired requests."""
    count = request_service.delete_expired_requests(db)
    return {"deleted": count}


# ── teacher endpoints ─────────────────────────────────────────────────────────

@router.get("/open", response_model=List[dict])
def list_open_requests(
    grade_level: Optional[str] = None,
    _teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Teacher: list open (non-expired) requests, optionally filtered by grade."""
    if grade_level:
        reqs = request_service.get_requests_by_grade(grade_level, db)
        reqs = [r for r in reqs if r.status.value == "open"]
    else:
        reqs = request_service.get_open_requests(db)
    return [_serialize(r) for r in reqs]


@router.post("/{request_id}/apply", response_model=dict, status_code=201)
def apply(
    request_id: int,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Teacher: apply for a substitute request."""
    app = request_service.apply_for_request(request_id, teacher.id, db)
    return {"id": app.id, "request_id": app.request_id, "status": app.status}


# ── shared ────────────────────────────────────────────────────────────────────

@router.get("/grade-levels", response_model=List[str])
def grade_levels():
    """Return all valid grade levels."""
    return GRADE_LEVELS


def _serialize(req: SubstituteRequest) -> dict:
    return {
        "id": req.id,
        "date": str(req.date),
        "grade_level": req.grade_level,
        "subject_id": req.subject_id,
        "time_slot": req.time_slot,
        "note": req.note,
        "status": req.status,
        "expires_at": req.expires_at.isoformat() if req.expires_at else None,
        "created_by": req.created_by,
        "created_at": req.created_at.isoformat(),
    }
