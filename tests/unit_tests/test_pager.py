import unittest

from taskmgr.lib.database.pager import Pager


class TestPager(unittest.TestCase):

    def setUp(self) -> None: pass

    def tearDown(self) -> None: pass

    def test_get_page_count(self):
        pager = Pager(6500, 100)
        pager.assemble_pages()
        self.assertTrue(pager.page_count == 65)

    def test_get_page(self):
        pager = Pager(58, 10)
        pager.assemble_pages()

        page = pager.get_page(1)
        self.assertEqual(page.offset, 1)
        self.assertEqual(page.row_limit, pager.row_limit)

        page = pager.get_page(2)
        self.assertEqual(page.offset, 11)
        self.assertEqual(page.row_limit, pager.row_limit)

        page = pager.get_page(3)
        self.assertEqual(page.offset, 21)
        self.assertEqual(page.row_limit, pager.row_limit)

        page = pager.get_page(4)
        self.assertEqual(page.offset, 31)
        self.assertEqual(page.row_limit, pager.row_limit)

        page = pager.get_page(5)
        self.assertEqual(page.offset, 41)
        self.assertEqual(page.row_limit, pager.row_limit)

        page = pager.get_page(6)
        self.assertEqual(page.offset, 51)
        self.assertEqual(page.row_limit, pager.row_limit)

        page = pager.get_page(7)
        self.assertIsNone(page)

