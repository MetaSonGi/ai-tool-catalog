"""로컬 웹 UI 테스트. 실제 서버를 임시 포트(127.0.0.1)로 띄우고
urllib로 호출한다. 테스트 후 서버를 반드시 종료한다. 외부 전송 없음."""

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from toolkit_hub.web import create_server


def _call(base, path, method="GET", body=None):
    req = urllib.request.Request(
        base + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


class WebTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = str(Path(self.tmp.name) / "hub.json")
        self.server = create_server(self.data, "127.0.0.1", 0)
        self.port = self.server.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.tmp.cleanup()

    def test_index_and_status(self):
        with urllib.request.urlopen(self.base + "/", timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("도구 허브", resp.read().decode())
        status, body = _call(self.base, "/api/status")
        self.assertEqual(status, 200)
        self.assertEqual(body["tools"], 0)

    def test_catalog_board_map_flow_reuses_cli_logic(self):
        status, tool = _call(self.base, "/api/catalog", "POST", {
            "id": "web-tool", "name": "웹 도구", "category": "개발", "tags": ["웹"]})
        self.assertEqual(status, 201)
        status, tools = _call(self.base, "/api/catalog?keyword=" + urllib.parse.quote("웹"))
        self.assertEqual([t["id"] for t in tools], ["web-tool"])
        # 중복 id는 CLI와 같은 검증으로 거부된다.
        status, body = _call(self.base, "/api/catalog", "POST", {
            "id": "web-tool", "name": "중복", "category": "개발"})
        self.assertEqual(status, 400)
        status, task = _call(self.base, "/api/board", "POST", {"title": "웹 작업"})
        self.assertEqual(status, 201)
        status, moved = _call(self.base, "/api/board/move", "POST",
                              {"id": task["id"], "status": "진행 중"})
        self.assertEqual(moved["status"], "진행 중")
        status, item = _call(self.base, "/api/map", "POST", {
            "project": "웹 프로젝트", "feature": "검색", "tool": "web-tool"})
        self.assertEqual(status, 201)
        # 매핑에서 쓰는 도구는 삭제가 거부된다 (CLI와 동일).
        status, body = _call(self.base, "/api/catalog?id=web-tool", "DELETE")
        self.assertEqual(status, 400)
        status, tools = _call(self.base, "/api/catalog")
        self.assertEqual(len(tools), 1)

    def test_server_binds_localhost_only(self):
        host, _port = self.server.server_address
        self.assertEqual(host, "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
