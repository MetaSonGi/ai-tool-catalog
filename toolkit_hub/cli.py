"""CLI 진입점. 사용법: python main.py --help

데이터는 기본적으로 ./data/hub.json 에 저장된다.
--data 로 다른 경로를 지정할 수 있다. 외부 전송은 일절 없다.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, board, catalog, mapping, store

SAMPLE_TOOLS = [
    {
        "id": "example-editor",
        "name": "예시 코드 편집기",
        "category": "개발",
        "description": "합성 예시 데이터입니다. 실제 도구로 교체해서 쓰세요.",
        "url": "",
        "tags": ["예시"],
    },
    {
        "id": "example-image",
        "name": "예시 이미지 생성기",
        "category": "콘텐츠",
        "description": "합성 예시 데이터입니다. 실제 도구로 교체해서 쓰세요.",
        "url": "",
        "tags": ["예시"],
    },
]


def _print_json(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyoki-toolkit-hub",
        description="로컬 우선 AI 도구 카탈로그 + 프로젝트 기능 매핑 + 지속 개발 보드",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--data", default="data/hub.json", help="데이터 JSON 경로 (기본값: data/hub.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("seed", help="합성 예시 데이터를 비어 있는 저장소에 채운다")
    p.add_argument("--force", action="store_true", help="이미 데이터가 있어도 예시로 덮어쓴다")

    p = sub.add_parser("catalog", help="도구 카탈로그")
    cat = p.add_subparsers(dest="catalog_cmd", required=True)
    p_list = cat.add_parser("list", help="도구 목록")
    p_list.add_argument("--keyword", default="")
    p_list.add_argument("--category", default="")
    p_add = cat.add_parser("add", help="도구 추가")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--description", default="")
    p_add.add_argument("--url", default="")
    p_add.add_argument("--tags", default="", help="쉼표로 구분 (예: 코드,편집)")
    p_rm = cat.add_parser("remove", help="도구 삭제")
    p_rm.add_argument("--id", required=True)

    p = sub.add_parser("board", help="지속 개발 보드")
    b = p.add_subparsers(dest="board_cmd", required=True)
    p_list = b.add_parser("list", help="작업 목록")
    p_list.add_argument("--status", default="", help="할 일 / 진행 중 / 완료 중 하나")
    p_add = b.add_parser("add", help="작업 추가")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--status", default="할 일")
    p_mv = b.add_parser("move", help="작업 상태 변경")
    p_mv.add_argument("--id", required=True)
    p_mv.add_argument("--status", required=True)

    p = sub.add_parser("map", help="프로젝트 기능 매핑")
    m = p.add_subparsers(dest="map_cmd", required=True)
    p_list = m.add_parser("list", help="매핑 목록")
    p_list.add_argument("--project", default="")
    p_add = m.add_parser("add", help="매핑 추가")
    p_add.add_argument("--project", required=True)
    p_add.add_argument("--feature", required=True)
    p_add.add_argument("--tool", required=True)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = store.load_store(args.data)
    except ValueError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 2

    try:
        if args.command == "seed":
            if not args.force and (data["tools"] or data["tasks"] or data["mappings"]):
                print("오류: 저장소가 비어 있지 않습니다. 덮어쓰려면 --force를 쓰세요.", file=sys.stderr)
                return 2
            data = store.empty_store()
            for tool in SAMPLE_TOOLS:
                catalog.add_tool(data["tools"], tool)
            board.add_task(data["tasks"], "예시: 카탈로그에 실제 도구 채우기")
            mapping.add_mapping(data["mappings"], data["tools"], "예시 프로젝트", "이미지 생성", "example-image")
            store.save_store(args.data, data)
            print(f"예시 데이터를 저장했습니다: {args.data}")
            return 0

        if args.command == "catalog":
            if args.catalog_cmd == "list":
                _print_json(catalog.search_tools(data["tools"], args.keyword, args.category))
            elif args.catalog_cmd == "add":
                tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
                tool = catalog.add_tool(
                    data["tools"],
                    {
                        "id": args.id,
                        "name": args.name,
                        "category": args.category,
                        "description": args.description,
                        "url": args.url,
                        "tags": tags,
                    },
                )
                store.save_store(args.data, data)
                _print_json(tool)
            elif args.catalog_cmd == "remove":
                if any(m.get("tool_id") == args.id for m in data["mappings"]):
                    print(f"오류: 매핑에서 사용 중인 도구라 삭제할 수 없습니다: {args.id}", file=sys.stderr)
                    return 2
                if not catalog.remove_tool(data["tools"], args.id):
                    print(f"오류: 없는 도구 id입니다: {args.id}", file=sys.stderr)
                    return 2
                store.save_store(args.data, data)
                print(f"삭제했습니다: {args.id}")
            return 0

        if args.command == "board":
            if args.board_cmd == "list":
                _print_json(board.list_tasks(data["tasks"], args.status))
            elif args.board_cmd == "add":
                task = board.add_task(data["tasks"], args.title, args.status)
                store.save_store(args.data, data)
                _print_json(task)
            elif args.board_cmd == "move":
                task = board.move_task(data["tasks"], args.id, args.status)
                store.save_store(args.data, data)
                _print_json(task)
            return 0

        if args.command == "map":
            if args.map_cmd == "list":
                if args.project:
                    _print_json(mapping.mappings_for_project(data["mappings"], args.project))
                else:
                    _print_json(data["mappings"])
            elif args.map_cmd == "add":
                item = mapping.add_mapping(
                    data["mappings"], data["tools"], args.project, args.feature, args.tool
                )
                store.save_store(args.data, data)
                _print_json(item)
            return 0
    except ValueError as exc:
        # 검증 실패는 저장하지 않고 종료 코드 2로 알린다.
        print(f"오류: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
