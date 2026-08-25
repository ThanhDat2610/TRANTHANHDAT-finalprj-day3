from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.project import ProjectMember
from app.models.task import Task
from app.models.user import UserModel
from app.services.project import get_project_by_id, check_member, is_project_member, check_owner


def create_task(
    db: Session,
    project_id: str,
    current_user: UserModel,
    task_data: dict,
) -> Task:
    project = get_project_by_id(db, project_id)
    check_member(db, project, current_user)

    # Nếu có assignee_id, kiểm tra người được gán có phải member/owner của project không
    assignee_id = task_data.get("assignee_id")
    if assignee_id != current_user.id:
        # Bước 1: user đó có tồn tại trong hệ thống không
        assignee = db.query(UserModel).filter(UserModel.id == assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Không tìm thấy assignee")

        # Bước 2: user đó có phải member/owner của ĐÚNG project này không
        if not is_project_member(db, project, assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể giao task cho thành viên của project này",
            )


    new_task = Task(
        project_id=project_id,       # ← lấy từ path, KHÔNG dùng task_data["project_id"]
        title=task_data["title"],
        description=task_data.get("description"),
        due_date=task_data.get("due_date"),
        priority=task_data.get("priority", "MEDIUM"),
        status=task_data.get("status", "TODO"),
        assignee_id=assignee_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_project_tasks(
    db: Session,
    project_id: str,
    current_user: UserModel,
    status_filter: str | None = None,
    priority: str | None = None,
    assignee_id: str | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[Task]:
    # Kiểm tra project tồn tại + user thuộc project (dùng helper đã có)
    project = get_project_by_id(db, project_id)
    check_member(db, project, current_user)

    query = db.query(Task).filter(Task.project_id == project_id)

    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    # sort
    if sort_by == "created_at":
        sort_column = Task.created_at
    elif sort_by == "due_date":
        sort_column = Task.due_date
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by chỉ được là created_at hoặc due_date",
        )

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    return query.offset(offset).limit(limit).all()


def get_task_by_id(db: Session, task_id: str) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy task")
    return task


def get_task_detail(db: Session, task_id: str, current_user: UserModel) -> Task:
    task = get_task_by_id(db, task_id)
    project = get_project_by_id(db, task.project_id)
    check_member(db, project, current_user)
    return task

def update_task(
    db: Session,
    task_id: str,
    current_user: UserModel,
    update_data: dict,
) -> Task:
    task = get_task_by_id(db, task_id)
    project = get_project_by_id(db, task.project_id)
    check_member(db, project, current_user)

    # Nếu có đổi assignee_id, kiểm tra người mới có thuộc project không
    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        new_assignee_id = update_data["assignee_id"]
        assignee = db.query(UserModel).filter(UserModel.id == new_assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy assignee")
        if not is_project_member(db, project, new_assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chỉ có thể giao task cho thành viên của project này",
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task



def delete_task(db:Session, task_id:str,current_user: UserModel):
    task = get_task_by_id(db, task_id)
    project = get_project_by_id(db, task.project_id)
    check_owner(project, current_user)
    db.delete(task)
    db.commit()