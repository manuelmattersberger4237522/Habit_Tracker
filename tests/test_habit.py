import pytest
from datetime import datetime, timedelta
import shutil
from context import src
from src.habit import Habit, Periodicity, StreakType, DatabaseTable
from src.database_manager import DatabaseManager

pytest.main()


class TestHabit:

    __EXAMPLE_DATABASE_NAME = "example_habit.db"
    __TEST_DATABASE_NAME = "test_habit.db"

    def setup_method(self):

        # Copy example data to test database
        shutil.copy(self.__EXAMPLE_DATABASE_NAME, self.__TEST_DATABASE_NAME)

        self.__database_manager = DatabaseManager(self.__TEST_DATABASE_NAME)

        self.__habits = []
        
        # Create loaded habits
        self.loaded_habit_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        for row in self.loaded_habit_table:
            habit = Habit(row[0], 
                          row[1], 
                          row[2], 
                          Periodicity(row[3]), 
                          datetime.fromisoformat(row[4]), 
                          database_name=self.__TEST_DATABASE_NAME)
            self.__habits.append(habit)

        self.loaded_check_off_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        for row in self.loaded_check_off_table:
            habit_id = row[1]
            check_off_datetime = datetime.fromisoformat(row[2])

            for habit in self.__habits:
                if habit.habit_id == habit_id:
                    habit.check_off([check_off_datetime])
                    break

    def test_check_off(self):

        assert self.__habits[0].get_streak(StreakType.CURRENT) == 0

        self.__habits[0].check_off()
        assert self.__habits[0].get_streak(StreakType.CURRENT) == 1

        dates_to_check_off = [
            datetime.now() - timedelta(days=i) 
            for i in range(1,5)]
        self.__habits[0].check_off(dates_to_check_off)
        assert self.__habits[0].get_streak(StreakType.CURRENT) == 5

    def test_get_streak_current(self):

        self.__habits[1].check_off([datetime.now() - timedelta(days=2)])
        assert self.__habits[1].get_streak(StreakType.CURRENT) == 0

        self.__habits[1].check_off([datetime.now() - timedelta(days=1)])
        assert self.__habits[1].get_streak(StreakType.CURRENT) == 2

        self.__habits[1].check_off()
        assert self.__habits[1].get_streak(StreakType.CURRENT) == 3

        self.__habits[2].check_off([datetime.now() - timedelta(days=17)])
        assert self.__habits[2].get_streak(StreakType.CURRENT) == 0

        self.__habits[2].check_off([datetime.now() - timedelta(days=10)])
        self.__habits[2].check_off([datetime.now() - timedelta(days=3)])
        assert self.__habits[2].get_streak(StreakType.CURRENT) == 3

        self.__habits[2].check_off([datetime.now() - timedelta(days=15)])
        assert self.__habits[2].get_streak(StreakType.CURRENT) == 2

        self.__habits[2].check_off()
        assert self.__habits[2].get_streak(StreakType.CURRENT) == 1

    def test_get_streak_longest(self):

        assert self.__habits[1].get_streak(StreakType.LONGEST) == 14

        self.__habits[1].check_off([datetime(year=2024, month=8, day=1)])
        for i in range(4,15):
            self.__habits[1].check_off([datetime(year=2024, month=8, day=i)])
        assert self.__habits[1].get_streak(StreakType.LONGEST) == 18

        self.__habits[1].check_off([datetime(year=2024, month=7, day=30)])
        assert self.__habits[1].get_streak(StreakType.LONGEST) == 16

        assert self.__habits[2].get_streak(StreakType.LONGEST) == 5

        self.__habits[2].check_off([datetime(year=2024, month=8, day=10)])
        assert self.__habits[2].get_streak(StreakType.LONGEST) == 6

        self.__habits[2].check_off([datetime(year=2024, month=7, day=20)])
        assert self.__habits[2].get_streak(StreakType.LONGEST) == 4

    def test_save(self):

        habit = Habit(5, 
                      "Running", 
                      "Go running once a week.", 
                      Periodicity.WEEKLY, 
                      datetime(year=2024, month=7, day=2), 
                      database_name=self.__TEST_DATABASE_NAME)
        habit.check_off(
            [datetime(year=2024, month=7, day=2), 
             datetime(year=2024, month=7, day=9)])

        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower(), 
            {"habit_id": 5})
        assert loaded_table == [
            (5, 
             "Running", 
             "Go running once a week.", 
             7, 
             datetime(year=2024, month=7, day=2).isoformat())]
        
        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
            {"habit_id": 5})
        assert loaded_table == [
            (79, 5, datetime(year=2024, month=7, day=2).isoformat()), 
            (80, 5, datetime(year=2024, month=7, day=9).isoformat())]

    def test_delete(self):

        self.__habits[4].delete()
        self.__habits[1].delete()

        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        assert loaded_table == [
            row 
            for row in self.loaded_habit_table 
            if row[0] in [0, 2, 3]]

        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        assert loaded_table == [
            row 
            for row in self.loaded_check_off_table 
            if row[1] in [0, 2, 3]]

    def teardown_method(self):
        
        for habit in self.__habits:
            del habit
        del self.__database_manager