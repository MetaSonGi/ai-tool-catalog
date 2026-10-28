import json
import tempfile
import unittest
from pathlib import Path

from toolkit_hub.store import empty_store, load_store, save_store


class TestStore(unittest.TestCase):
    def test_missing_file_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(load_store(Path(tmp) / "nope.json"), empty_store())

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sub" / "hub.json"
            data = empty_store()
            data["tools"].append({"id": "a", "name": "도구A", "category": "개발"})
            save_store(path, data)
            self.assertEqual(load_store(path), data)

    def test_corrupt_file_raises_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hub.json"
            path.write_text("{ broken json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_store(path)
            # 손상 파일이 그대로 남아 있다 (조용히 덮지 않음)
            self.assertEqual(path.read_text(encoding="utf-8"), "{ broken json")

    def test_wrong_top_level_type_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "hub.json"
            path.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_store(path)


if __name__ == "__main__":
    unittest.main()
