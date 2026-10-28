"""프로젝트 기능 매핑: 프로젝트의 기능이 어떤 도구를 쓰는지 연결한다."""

from __future__ import annotations


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}'는 비어 있을 수 없습니다.")
    return value.strip()


def add_mapping(mappings: list, tools: list, project: str, feature: str, tool_id: str) -> dict:
    """매핑을 추가한다.

    - 프로젝트명·기능명·도구 id가 비면 ValueError
    - 카탈로그에 없는 도구 id면 ValueError (고아 매핑 방지)
    - 같은 (프로젝트, 기능, 도구) 중복이면 ValueError
    """
    project = _require_text(project, "project")
    feature = _require_text(feature, "feature")
    tool_id = _require_text(tool_id, "tool_id")
    if not any(t.get("id") == tool_id for t in tools):
        raise ValueError(f"카탈로그에 없는 도구 id입니다: {tool_id}")
    mapping = {"project": project, "feature": feature, "tool_id": tool_id}
    if mapping in mappings:
        raise ValueError(f"이미 존재하는 매핑입니다: {project} / {feature} / {tool_id}")
    mappings.append(mapping)
    return mapping


def mappings_for_project(mappings: list, project: str) -> list:
    project = _require_text(project, "project")
    return [m for m in mappings if m.get("project") == project]


def tool_ids_for_project(mappings: list, project: str) -> list:
    """프로젝트가 쓰는 도구 id 목록(중복 제거, 등장 순서 유지)."""
    seen: list = []
    for mapping in mappings_for_project(mappings, project):
        tool_id = mapping.get("tool_id")
        if tool_id not in seen:
            seen.append(tool_id)
    return seen
