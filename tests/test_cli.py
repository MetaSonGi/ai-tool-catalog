"""CLI 통합 테스트. 외부 의존성 없이 임시 데이터 파일만 쓴다."""

import tempfile
import unittest
from pathlib import Path

from toolkit_hub.cli import main


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = str(Path(self.tmp.name) / "hub.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_seed_and_catalog_flow(self):
        self.assertEqual(main(["--data", self.data, "seed"]), 0)
        self.assertEqual(main(["--data", self.data, "catalog", "list"]), 0)
        # 이미 데이터가 있으면 seed 거부
        self.assertEqual(main(["--data", self.data, "seed"]), 2)

    def test_board_flow_and_invalid_status(self):
        self.assertEqual(main(["--data", self.data, "board", "add", "--title", "할 일 1"]), 0)
        self.assertEqual(
            main(["--data", self.data, "board", "move", "--id", "t001", "--status", "완료"]), 0
        )
        self.assertEqual(
            main(["--data", self.data, "board", "move", "--id", "t001", "--status", "엉뚱"]), 2
        )
        self.assertEqual(
            main(["--data", self.data, "board", "move", "--id", "t999", "--status", "완료"]), 2
        )

    def test_map_requires_known_tool(self):
        self.assertEqual(
            main(["--data", self.data, "map", "add", "--project", "P", "--feature", "F", "--tool", "없음"]),
            2,
        )
        self.assertEqual(
            main(
                [
                    "--data",
                    self.data,
                    "catalog",
                    "add",
                    "--id",
                    "x",
                    "--name",
                    "도구X",
                    "--category",
                    "개발",
                ]
            ),
            0,
        )
        self.assertEqual(
            main(["--data", self.data, "map", "add", "--project", "P", "--feature", "F", "--tool", "x"]),
            0,
        )
        # 매핑에서 쓰는 도구는 삭제 거부
        self.assertEqual(main(["--data", self.data, "catalog", "remove", "--id", "x"]), 2)


if __name__ == "__main__":
    unittest.main()
