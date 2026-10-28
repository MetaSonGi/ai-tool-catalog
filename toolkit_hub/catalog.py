"""AI 도구 카탈로그: 추가·검색·삭제. 외부 의존성 없음."""

from __future__ import annotations


def _require_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}'는 비어 있을 수 없습니다.")
    return value.strip()


def validate_tool(tool: dict) -> dict:
    """도구 dict를 검증하고 정규화한 복사본을 돌려준다."""
    tool_id = _require_text(tool.get("id"), "id")
    if any(ch.isspace() for ch in tool_id):
        raise ValueError("'id'에는 공백을 쓸 수 없습니다.")
    name = _require_text(tool.get("name"), "name")
    category = _require_text(tool.get("category"), "category")
    description = tool.get("description", "")
    if description is None:
        description = ""
    if not isinstance(description, str):
        raise ValueError("'description'은 문자열이어야 합니다.")
    url = tool.get("url", "")
    if url is None:
        url = ""
    if not isinstance(url, str):
        raise ValueError("'url'은 문자열이어야 합니다.")
    url = url.strip()
    if url and not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("'url'은 http:// 또는 https:// 로 시작해야 합니다.")
    tags = tool.get("tags", [])
    if tags is None:
        tags = []
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise ValueError("'tags'는 문자열 목록이어야 합니다.")
    return {
        "id": tool_id,
        "name": name,
        "category": category,
        "description": description.strip(),
        "url": url,
        "tags": [t.strip() for t in tags if t.strip()],
    }


def add_tool(tools: list, tool: dict) -> dict:
    """중복 id가 없으면 도구를 추가한다. 중복이면 ValueError."""
    normalized = validate_tool(tool)
    if any(t.get("id") == normalized["id"] for t in tools):
        raise ValueError(f"이미 존재하는 도구 id입니다: {normalized['id']}")
    tools.append(normalized)
    return normalized


def remove_tool(tools: list, tool_id: str) -> bool:
    """도구를 삭제한다. 없으면 False를 돌려준다."""
    tool_id = _require_text(tool_id, "id")
    for i, tool in enumerate(tools):
        if tool.get("id") == tool_id:
            del tools[i]
            return True
    return False


def search_tools(tools: list, keyword: str = "", category: str = "") -> list:
    """키워드(부분 일치, 대소문자 무시)와 카테고리로 필터링한다."""
    kw = (keyword or "").strip().lower()
    cat = (category or "").strip()
    result = []
    for tool in tools:
        if cat and tool.get("category") != cat:
            continue
        if kw:
            haystack = " ".join(
                [
                    str(tool.get("name", "")),
                    str(tool.get("category", "")),
                    str(tool.get("description", "")),
                    " ".join(tool.get("tags", [])),
                ]
            ).lower()
            if kw not in haystack:
                continue
        result.append(tool)
    return result
