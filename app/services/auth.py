from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.security import verify_password, get_password_hash, create_access_token
from app.models.user import UserModel

def get_user_by_email(db: Session, email: str):
    """Tìm kiếm user trong DB theo email."""
    return db.query(UserModel).filter(UserModel.email == email).first()

def register_user(db: Session, user_data: dict):
    """Đăng ký user mới: kiểm tra trùng, băm mật khẩu và lưu vào DB."""
    if get_user_by_email(db, user_data["email"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại"
        )
    hashed_pw = get_password_hash(user_data["password"])
    new_user = UserModel(
        full_name=user_data["username"],
        password_hash=hashed_pw,  
        email = user_data["email"],
        role=user_data.get("role", "user")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, login_data: dict) -> dict:
    """Xác thực đăng nhập và cấp token JWT."""
    user = get_user_by_email(db, login_data["email"])
    if not user or not verify_password(login_data["password"], user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác"
        )
    return {
        "access_token": create_access_token({"sub": user.id, "role": user.role}),
        "token_type": "bearer"
    }
