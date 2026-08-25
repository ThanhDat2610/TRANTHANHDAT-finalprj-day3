from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.services.project import create_project, get_user_projects, get_project_by_id
from app.db.database import get_db
from app.models.user import UserModel
from app.schemas.project import ProjectBase, ProjectResponse, ProjectUpdate, AddMemberRequest, ProjectMemberResponse, ProjectMemberDetailResponse
from app.security import get_current_active_user
from app.services.project import create_project, update_project, delete_project, add_member, remove_member,  get_project_members
from app.utils.exceptions import create_response


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    request: Request,
    payload: ProjectBase,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint tạo project mới.
    - Yêu cầu user đã đăng nhập (Bearer token).
    - Người tạo tự động trở thành OWNER (ghi vào project_members).
    """
    project = create_project(db, owner=current_user, project_data=payload.model_dump())
    data = ProjectResponse.model_validate(project)

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo project thành công",
        data=data,
        path=request.url.path,
    )

@router.get("")
def list_projects_router(
    request: Request,
    search: str | None = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    projects = get_user_projects(db, current_user=current_user, search=search)
    # data = [ProjectResponse.model_validate(p) for p in projects]

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách project thành công",
        data=projects,
        path=request.url.path,
    )


@router.get("/{project_id}")
def get_projects_by_id_router(
    project_id:str,
    db: Session = Depends(get_db),
):
    project = get_project_by_id(db, project_id)
   

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách project thành công",
        data=project,
        
    )

@router.patch("/{project_id}")
def update_project_router(
    request: Request,
    project_id: str,
    payload: ProjectUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Chỉ OWNER được sửa project."""
    update_data = payload.model_dump(exclude_unset=True)
    project = update_project(db, project_id, current_user, update_data)
    data = ProjectResponse.model_validate(project)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Cập nhật project thành công",
        data=data,
        path=request.url.path,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_router(
    project_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Chỉ OWNER được xoá project."""
    delete_project(db, project_id, current_user)
    return create_response(
            status_code=status.HTTP_200_OK,
            message="Xoa project thành công"
        )




@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
def add_member_router(
    request: Request,
    project_id: str,
    payload: AddMemberRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    OWNER thêm user vào project.
    - Chỉ OWNER mới thêm được.
    - Không cho thêm trùng (user đã là member).
    """
    member = add_member(
        db,
        project_id=project_id,
        current_user=current_user,
        user_id=payload.user_id,
        role=payload.role,
    )
    data = ProjectMemberResponse.model_validate(member)

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Thêm thành viên thành công",
        data=data,
        path=request.url.path,
    )


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member_router(
    project_id: str,
    user_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    OWNER xoá 1 thành viên khỏi project.
    - Chỉ OWNER mới xoá được.
    - Không được xoá OWNER cuối cùng của project.
    """
    remove_member(db, project_id=project_id, current_user=current_user, user_id=user_id)


@router.get("/{project_id}/members")
def list_project_members_endpoint(
    request: Request,
    project_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Trả danh sách thành viên và role trong project."""
    members = get_project_members(db, project_id=project_id, current_user=current_user)

    data = [
        ProjectMemberDetailResponse(
            user_id=m.user.id,
            full_name=m.user.full_name,
            email=m.user.email,
            role=m.role,
            joined_at=m.joined_at,
        )
        for m in members
    ]

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách thành viên thành công",
        data=data,
        path=request.url.path,
    )