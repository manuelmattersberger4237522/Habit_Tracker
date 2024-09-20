from datetime import datetime
from src.habit import Habit, Periodicity, StreakType, DatabaseTable
from src.database_manager import DatabaseManager


class HabitManager:
    """
    Represents a habit manager.

    Attributes:
        database_name (str): The name of the database where the habit gets saved in and loaded from.
        __habits (list): The existing habits.
        __database_manager (DatabaseManager): An instance of the DatabaseManager class.
    """

    def __init__(self, database_name="habit.db"):
        """
        Initializes a new instance of the HabitManager class.

        Attributes:
            database_name (str): The name of the database where the habit gets saved in and loaded from.
        """
        
        self.database_name = database_name

        self.__habits = []
        self.__database_manager = DatabaseManager(self.database_name)

        self.__load_data()

    def __load_data(self):
        """
        Loads all data from the database. Loads the habit data and saves the Habit instances in self.__habits. Also loads the check off datetimes and checkes them off for the according habits in self.__habits.
        """
        
        loaded_table = self.__database_manager.load(DatabaseTable.HABIT.name.lower())
        for row in loaded_table:
            habit = Habit(row[0], 
                          row[1], 
                          row[2], 
                          Periodicity(row[3]), 
                          datetime.fromisoformat(row[4]), 
                          database_name=self.database_name)
            self.__habits.append(habit)

        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        for row in loaded_table:
            habit_id = row[1]
            check_off_datetime = datetime.fromisoformat(row[2])
            self.check_off(habit_id, [check_off_datetime])

    def create_habit(self, name, description, periodicity):
        """
        Creates a habit and appends it to self.__habits.

        Args:
            name (str): The name of the habit.
            description (str): The description of the habit.
            periodicity (Periodicity): The periodicity of the habit.
        """
        
        habit_id = self.__create_habit_id()
        habit = Habit(
            habit_id, 
            name, 
            description, 
            periodicity, 
            database_name=self.database_name)
        self.__habits.append(habit)

    def delete_habit(self, habit_id):
        """
        Deletes a habit and removes it from self.__habits.

        Args:
            habit_id (int): The habit_id of the habit.
        """
        
        for habit in self.__habits:
            if habit_id == habit.habit_id:
                habit.delete()
                self.__habits.remove(habit)

    def check_off(self, habit_id, datetimes=[datetime.now()]):
        """
        Checks off a habit for the given datetimes.

        Args:
            habit_id (int): The habit_id of the habit to check off.
            datetimes (list): The datetimes to check off.
        """
        
        for habit in self.__habits:
            if habit_id == habit.habit_id:
                habit.check_off(datetimes)
                break

    def get_all_habits(self, periodicity=None):
        """
        Returns the habits.

        Args:
            periodicity (Periodicity): Only the habits with this periodicity get returned. If None, all habits will be returned

        Returns:
            list: The matching habits in self.__habits.
        """
        
        if periodicity is None:
            all_habits = [
                {"habit_id": habit.habit_id, 
                "name": habit.name, 
                "description": habit.description, 
                "periodicity": habit.periodicity.name.capitalize(), 
                "creation_datetime": habit.creation_datetime.isoformat()} 
                for habit in self.__habits]
            
        else:
            all_habits = [
                {"habit_id": habit.habit_id, 
                "name": habit.name, 
                "description": habit.description, 
                "periodicity": habit.periodicity.name.capitalize(), 
                "creation_datetime": habit.creation_datetime.isoformat()} 
                for habit in self.__habits
                if habit.periodicity == periodicity]
        
        return all_habits

    def get_streak(self, streak_type, habit_id=None):
        """
        Calculates and returns the habit streak.

        Args:
            streak_type (StreakType): The streak type to calculate.
            habit_id (int): The habit_id of the habit to calculate the streak for. If None, the longest streak of all habits will be returned.

        Returns:
            int: The habit streak.
        """
        
        if habit_id is None:
            longest_streak = 0

            for habit in self.__habits:
                this_streak = habit.get_streak(streak_type)
                longest_streak = max(longest_streak, this_streak)

            return longest_streak
        
        else:
            for habit in self.__habits:
                if habit_id == habit.habit_id:
                    return habit.get_streak(streak_type)
            
            return 0

    def __create_habit_id(self):
        """
        Creates and returns a unique habit_id.

        Returns:
            int: The habit_id.
        """
        
        existing_habit_ids = self.__get_habit_ids()
        habit_id = 0

        while habit_id in existing_habit_ids:
            habit_id += 1

        return habit_id

    def __get_habit_ids(self):
        """
        Returns all existing habit_ids.

        Returns:
            list: The existing habit_ids.
        """
        
        habit_ids = [habit.habit_id for habit in self.__habits]

        return habit_ids