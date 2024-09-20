import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
import shutil
from context import src
from src.habit_manager import HabitManager, DatabaseManager, Periodicity, StreakType, DatabaseTable


class TestHabitManager:

    __DATETIME_NOW = datetime.now()

    __EXAMPLE_DATABASE_NAME = "example_habit.db"
    __TEST_DATABASE_NAME = "test_habit.db"

    def setup_method(self):

        # Copy example data to test database
        shutil.copy(self.__EXAMPLE_DATABASE_NAME, self.__TEST_DATABASE_NAME)

        self.__database_manager = DatabaseManager(self.__TEST_DATABASE_NAME)
        self.__habit_manager = HabitManager(self.__TEST_DATABASE_NAME)

        # Load habit table
        self.loaded_habit_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())

    @freeze_time(__DATETIME_NOW.isoformat().replace("T", " "))
    def test_create_habit(self):
        
        self.__habit_manager.create_habit("habit 1", 
                                          "description 1", 
                                          Periodicity.DAILY)
        assert self.__habit_manager.get_all_habits() == (
            [self.get_habit_dict_from_tuple(habit) 
             for habit in self.loaded_habit_table] 
            + [{"habit_id": 5, 
                "name": "habit 1", 
                "description": "description 1", 
                "periodicity": Periodicity.DAILY.name.capitalize(), 
                "creation_datetime": datetime.now().isoformat()}]
            )
        
    def test_delete_habit(self):
        
        self.__habit_manager.delete_habit(0)
        assert self.__habit_manager.get_all_habits() == [
            self.get_habit_dict_from_tuple(habit) 
            for habit in self.loaded_habit_table 
            if int(habit[0]) not in [0]
            ]
        
        self.__habit_manager.delete_habit(3)
        self.__habit_manager.delete_habit(4)
        assert self.__habit_manager.get_all_habits() == [
            self.get_habit_dict_from_tuple(habit) 
            for habit in self.loaded_habit_table 
            if int(habit[0]) not in [0, 3, 4]
            ]

    def test_check_off(self):
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 1) == 0

        self.__habit_manager.check_off(1)
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 1) == 1

        self.__habit_manager.check_off(1)
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 1) == 1

        self.__habit_manager.check_off(1, 
                                       [datetime.now() - timedelta(days=2), 
                                        datetime.now() - timedelta(days=3)])
        self.__habit_manager.check_off(1, 
                                       [datetime.now() - timedelta(days=1)])
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 1) == 4


    def test_get_all_habits(self):

        assert self.__habit_manager.get_all_habits() == [
            self.get_habit_dict_from_tuple(habit) 
            for habit in self.loaded_habit_table
            ]

        assert self.__habit_manager.get_all_habits(Periodicity.DAILY) == [
            self.get_habit_dict_from_tuple(habit) 
            for habit in self.loaded_habit_table 
            if habit[3] == 1
            ]
        assert self.__habit_manager.get_all_habits(Periodicity.WEEKLY) == [
            self.get_habit_dict_from_tuple(habit) 
            for habit in self.loaded_habit_table 
            if habit[3] == 7
            ]

    def test_get_streak(self):

        assert self.__habit_manager.get_streak(StreakType.CURRENT, 2) == 0
        assert self.__habit_manager.get_streak(StreakType.LONGEST, 2) == 5

        self.__habit_manager.check_off(2)
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 2) == 1

        self.__habit_manager.check_off(2)
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 2) == 1

        self.__habit_manager.check_off(2, 
                                       [datetime.now() - timedelta(days=14), 
                                        datetime.now() - timedelta(days=21)])
        self.__habit_manager.check_off(2, 
                                       [datetime.now() - timedelta(days=7)])
        assert self.__habit_manager.get_streak(StreakType.CURRENT, 2) == 4
        assert self.__habit_manager.get_streak(StreakType.LONGEST, 2) == 5

    def teardown_method(self):

        del self.__habit_manager
        del self.__database_manager

    def get_habit_dict_from_tuple(self, habit_tuple):

        return {"habit_id": int(habit_tuple[0]), 
            "name": habit_tuple[1], 
            "description": habit_tuple[2], 
            "periodicity": Periodicity(habit_tuple[3]).name.capitalize(), 
            "creation_datetime": habit_tuple[4]}

pytest.main()