from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import UserModel
import app.security as security

def get_current_user_67(current_user,db:Session):
    return current_user

def get_user_for_admin(
    db: Session,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[UserModel]:
    """Lấy danh sách user, có thể lọc theo search (tên/email) và trạng thái active."""
    query = db.query(UserModel)

    if search:
        keyword = f"%{search}%"
        query = query.filter(
            (UserModel.full_name.ilike(keyword)) | (UserModel.email.ilike(keyword))
        )

    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)

    return query.all()