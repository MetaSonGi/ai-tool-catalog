# ai-tool-catalog

Local-first AI tool catalog, project feature mapping and persistent development board. Python standard library, Korean UI.

> 원본 저장소 설명 문장 그대로 유지. 원본 저장소(2026-10-25 생성, 커밋 1개)에는
> 이 문장 2줄짜리 README.md 1개 파일만 있었고, 코드·테스트·CLI가 전혀 없었다.
> 이 작업본은 그 설명을 실제로 동작하는 최소 구현으로 채운 로컬 작업본이다.
> GitHub에는 푸시하지 않았다. 푸시 여부는 사용자가 나중에 결정한다.

## 무엇을 하는지

로컬 컴퓨터에서만 동작하는 작은 도구 허브다. 외부 서버·외부 모델·외부 API 호출이 없다.

1. **AI 도구 카탈로그** — 도구를 id·이름·카테고리·설명·URL·태그로 등록하고,
   키워드/카테고리로 검색한다.
2. **프로젝트 기능 매핑** — "어떤 프로젝트의 어떤 기능이 어떤 도구를 쓰는가"를 연결한다.
   카탈로그에 없는 도구로는 매핑을 만들 수 없어 고아 매핑이 생기지 않는다.
3. **지속 개발 보드** — 작업을 `할 일 / 진행 중 / 완료` 상태로 관리한다.
   데이터는 로컬 JSON 파일에 남아 다음 실행 때도 이어진다.

## 무엇이 필요한지

- Python 3.10 이상 (표준 라이브러리만 사용, 별도 설치 패키지 없음)
- 인터넷·API 키·계정 불필요
- 테스트: Python 표준 `unittest`만 사용

## 어떻게 실행하는지

```bash
# 저장소 작업본 디렉터리에서
python3 main.py --help
python3 main.py seed                 # 합성 예시 데이터 채우기 (빈 저장소에서만)
python3 main.py catalog list
python3 main.py catalog list --keyword 코드 --category 개발
python3 main.py catalog add --id my-tool --name "내 도구" --category 개발 --description "설명" --tags 코드,편집
python3 main.py board add --title "카탈로그에 실제 도구 채우기"
python3 main.py board list
python3 main.py board move --id t001 --status "진행 중"
python3 main.py map add --project "예시 프로젝트" --feature "이미지 생성" --tool example-image
python3 main.py map list --project "예시 프로젝트"
```

데이터 위치는 기본값 `./data/hub.json`이다. 다른 경로를 쓰려면:

```bash
python3 main.py --data /tmp/hub-test.json seed
python3 main.py --data /tmp/hub-test.json catalog list
```

`python3 -m toolkit_hub --help` 로도 실행할 수 있다.

## 로컬 웹 UI (127.0.0.1 전용, Python 표준 라이브러리만)

```bash
python3 -m toolkit_hub.web --data data/hub.json --port 8767
# 브라우저에서 http://127.0.0.1:8767 접속
```

- 기능: 카탈로그 목록·검색·추가·삭제, 보드 목록·추가·상태 이동,
  매핑 목록·추가. 검증·검색·저장 로직은 기존 CLI 모듈
  (`catalog.py`·`board.py`·`mapping.py`·`store.py`)을 그대로 재사용하고,
  웹용으로 중복 구현하지 않았다.
- 이 서버는 127.0.0.1 전용이다. 외부 노출용으로 바인드 주소를 바꾸지 마세요.
- **이 웹 UI는 GitHub Pages용이 아니다.** Pages는 정적 사이트라 Python
  서버가 돌아가지 않는다. 로컬에서만 쓰는 UI다.
- 웹 UI 추가분은 로컬 작업본에만 있으며, GitHub에는 푸시하지 않았다.

## 데이터 형식

`data/hub.json` (또는 `--data` 경로)은 다음 3개 목록을 가진 JSON이다.
`examples/sample_data.json`에 같은 형식의 합성 예시가 있다.

```json
{
  "tools": [{"id": "example-image", "name": "예시 이미지 생성기", "category": "콘텐츠",
             "description": "...", "url": "", "tags": ["예시"]}],
  "mappings": [{"project": "예시 프로젝트", "feature": "이미지 생성", "tool_id": "example-image"}],
  "tasks": [{"id": "t001", "title": "예시 작업", "status": "할 일"}]
}
```

## 오류 처리·입력 검증 (최소 보강)

- 빈 이름/카테고리/프로젝트/기능, 공백 포함 도구 id, `http(s)://`가 아닌 URL은 거부된다.
- 도구 id 중복, 매핑 중복, 보드 상태(`할 일/진행 중/완료` 외)은 거부된다.
- 없는 작업 id 이동, 없는 도구로의 매핑, 매핑에서 사용 중인 도구 삭제는 거부된다.
- 검증 실패 시 저장하지 않고 종료 코드 2와 한국어 오류 메시지를 낸다.
- 데이터 파일이 없으면 빈 저장소로 시작하고, 손상된 JSON은 조용히 덮지 않고 오류를 낸다.
- 저장은 임시 파일 + 교체 방식으로 원자적으로 수행한다.

## 테스트

```bash
python3 -m unittest discover -s tests -v
```

외부 모델이 필요한 부분은 없다. 모든 테스트는 합성 데이터와 임시 디렉터리만 쓰며,
실제 모델·네트워크 검증은 이 프로젝트에 존재하지 않으므로 '미검증'으로 남긴다
(검증 대상 자체가 없음 — 과장하지 않는다).

## 파일 구성

| 경로 | 역할 |
|---|---|
| `main.py` | CLI 진입점 |
| `toolkit_hub/__init__.py` | 버전 정보 |
| `toolkit_hub/cli.py` | argparse CLI (한국어 도움말·오류) |
| `toolkit_hub/web.py` | 로컬 웹 UI (127.0.0.1 전용, 표준 라이브러리만) |
| `toolkit_hub/catalog.py` | 도구 카탈로그 검증·검색 |
| `toolkit_hub/mapping.py` | 프로젝트 기능 매핑 검증 |
| `toolkit_hub/board.py` | 개발 보드 상태 관리 |
| `toolkit_hub/store.py` | 로컬 JSON 저장·불러오기 |
| `tests/test_*.py` | 단위·CLI 통합·웹 테스트 |
| `examples/sample_data.json` | 합성 예시 데이터 |

## 남은 한계

- 로컬 웹 UI가 추가됐으나, GitHub Pages용 정적 사이트는 아니다.
  Python 서버를 로컬에서 실행해야만 웹 UI가 열린다.
- 웹 UI는 한 명이 로컬에서 쓰는 용도다. 다중 사용자·동시 쓰기 잠금이 없다.
- 실제 AI 도구 연동·모델 호출이 없다. 카탈로그는 사람이 채우는 목록이다.
- 다중 사용자·동시 쓰기 잠금이 없다. 한 번에 한 명이 로컬에서 쓰는 용도다.
- 원본 저장소에 있던 것은 README 1개뿐이므로, 이 구현은 기존 코드 구조 변경이 아니라
  신규 최소 구현이다. 실제 도구 목록은 사용자가 직접 채워야 한다.
