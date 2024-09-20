from datetime import datetime, date, timedelta
from . import Periodicity, StreakType, DatabaseTable
from src.database_manager import DatabaseManager


class Habit:
    """
    Represents a habit.

    Attributes:
        habit_id (int): The identifier for this habit.
        name (str): The name of the habit.
        description (str): The description of the habit.
        periodicity (Periodicity): The periodicity of the habit.
        creation_datetime (datetime.datetime): The creation datetime of the habit.
        database_name (str): The name of the database where the habit gets saved.
        __checked_off_datetimes (list): The checked off datetimes for this habit.
        __database_manager (DatabaseManager): An instance of the DatabaseManager class.
    """

    def __init__(self, 
                 habit_id, name, description, periodicity, 
                 creation_datetime=None, database_name="habit.db"):

        """
        Initializes a new instance of the Habit class, initializes the database and saves the habit in the database.

        Args:
            habit_id (int): The identifier for this habit.
            name (str): The name of the habit.
            description (str): The description of the habit.
            periodicity (Periodicity): The periodicity of the habit.
            creation_datetime (datetime.datetime): The creation datetime of the habit.
            database_name (str): The name of the database where the habit gets saved.
        """
        
        self.habit_id = habit_id
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.creation_datetime = (datetime.now() 
                                  if creation_datetime is None 
                                  else creation_datetime)
        self.database_name = database_name

        self.__checked_off_datetimes = []
        self.__database_manager = DatabaseManager(self.database_name)

        self.__initialize_database()
        self.__save(DatabaseTable.HABIT)

    def check_off(self, datetimes=[datetime.now()]):
        """
        Checkes off datetimes and saves them in the database.

        Args:
            datetimes (list): The datetimes to check off.
        """
        
        for datetime in datetimes:
            if datetime not in self.__checked_off_datetimes:
                self.__checked_off_datetimes.append(datetime)

        self.__save(DatabaseTable.CHECK_OFF_DATETIME)
    
    def delete(self):
        """
        Deletes the habit instance and the according checked off dates from the database.
        """
        
        for database_table in DatabaseTable:
            self.__database_manager.delete(
                database_table.name.lower(), 
                where_expressions={"habit_id": self.habit_id})

    def get_streak(self, streak_type):
        """
        Calculates and returns the streak.

        Args:
            streak_type (StreakType): The streak type to calculate.

        Returns:
            int: The streak of the habit.
        """
        
        if streak_type == StreakType.CURRENT:
            return self.__get_current_streak()
        
        elif streak_type == StreakType.LONGEST:
            return self.__get_longest_streak()

    def __get_current_streak(self):
        """
        Calculates and returns the current streak.

        Returns:
            int: The current streak of the habit.
        """
        
        checked_off_dates = [
            checked_off_datetime.date() 
            for checked_off_datetime in self.__checked_off_datetimes]
        reverse_sorted_dates = sorted(checked_off_dates, reverse=True)
        period_ago_day = date.today() - timedelta(days=self.periodicity.value)

        if reverse_sorted_dates == [] or reverse_sorted_dates[0] < period_ago_day:
            return 0
        
        else:
            streak = 1

            for i in range(1, len(reverse_sorted_dates)):
                date_1 = reverse_sorted_dates[i-1]
                date_2 = reverse_sorted_dates[i]
                day_difference = (date_1 - date_2).days

                if day_difference == self.periodicity.value:
                    streak += 1
                else:
                    return streak
                
            return streak

    def __get_longest_streak(self):
        """
        Calculates and returns the longest streak.

        Returns:
            int: The longest streak of the habit.
        """
        
        checked_off_dates = [
            checked_off_datetime.date() 
            for checked_off_datetime in self.__checked_off_datetimes]
        sorted_dates = sorted(checked_off_dates)

        if sorted_dates == []:
            return 0
        
        else:
            temp_streak = 1
            streak = temp_streak

            for i in range(1, len(sorted_dates)):
                date_1 = sorted_dates[i-1]
                date_2 = sorted_dates[i]
                day_difference = (date_2 - date_1).days

                if day_difference == self.periodicity.value:
                    temp_streak += 1
                    streak = max(streak, temp_streak)
                else:
                    temp_streak = 1

            return streak

    def __initialize_database(self):
        """
        Creates the tables in the database.
        """
        
        habit_data_structure = {
            "habit_id": "INTEGER",
            "name": "TEXT",
            "description": "TEXT",
            "periodicity": "INTEGER",
            "creation_datetime": "TEXT"}
        self.__database_manager.initialize_database(
            DatabaseTable.HABIT.name.lower(), 
            habit_data_structure)

        check_off_data_structure = {
            "id": "INTEGER",
            "habit_id": "INTEGER",
            "check_off_datetime": "TEXT"}
        self.__database_manager.initialize_database(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
            check_off_data_structure, 
            foreign_keys={"habit_id": "habit(habit_id)"})

    def __save(self, database_table):
        """
        Saves data from this habit instance in the provided table in the database.

        Args:
            database_table (DatabaseTable): The database table that should be updated.
        """
        
        if database_table == DatabaseTable.HABIT:
            data_record = {"habit_id": str(self.habit_id),
                           "name": self.name,
                           "description": self.description,
                           "periodicity": str(self.periodicity.value),
                           "creation_datetime": self.creation_datetime.isoformat()}
            
            self.__database_manager.save(
                DatabaseTable.HABIT.name.lower(), 
                data_record, 
                primary_key_name="habit_id")

        elif database_table == DatabaseTable.CHECK_OFF_DATETIME:
            for check_off_datetime in self.__checked_off_datetimes:
                data_record = {"habit_id": str(self.habit_id),
                               "check_off_datetime": check_off_datetime.isoformat()}
                
                self.__database_manager.save(
                    DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
                    data_record, 
                    primary_key_name="id", 
                    only_insert_if_unique=True)