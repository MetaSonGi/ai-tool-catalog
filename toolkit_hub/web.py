"""로컬 웹 UI (표준 라이브러리만 사용).

이 서버는 GitHub Pages용이 아니다. Pages는 정적 사이트라 Python 서버가
돌아가지 않는다. 이 서버는 127.0.0.1 전용으로, 같은 PC의 브라우저에서만
열 수 있는 로컬 UI다. 외부 전송은 없다.

기존 CLI 로직(catalog.py, board.py, mapping.py, store.py)을 그대로
재사용한다. 웹용으로 검증·검색·저장 로직을 중복 구현하지 않는다.

실행:
    python3 -m toolkit_hub.web --data data/hub.json --port 8767
    # 브라우저에서 http://127.0.0.1:8767 접속
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import __version__, board, catalog, mapping, store

PAGE = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>도구 허브 (로컬)</title>
<style>
body{font-family:system-ui,sans-serif;max-width:900px;margin:20px auto;padding:0 16px}
section{border:1px solid #ccc;border-radius:12px;padding:16px;margin:16px 0}
input,select,button{padding:8px;margin:4px 2px}
table{border-collapse:collapse;width:100%} td,th{border:1px solid #ddd;padding:6px;text-align:left}
.note{color:#555;font-size:14px}
</style></head><body>
<h1>도구 허브 (로컬 전용)</h1>
<p class="note">이 페이지는 127.0.0.1 로컬 서버에서만 열린다. 데이터는 로컬 JSON 파일에만 저장되고, 외부로 전송되지 않는다.</p>

<section><h2>카탈로그</h2>
<input id="kw" placeholder="키워드 검색"> <input id="cat" placeholder="카테고리">
<button onclick="loadCatalog()">검색</button>
<table><thead><tr><th>id</th><th>이름</th><th>카테고리</th><th>태그</th><th></th></tr></thead>
<tbody id="catalog"></tbody></table>
<h3>도구 추가</h3>
<input id="t-id" placeholder="id (공백 불가)"> <input id="t-name" placeholder="이름">
<input id="t-cat" placeholder="카테고리"> <input id="t-tags" placeholder="태그, 쉼표 구분">
<input id="t-url" placeholder="URL (http:// 또는 https://, 비워도 됨)" size="40">
<button onclick="addTool()">추가</button>
<p id="catalog-msg"></p></section>

<section><h2>개발 보드</h2>
<table><thead><tr><th>id</th><th>제목</th><th>상태</th><th>이동</th></tr></thead>
<tbody id="tasks"></tbody></table>
<input id="task-title" placeholder="새 작업 제목"> <button onclick="addTask()">작업 추가</button>
<p id="board-msg"></p></section>

<section><h2>프로젝트 기능 매핑</h2>
<table><thead><tr><th>프로젝트</th><th>기능</th><th>도구 id</th></tr></thead>
<tbody id="maps"></tbody></table>
<input id="m-project" placeholder="프로젝트"> <input id="m-feature" placeholder="기능">
<input id="m-tool" placeholder="도구 id"> <button onclick="addMap()">매핑 추가</button>
<p id="map-msg"></p></section>

<script>
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function api(path, method, body){
  const r = await fetch(path, {method, headers:{'Content-Type':'application/json'},
    body: body ? JSON.stringify(body) : undefined});
  const data = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(data.error || ('HTTP ' + r.status));
  return data;
}
async function loadCatalog(){
  const kw = document.getElementById('kw').value, cat = document.getElementById('cat').value;
  const tools = await api('/api/catalog?keyword=' + encodeURIComponent(kw) + '&category=' + encodeURIComponent(cat));
  document.getElementById('catalog').innerHTML = tools.map(t =>
    `<tr><td>${esc(t.id)}</td><td>${esc(t.name)}</td><td>${esc(t.category)}</td><td>${esc(t.tags.join(', '))}</td>` +
    `<td><button onclick="removeTool('${esc(t.id)}')">삭제</button></td></tr>`).join('');
}
async function addTool(){
  try{
    await api('/api/catalog', 'POST', {id: document.getElementById('t-id').value,
      name: document.getElementById('t-name').value, category: document.getElementById('t-cat').value,
      tags: document.getElementById('t-tags').value.split(',').map(s=>s.trim()).filter(Boolean),
      url: document.getElementById('t-url').value, description: ''});
    document.getElementById('catalog-msg').textContent = '추가했습니다.'; loadCatalog();
  }catch(e){ document.getElementById('catalog-msg').textContent = '오류: ' + e.message; }
}
async function removeTool(id){
  try{ await api('/api/catalog?id=' + encodeURIComponent(id), 'DELETE'); loadCatalog(); }
  catch(e){ alert('오류: ' + e.message); }
}
async function loadBoard(){
  const tasks = await api('/api/board');
  document.getElementById('tasks').innerHTML = tasks.map(t =>
    `<tr><td>${esc(t.id)}</td><td>${esc(t.title)}</td><td>${esc(t.status)}</td><td>` +
    ['할 일','진행 중','완료'].map(s => `<button onclick="moveTask('${esc(t.id)}','${s}')">${s}</button>`).join(' ') + `</td></tr>`).join('');
}
async function addTask(){
  try{ await api('/api/board', 'POST', {title: document.getElementById('task-title').value}); loadBoard(); }
  catch(e){ document.getElementById('board-msg').textContent = '오류: ' + e.message; }
}
async function moveTask(id, status){
  try{ await api('/api/board/move', 'POST', {id, status}); loadBoard(); }
  catch(e){ alert('오류: ' + e.message); }
}
async function loadMap(){
  const maps = await api('/api/map');
  document.getElementById('maps').innerHTML = maps.map(m =>
    `<tr><td>${esc(m.project)}</td><td>${esc(m.feature)}</td><td>${esc(m.tool_id)}</td></tr>`).join('');
}
async function addMap(){
  try{ await api('/api/map', 'POST', {project: document.getElementById('m-project').value,
    feature: document.getElementById('m-feature').value, tool: document.getElementById('m-tool').value});
    loadMap(); }catch(e){ document.getElementById('map-msg').textContent = '오류: ' + e.message; }
}
loadCatalog(); loadBoard(); loadMap();
</script></body></html>
"""


def _load(handler):
    return store.load_store(handler.server.data_path)


def _save(handler, data):
    store.save_store(handler.server.data_path, data)


class HubHandler(BaseHTTPRequestHandler):
    server_version = "ToolkitHub/1.0"

    def log_message(self, *args):  # 테스트 출력을 조용히 유지
        pass

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self):
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > 1_000_000:
            raise ValueError("요청 본문이 너무 큽니다 (1MB 제한).")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError(f"JSON 형식이 올바르지 않습니다: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("요청 본문은 JSON 객체여야 합니다.")
        return data

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler naming
        parsed = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        try:
            if parsed.path == "/":
                self._send_html()
            elif parsed.path == "/api/status":
                data = _load(self)
                self._send_json(
                    {"version": __version__, "tools": len(data["tools"]),
                     "tasks": len(data["tasks"]), "mappings": len(data["mappings"])}
                )
            elif parsed.path == "/api/catalog":
                data = _load(self)
                self._send_json(catalog.search_tools(
                    data["tools"], query.get("keyword", ""), query.get("category", "")))
            elif parsed.path == "/api/board":
                data = _load(self)
                self._send_json(board.list_tasks(data["tasks"], query.get("status", "")))
            elif parsed.path == "/api/map":
                data = _load(self)
                if query.get("project"):
                    self._send_json(mapping.mappings_for_project(data["mappings"], query["project"]))
                else:
                    self._send_json(data["mappings"])
            else:
                self._send_json({"error": "없는 경로입니다."}, 404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        try:
            body = self._read_json()
            data = _load(self)
            if parsed.path == "/api/catalog":
                tool = catalog.add_tool(data["tools"], body)
                _save(self, data)
                self._send_json(tool, 201)
            elif parsed.path == "/api/board":
                task = board.add_task(data["tasks"], body.get("title", ""), body.get("status", "할 일"))
                _save(self, data)
                self._send_json(task, 201)
            elif parsed.path == "/api/board/move":
                task = board.move_task(data["tasks"], body.get("id", ""), body.get("status", ""))
                _save(self, data)
                self._send_json(task)
            elif parsed.path == "/api/map":
                item = mapping.add_mapping(
                    data["mappings"], data["tools"],
                    body.get("project", ""), body.get("feature", ""), body.get("tool", ""))
                _save(self, data)
                self._send_json(item, 201)
            else:
                self._send_json({"error": "없는 경로입니다."}, 404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)

    def do_DELETE(self):  # noqa: N802
        parsed = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        try:
            if parsed.path == "/api/catalog":
                tool_id = query.get("id", "")
                data = _load(self)
                if any(m.get("tool_id") == tool_id for m in data["mappings"]):
                    self._send_json({"error": f"매핑에서 사용 중인 도구라 삭제할 수 없습니다: {tool_id}"}, 400)
                    return
                if not catalog.remove_tool(data["tools"], tool_id):
                    self._send_json({"error": f"없는 도구 id입니다: {tool_id}"}, 404)
                    return
                _save(self, data)
                self._send_json({"deleted": tool_id})
            else:
                self._send_json({"error": "없는 경로입니다."}, 404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)


def create_server(data_path="data/hub.json", host="127.0.0.1", port=0):
    """127.0.0.1 전용 서버를 만든다. port=0이면 OS가 빈 포트를 고른다."""
    server = ThreadingHTTPServer((host, port), HubHandler)
    server.daemon_threads = True
    server.data_path = str(data_path)
    return server


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="도구 허브 로컬 웹 UI (127.0.0.1 전용)")
    parser.add_argument("--data", default="data/hub.json", help="데이터 JSON 경로")
    parser.add_argument("--host", default="127.0.0.1", help="바인드 주소 (기본값: 127.0.0.1, 바꾸지 마세요)")
    parser.add_argument("--port", type=int, default=8767, help="포트 (기본값: 8767)")
    args = parser.parse_args(argv)
    if args.host != "127.0.0.1":
        parser.error("이 서버는 127.0.0.1 전용입니다. 외부 노출용으로 바꾸지 마세요.")
    server = create_server(args.data, args.host, args.port)
    print(f"도구 허브 로컬 웹 UI: http://127.0.0.1:{server.server_address[1]}")
    print(f"데이터: {Path(args.data).resolve()} (Ctrl+C로 종료)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
