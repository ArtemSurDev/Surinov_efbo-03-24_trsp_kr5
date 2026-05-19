from fastapi import APIRouter, Depends, HTTPException, status
from ..storage import TaskStorage
from ..dependencies import require_admin, get_storage_dep
from ..schemas import TaskStats

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=TaskStats)
def get_stats(
        admin_user=Depends(require_admin),
        storage: TaskStorage = Depends(get_storage_dep)
):
    return storage.get_stats()


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_task(
        task_id: int,
        admin_user=Depends(require_admin),
        storage: TaskStorage = Depends(get_storage_dep)
):
    task = storage.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    storage.delete_task(task_id)
    return None