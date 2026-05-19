from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from ..schemas import Task, TaskCreate, TaskStatusUpdate
from ..storage import TaskStorage
from ..dependencies import get_current_user, get_storage_dep

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
        task_data: TaskCreate,
        current_user=Depends(get_current_user),
        storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.create(task_data.model_dump(), current_user.id)
    return task


@router.get("/", response_model=List[Task])
def get_tasks(
        status_filter: Optional[str] = None,
        min_priority: Optional[int] = None,
        current_user=Depends(get_current_user),
        storage: TaskStorage = Depends(get_storage_dep)
):
    tasks = storage.get_user_tasks(current_user.id, status_filter, min_priority)
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(
        task_id: int,
        current_user=Depends(get_current_user),
        storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)

    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
        task_id: int,
        status_update: TaskStatusUpdate,
        current_user=Depends(get_current_user),
        storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)

    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    updated_task = storage.update_task_status(task_id, status_update.status.value)
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
        task_id: int,
        current_user=Depends(get_current_user),
        storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)

    if task is None or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    storage.delete_task(task_id)
    return None