import unittest

from toolkit_hub.catalog import add_tool, remove_tool, search_tools


def tool(**over):
    base = {"id": "t1", "name": "테스트 도구", "category": "개발", "description": "코드 편집", "tags": ["코드"]}
    base.update(over)
    return base


class TestCatalog(unittest.TestCase):
    def test_add_and_search(self):
        tools = []
        add_tool(tools, tool())
        add_tool(tools, tool(id="t2", name="다른 도구", category="콘텐츠", description="이미지", tags=["그림"]))
        self.assertEqual(len(search_tools(tools, "코드")), 1)
        self.assertEqual(len(search_tools(tools, "", "콘텐츠")), 1)
        self.assertEqual(len(search_tools(tools)), 2)

    def test_duplicate_id_rejected(self):
        tools = []
        add_tool(tools, tool())
        with self.assertRaises(ValueError):
            add_tool(tools, tool(name="다른 이름"))

    def test_empty_name_and_bad_url_rejected(self):
        tools = []
        with self.assertRaises(ValueError):
            add_tool(tools, tool(name="  "))
        with self.assertRaises(ValueError):
            add_tool(tools, tool(id="t9", url="ftp://example.com"))
        with self.assertRaises(ValueError):
            add_tool(tools, tool(id="bad id"))

    def test_remove(self):
        tools = []
        add_tool(tools, tool())
        self.assertTrue(remove_tool(tools, "t1"))
        self.assertFalse(remove_tool(tools, "t1"))
        self.assertEqual(tools, [])


if __name__ == "__main__":
    unittest.main()
