import unittest

from toolkit_hub.catalog import add_tool
from toolkit_hub.mapping import add_mapping, mappings_for_project, tool_ids_for_project


class TestMapping(unittest.TestCase):
    def setUp(self):
        self.tools = []
        add_tool(self.tools, {"id": "a", "name": "도구A", "category": "개발"})
        add_tool(self.tools, {"id": "b", "name": "도구B", "category": "콘텐츠"})

    def test_add_and_query(self):
        mappings = []
        add_mapping(mappings, self.tools, "P1", "편집", "a")
        add_mapping(mappings, self.tools, "P1", "생성", "b")
        add_mapping(mappings, self.tools, "P1", "편집2", "a")
        self.assertEqual(len(mappings_for_project(mappings, "P1")), 3)
        self.assertEqual(tool_ids_for_project(mappings, "P1"), ["a", "b"])
        self.assertEqual(mappings_for_project(mappings, "없는 프로젝트"), [])

    def test_unknown_tool_rejected(self):
        with self.assertRaises(ValueError):
            add_mapping([], self.tools, "P1", "편집", "없음")

    def test_duplicate_rejected(self):
        mappings = []
        add_mapping(mappings, self.tools, "P1", "편집", "a")
        with self.assertRaises(ValueError):
            add_mapping(mappings, self.tools, "P1", "편집", "a")

    def test_empty_fields_rejected(self):
        with self.assertRaises(ValueError):
            add_mapping([], self.tools, "  ", "편집", "a")


if __name__ == "__main__":
    unittest.main()
