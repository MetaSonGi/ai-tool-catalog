"""CLI 진입점: python main.py --help

실행 예시:
  python main.py seed
  python main.py catalog list
  python main.py board add --title "카탈로그 채우기"
  python main.py map add --project "예시 프로젝트" --feature "이미지 생성" --tool example-image
"""

from toolkit_hub.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
