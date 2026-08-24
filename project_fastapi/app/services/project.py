from sqlalchemy.orm import Session
from app.models.project import Project, ProjectMember
from app.models.user import UserModel
from fastapi import HTTPException, status

def create_project(db: Session, owner: UserModel, project_data: dict) -> Project:
    """Tạo project mới, người tạo tự động trở thành OWNER trong project_members."""
    new_project = Project(
        name=project_data["name"],
        description=project_data.get("description"),
        owner_id=owner.id,
    )
    db.add(new_project)
    db.flush()  # để new_project.id có giá trị (đã sinh UUID) trước khi tạo ProjectMember, chưa commit

    owner_membership = ProjectMember(
        project_id=new_project.id,
        user_id=owner.id,
        role="OWNER",
    )
    db.add(owner_membership)
  
    db.commit()
    db.refresh(new_project)
    return new_project

def get_user_projects(
    db: Session,
    current_user: UserModel,
    search: str | None = None,
) -> list[Project]:
    """
    Lấy danh sách project mà user hiện tại là OWNER hoặc MEMBER.
    Hỗ trợ tìm kiếm theo tên project (không phân biệt hoa/thường).
    """
    query = (
        db.query(Project)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .filter( (Project.owner_id == current_user.id) | (ProjectMember.user_id == current_user.id)).distinct()
    )

    if search:
        keyword = f"%{search}%"
        query = query.filter(Project.name.ilike(keyword))

    return query.all()



def get_project_by_id(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy project")
    return project


def check_owner(project: Project, current_user: UserModel):
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ chủ sở hữu (OWNER) mới có quyền thực hiện thao tác này",
        )


def update_project(
    db: Session,
    project_id: str,
    current_user: UserModel,
    update_data: dict,
) -> Project:
    project = get_project_by_id(db, project_id)
    check_owner(project, current_user)

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: str, current_user: UserModel) -> None:
    project = get_project_by_id(db, project_id)
    check_owner(project, current_user)

    db.delete(project)
    db.commit()


def add_member(
    db: Session,
    project_id: str,
    current_user: UserModel,
    user_id: str,
    role: str = "MEMBER",
) -> ProjectMember:
    project = get_project_by_id(db, project_id)
    check_owner(project, current_user)

    # Kiểm tra user cần thêm có tồn tại không
    user_to_add = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy user")

    # Kiểm tra đã là member chưa (tránh trùng)
    existing = (
        db.query(ProjectMember).filter(ProjectMember.project_id == project_id,ProjectMember.user_id == user_id,).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User này đã là thành viên của project",
        )

    new_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

def remove_member(
    db: Session,
    project_id: str,
    current_user: UserModel,
    user_id: str,
) -> None:
    project = get_project_by_id(db, project_id)
    check_owner(project, current_user)

    member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User này không phải thành viên của project",
        )

    # Chặn xoá OWNER cuối cùng
    if member.role == "OWNER":
        owner_count = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.role == "OWNER",
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể xoá OWNER cuối cùng của project",
            )

    db.delete(member)
    db.commit()

def get_project_members(
    db: Session,
    project_id: str,
    current_user: UserModel,
) -> list[ProjectMember]:
    project = get_project_by_id(db, project_id)

    # Chỉ member (hoặc owner) của project mới xem được danh sách thành viên
    is_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not is_member and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải thành viên của project này",
        )

    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id)
        .all()
    )