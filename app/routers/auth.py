from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth import register_user, login_user
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])



@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Endpoint xử lý đăng ký tài khoản mới.
    - Validate dữ liệu đầu vào theo UserRegisterRequest
    - Kiểm tra username đã tồn tại chưa
    - Băm mật khẩu bằng Bcrypt trước khi lưu vào DB
    """
    user = register_user(db, request.model_dump())
    return user

@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint xử lý đăng nhập.
    - So khớp username và password bằng bcrypt.checkpw
    - Cấp phát Access Token JWT kèm payload (sub, role)
    """
    return login_user(db, request.model_dump())

