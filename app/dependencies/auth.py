
import jwt
from app.models.user import UserModel
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
# Khóa bí mật dùng để ký và giải mã JWT (cần giữ bí mật tuyệt đối ở production)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
EXPIRE_MINUTES = settings.EXPIRE_MINUTES

security = HTTPBearer()

# ---------- Dependency: lấy user hiện tại từ token ----------


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Lấy JWT từ Authorization: Bearer <token>
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError:
        raise credentials_exception

    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user

# ---------- Dependency: chỉ cho phép user đang active ----------

def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hoá",
        )
    return current_user


def require_role(*allowed_roles: str):
    """
    Trả về 1 dependency chỉ cho phép user có role nằm trong allowed_roles.
    Dùng: Depends(require_role("ADMIN"))
          Depends(require_role("ADMIN", "MANAGER"))
    """
    def role_checker(
        current_user: UserModel = Depends(get_current_active_user),
    ) -> UserModel:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu quyền: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker
