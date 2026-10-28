import unittest

from toolkit_hub.board import add_task, list_tasks, move_task, next_task_id


class TestBoard(unittest.TestCase):
    def test_add_and_move(self):
        tasks = []
        task = add_task(tasks, "첫 작업")
        self.assertEqual(task["id"], "t001")
        self.assertEqual(task["status"], "할 일")
        moved = move_task(tasks, "t001", "진행 중")
        self.assertEqual(moved["status"], "진행 중")
        self.assertEqual(next_task_id(tasks), "t002")

    def test_invalid_status_rejected(self):
        tasks = []
        with self.assertRaises(ValueError):
            add_task(tasks, "작업", "이상한 상태")
        add_task(tasks, "작업")
        with self.assertRaises(ValueError):
            move_task(tasks, "t001", "이상한 상태")
        with self.assertRaises(ValueError):
            list_tasks(tasks, "이상한 상태")

    def test_move_unknown_id_rejected(self):
        with self.assertRaises(ValueError):
            move_task([], "t999", "완료")

    def test_list_filter(self):
        tasks = []
        add_task(tasks, "A")
        add_task(tasks, "B", "완료")
        self.assertEqual(len(list_tasks(tasks)), 2)
        self.assertEqual(len(list_tasks(tasks, "완료")), 1)


if __name__ == "__main__":
    unittest.main()
