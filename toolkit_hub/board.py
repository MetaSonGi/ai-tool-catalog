"""지속 개발 보드: 할 일 / 진행 중 / 완료 상태의 작업 목록."""

from __future__ import annotations

STATUSES = ("할 일", "진행 중", "완료")


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}'는 비어 있을 수 없습니다.")
    return value.strip()


def next_task_id(tasks: list) -> str:
    """t001, t002 ... 형식의 다음 작업 id를 만든다."""
    numbers = []
    for task in tasks:
        task_id = str(task.get("id", ""))
        if task_id.startswith("t") and task_id[1:].isdigit():
            numbers.append(int(task_id[1:]))
    return f"t{max(numbers, default=0) + 1:03d}"


def add_task(tasks: list, title: str, status: str = "할 일") -> dict:
    """작업을 추가한다. 상태가 유효하지 않으면 ValueError."""
    title = _require_text(title, "title")
    if status not in STATUSES:
        raise ValueError(f"유효하지 않은 상태입니다: {status} (가능: {', '.join(STATUSES)})")
    task = {"id": next_task_id(tasks), "title": title, "status": status}
    tasks.append(task)
    return task


def move_task(tasks: list, task_id: str, status: str) -> dict:
    """작업 상태를 바꾼다. 없는 id나 유효하지 않은 상태면 ValueError."""
    task_id = _require_text(task_id, "id")
    if status not in STATUSES:
        raise ValueError(f"유효하지 않은 상태입니다: {status} (가능: {', '.join(STATUSES)})")
    for task in tasks:
        if task.get("id") == task_id:
            task["status"] = status
            return task
    raise ValueError(f"없는 작업 id입니다: {task_id}")


def list_tasks(tasks: list, status: str = "") -> list:
    """상태 필터(없으면 전체)로 작업 목록을 돌려준다."""
    status = (status or "").strip()
    if status and status not in STATUSES:
        raise ValueError(f"유효하지 않은 상태입니다: {status} (가능: {', '.join(STATUSES)})")
    if not status:
        return list(tasks)
    return [t for t in tasks if t.get("status") == status]
