"""로컬 JSON 저장소. 표준 라이브러리만 사용한다.

- 파일이 없으면 빈 저장소로 시작한다 (오류가 아니다).
- 파일이 손상됐으면 조용히 덮어쓰지 않고 ValueError를 낸다.
- 저장은 임시 파일 + os.replace로 원자적으로 수행한다.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def empty_store() -> dict:
    return {"tools": [], "mappings": [], "tasks": []}


def load_store(path: str | Path) -> dict:
    """JSON 파일을 읽어 저장소 dict를 돌려준다.

    파일이 없으면 빈 저장소를 돌려준다. JSON 파싱에 실패하거나
    최상위 구조가 dict가 아니면 ValueError를 낸다.
    """
    p = Path(path)
    if not p.exists():
        return empty_store()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"데이터 파일이 손상되었습니다: {p} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"데이터 파일 형식이 올바르지 않습니다: {p} (최상위가 객체가 아님)")
    store = empty_store()
    for key in store:
        value = data.get(key, [])
        if not isinstance(value, list):
            raise ValueError(f"데이터 파일 형식이 올바르지 않습니다: {p} ('{key}'가 목록이 아님)")
        store[key] = value
    return store


def save_store(path: str | Path, store: dict) -> None:
    """저장소를 원자적으로 저장한다. 부모 디렉터리는 필요 시 만든다."""
    p = Path(path)
    if p.parent and str(p.parent) not in ("", "."):
        p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(f".{p.name}.tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)
