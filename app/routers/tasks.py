from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import UserModel
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.security import get_current_active_user
from app.services.task import create_task, get_project_tasks, get_task_detail, update_task, delete_task
from app.utils.exceptions import create_response

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Tasks"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    request: Request,
    project_id: str,
    payload: TaskCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Thành viên (owner hoặc member) tạo task trong project."""
    task_data = payload.model_dump()
    task_data.pop("project_id", None)   # bỏ project_id trong body, luôn dùng path param

    task = create_task(db, project_id=project_id, current_user=current_user, task_data=task_data)
    data = TaskResponse.model_validate(task)

    return create_response(
        status_code=status.HTTP_201_CREATED,
        message="Tạo task thành công",
        data=data,
        path=request.url.path,
    )

@router.get("")
def list_tasks_endpoint(
    request: Request,
    project_id: str,
    status_filter: str | None = None,
    priority: str | None = None,
    assignee_id: str | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Lấy danh sách task thuộc project, hỗ trợ lọc/tìm kiếm/sắp xếp/phân trang."""
    tasks = get_project_tasks(
        db,
        project_id=project_id,
        current_user=current_user,
        status_filter=status_filter,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = [TaskResponse.model_validate(t) for t in tasks]

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách task thành công",
        data=data,
        path=request.url.path,
    )

# Thêm 1 router mới trong CÙNG file app/routers/task.py
task_detail_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_detail_router.get("/{task_id}")
def get_task_endpoint(
    request: Request,
    task_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Lấy chi tiết 1 task. Chỉ member/owner của project chứa task đó mới xem được."""
    task = get_task_detail(db, task_id=task_id, current_user=current_user)
    data = TaskResponse.model_validate(task)

    return create_response(
        status_code=status.HTTP_200_OK,
        message="Lấy thông tin task thành công",
        data=data,
        path=request.url.path,
    )


@task_detail_router.patch("/{task_id}")
def update_task_endpoint(
    request: Request,
    task_id: str,
    payload: TaskUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)
    task = update_task(db, task_id=task_id, current_user=current_user, update_data=update_data)
    data = TaskResponse.model_validate(task)
    return create_response(status_code=status.HTTP_200_OK, message="Cập nhật task thành công", data=data, path=request.url.path)

@task_detail_router.get("/delete/{task_id}")
def delete_task_router(task_id: str,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)):
    delete_task(db, task_id, current_user)
    return create_response(
            status_code=status.HTTP_200_OK,
            message="Xoa task thành công"
        )