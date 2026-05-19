from typing import Dict, List, Optional
from .schemas import Task, TaskStatus


class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, task_data: dict, owner_id: int) -> Task:
        task = Task(
            id=self._next_id,
            owner_id=owner_id,
            **task_data
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_user_tasks(
            self,
            owner_id: int,
            status: Optional[str] = None,
            min_priority: Optional[int] = None
    ) -> List[Task]:
        tasks = [t for t in self._tasks.values() if t.owner_id == owner_id]

        if status:
            tasks = [t for t in tasks if t.status.value == status]

        if min_priority is not None:
            tasks = [t for t in tasks if t.priority >= min_priority]

        return sorted(tasks, key=lambda x: x.id)

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_task_status(self, task_id: int, status: str) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task:
            updated_task = task.model_copy(update={"status": TaskStatus(status)})
            self._tasks[task_id] = updated_task
            return updated_task
        return None

    def delete_task(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def get_all_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def get_stats(self) -> dict:
        tasks = self.get_all_tasks()
        total_tasks = len(tasks)
        by_status = {
            "todo": 0,
            "in_progress": 0,
            "done": 0
        }
        for task in tasks:
            by_status[task.status.value] += 1
        return {
            "total_tasks": total_tasks,
            "by_status": by_status
        }

    def clear(self):
        self._tasks.clear()
        self._next_id = 1


_storage = TaskStorage()


def get_storage() -> TaskStorage:
    return _storage