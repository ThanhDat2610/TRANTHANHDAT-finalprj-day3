from fastapi import APIRouter, Depends, status,Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth import register_user, login_user
from app.schemas.user import UserResponse
from app.models.user import UserModel
from app.security import get_current_user, require_role
from app.services.user import get_current_user_67, get_user_for_admin
from app.utils.exceptions import create_response

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/user/me", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def get_user(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_current_user_67(current_user, db)


@router.get("/user/admin")
def list_users(
    request: Request,
    search: str | None = None,
    is_active: bool | None = None,
    admin: UserModel = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    """Admin lấy danh sách user, hỗ trợ tìm kiếm và lọc theo trạng thái."""
    users = get_user_for_admin(db, search=search, is_active=is_active)
    data = [UserResponse.model_validate(user) for user in users]

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách người dùng thành công",
        data=data,
        path=request.url.path,
    )