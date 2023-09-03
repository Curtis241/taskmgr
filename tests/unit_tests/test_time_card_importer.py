import unittest

from taskmgr.lib.database.db_manager import DatabaseManager
from taskmgr.lib.model.time_card import TimeCard
from taskmgr.lib.presenter.sync import SyncAction
from taskmgr.lib.presenter.time_card_sync import TimeCardImporter
from taskmgr.lib.variables import CommonVariables


class TestTimeCardImporter(unittest.TestCase):

    def setUp(self):
        self.vars = CommonVariables('test_variables.ini')
        self.time_cards = DatabaseManager(self.vars).get_time_cards_model()
        self.time_cards.clear()
        self.importer = TimeCardImporter(self.time_cards)

    def tearDown(self):
        self.time_cards.clear()

    def test_convert_time_cards(self):
        obj_list = list()
        obj_list.append({'index': '1', 'time_in': '8:00', 'time_out': '10:00', 'elapsed_time': '2:00',
                 'date': '2020-09-10', 'last_updated': '2020-09-10 22:37:23', 'deleted': 'False',
                 'unique_id': 'bc2d81c94e3844228ccb9bfe2613c089'})
        obj_list.append({'index': '2', 'time_in': '10:00', 'time_out': '12:00', 'elapsed_time': '2:00',
                 'date': '2020-10-06', 'last_updated': '2020-10-06 22:00:46', 'deleted': 'False',
                 'unique_id': '3413035ab1f14cccb70a315e42c3242e'})
        obj_list.append({'index': '3', 'time_in': '12:30', 'time_out': '17:00', 'elapsed_time': '4:30',
                 'date': '2020-10-06', 'last_updated': '2020-10-06 22:01:05', 'deleted': 'False',
                 'unique_id': '1fd2878c4c64446fbbce21b79a7ce1ca'})
        time_card_list = self.importer.convert(obj_list)
        self.assertTrue(len(time_card_list) == 3)

    def test_convert_time_card_with_minimal_data(self):
        obj_list = list()
        obj_list.append({'time_in': '8:00', 'time_out': '10:00', 'date': '2020-09-10'})
        obj_list.append({'time_in': '10:00', 'time_out': '12:00', 'date': '2020-10-06'})
        obj_list.append({'time_in': '12:30', 'time_out': '17:00',  'date': '2020-10-06'})
        time_card_list = self.importer.convert(obj_list)
        self.assertTrue(len(time_card_list) == 3)


    def test_import_time_cards(self):
        time_card1 = TimeCard()
        time_card1.time_in = "8:00"
        time_card1.time_out = "10:00"
        time_card1.date = "2023-07-04"
        time_card1.elapsed_time = "2:00"
        time_card1.unique_id = "1"

        time_card2 = TimeCard()
        time_card2.time_out = "12:00"
        time_card2.elapsed_time = "4:00"
        time_card2.deleted = False
        time_card2.unique_id = "1"

        time_card3 = TimeCard()
        time_card3.deleted = True
        time_card3.unique_id = "1"

        time_card_list = [time_card1, time_card2, time_card3]

        sync_results = self.importer.import_objects(time_card_list)
        sync_results_list = sync_results.get_list()
        self.assertTrue(len(sync_results_list) == 3)

        self.assertTrue(sync_results_list[0] == SyncAction.ADDED)
        self.assertTrue(sync_results_list[1] == SyncAction.UPDATED)
        self.assertTrue(sync_results_list[2] == SyncAction.DELETED)
