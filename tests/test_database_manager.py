import pytest
from datetime import datetime, timedelta
import shutil
import sqlite3
from context import src
from src.database_manager import DatabaseManager
from src.habit import DatabaseTable


class TestDatabaseManager:

    __EXAMPLE_DATABASE_NAME = "example_habit.db"
    __TEST_DATABASE_NAME = "test_habit.db"

    def setup_method(self):

        self.__habit_data_structure = {
            "habit_id": "INTEGER",
            "name": "TEXT",
            "description": "TEXT",
            "periodicity": "INTEGER",
            "creation_datetime": "TEXT"}
        self.__check_off_data_structure = {
            "id": "INTEGER",
            "habit_id": "INTEGER",
            "check_off_datetime": "TEXT"}
        
        self.__habit_data_records = []
        self.__check_off_data_records = []

        # Copy example data to test database
        shutil.copy(self.__EXAMPLE_DATABASE_NAME, self.__TEST_DATABASE_NAME)

        self.__database_manager = DatabaseManager(self.__TEST_DATABASE_NAME)

        # Create loaded habits
        self.loaded_habit_table = self.select_from_database_table(
            DatabaseTable.HABIT.name.lower())

        for row in self.loaded_habit_table:
            data_structure_keys = list(self.__habit_data_structure.keys())
            data_record = {}

            for key in data_structure_keys:
                data_record[key] = row[data_structure_keys.index(key)]

            self.__habit_data_records.append(data_record)
        
        self.loaded_check_off_table = self.select_from_database_table(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())

        for row in self.loaded_check_off_table:
            data_structure_keys = list(self.__check_off_data_structure.keys())

            data_record["habit_id"] = row[1]
            data_record["check_off_datetime"] = row[2]

            self.__check_off_data_records.append(data_record)

    def test_initialize_database(self):

        test_table_name = "habit_test"
        loaded_table = self.select_from_database_table(test_table_name)
        assert loaded_table is None

        self.__database_manager.initialize_database(
            test_table_name, 
            self.__habit_data_structure)
        loaded_table = self.select_from_database_table(test_table_name)
        assert loaded_table == []

        self.__database_manager.initialize_database(
            DatabaseTable.HABIT.name.lower(), 
            self.__habit_data_structure)
        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        assert loaded_table == self.loaded_habit_table

        self.__database_manager.initialize_database(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
            self.__check_off_data_structure, 
            foreign_keys={"habit_id": "habit(habit_id)"})
        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        assert loaded_table == self.loaded_check_off_table

    def test_load(self):

        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        assert loaded_table == self.loaded_habit_table

        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        assert loaded_table == self.loaded_check_off_table

    def test_save_habit(self):

        for data_record in self.__habit_data_records:
            self.__database_manager.save(
                DatabaseTable.HABIT.name.lower(), 
                data_record, 
                "habit_id")

        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        assert loaded_table == self.loaded_habit_table

        data_record_1 = {"habit_id": "1",
        "name": "name_1",
        "description": "description_1",
        "periodicity": "7",
        "creation_datetime": "creation_datetime_1"}
        self.__database_manager.save(
            DatabaseTable.HABIT.name.lower(), 
            data_record_1, 
            "habit_id")
        data_record_5 = {"habit_id": "5",
        "name": "name_5",
        "description": "description_5",
        "periodicity": "1",
        "creation_datetime": "creation_datetime_5"}
        self.__database_manager.save(
            DatabaseTable.HABIT.name.lower(), 
            data_record_5, 
            "habit_id")
        self.__database_manager.save(
            DatabaseTable.HABIT.name.lower(), 
            data_record_5, 
            "habit_id")
        for data_record in self.__habit_data_records:
            self.__database_manager.save(
                DatabaseTable.HABIT.name.lower(), 
                data_record, 
                "habit_id")

        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        assert loaded_table == (self.loaded_habit_table 
                                + [tuple(int(value) 
                                         if value.isdigit() 
                                         else value 
                                         for value in data_record_5.values())])

    def test_check_off_date_save(self):

        data_record = {
            "habit_id": "0",
            "check_off_datetime": (datetime.now()).isoformat()}
        self.__database_manager.save(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
            data_record, 
            "id")
        data_record_1_tuple = tuple(
            int(value) 
            if value.isdigit() 
            else value 
            for value in ["79"] + list(data_record.values()))

        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        assert loaded_table == self.loaded_check_off_table + [data_record_1_tuple]

        data_record = {
            "habit_id": "1",
            "check_off_datetime": (datetime.now() - timedelta(days=5)).isoformat()}
        self.__database_manager.save(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
            data_record, 
            "id")
        data_record_2_tuple = tuple(
            int(value) 
            if value.isdigit() 
            else value 
            for value in ["80"] + list(data_record.values()))

        data_record = {
            "habit_id": "0",
            "check_off_datetime": (datetime.now() - timedelta(days=1)).isoformat()}
        self.__database_manager.save(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower(), 
            data_record, 
            "id")
        data_record_3_tuple = tuple(
            int(value) 
            if value.isdigit() 
            else value 
            for value in ["81"] + list(data_record.values()))

        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        assert loaded_table == (self.loaded_check_off_table 
                                + [data_record_1_tuple, 
                                   data_record_2_tuple, 
                                   data_record_3_tuple])

    def test_delete(self):

        for database_table in DatabaseTable:
            self.__database_manager.delete(
                database_table.name.lower(), 
                {"habit_id": 2})
            self.__database_manager.delete(
                database_table.name.lower(), 
                {"habit_id": 0})
        for database_table in DatabaseTable:
            self.__database_manager.delete(
                database_table.name.lower(), 
                {"habit_id": 2})

        loaded_table = self.__database_manager.load(
            DatabaseTable.HABIT.name.lower())
        assert loaded_table == [
            row 
            for row in self.loaded_habit_table 
            if row[0] in [1, 3, 4]]

        loaded_table = self.__database_manager.load(
            DatabaseTable.CHECK_OFF_DATETIME.name.lower())
        assert loaded_table == [
            row 
            for row in self.loaded_check_off_table 
            if row[1] in [1, 3, 4]]

    def teardown_method(self):

        del self.__database_manager

    def select_from_database_table(self, table_name):

        try:
            with sqlite3.connect(self.__TEST_DATABASE_NAME) as connection:
                cursor = connection.cursor()
                cursor.execute(f"""
                SELECT * FROM {table_name}
                """)
                return cursor.fetchall()
                
        except sqlite3.OperationalError as error:
            if "no such table: " in str(error):
                return None
            else:
                print(f"During loading from the database an error occurred: {error}")
                return 0
            
        except Exception as error:
            print(f"During loading from the database an error occurred: {error}")
            return 1

pytest.main()