import sqlite3
import copy
from . import DatabaseCommand


class DatabaseManager:
    """
    Represents a database manager.

    Attributes:
        database_name (str): The name of the database where the data gets stored and loaded from.
    """

    def __init__(self, database_name):
        """
        Initializes a new instance of the DatabaseManager class.

        Args:
            database_name (str): The name of the database where the data gets stored and loaded from.
        """
        
        self.database_name = database_name

    def initialize_database(self, 
                            database_table_name, data_structure, 
                            foreign_keys={}):
        """
        Creates a database table.

        Args:
            database_table_name (str): The name of the database table that should be created.
            data_structure (dict): The data structure of the database table. Must include "column name"-"data type" pairs.
            foreign_keys (dict): The foreign keys of the database table. Must include "foreign key"-"reference" pairs.
        """

        try:
            with sqlite3.connect(self.database_name) as connection:
                cursor = connection.cursor()
                sql_command = self.__create_sql_string(
                    DatabaseCommand.CREATE_TABLE, 
                    database_table_name, 
                    data_structure, 
                    foreign_keys)
                cursor.execute(sql_command)
                connection.commit()

        except Exception as error:
            print(f"During initializing the database an error occurred: {error}")

    def save(self, 
             database_table_name, data_record, primary_key_name, 
             only_insert_if_unique=False):
        """
        Saves a data record in a database table.

        Args:
            database_table_name (str): The name of the database table where the data record should be saved in.
            data_record (dict): The data record to save in the database table. Must include "column name"-"value" pairs.
            primary_key_name (str): The name of the primary key. If not first key of the table, primary key will automatically get created.
            only_insert_if_unique (bool): If True, the data record will only get inserted into the database table if it is unique (not considering the primary key).
        """

        try:
            with sqlite3.connect(self.database_name) as connection:
                cursor = connection.cursor()

                # Create primary key if not given
                first_key = next(iter(data_record))
                if primary_key_name != first_key:
                    primary_key_value = self.__create_primary_key(
                        database_table_name, 
                        cursor)
                    data_record = ({primary_key_name: str(primary_key_value)} 
                                   | data_record)

                # Check if primary_key exists already, then insert or update in database
                sql_command = self.__create_sql_string(
                    DatabaseCommand.SELECT, 
                    database_table_name, 
                    where_expressions={primary_key_name: data_record[primary_key_name]})
                cursor.execute(sql_command)
                primary_key_result = cursor.fetchall()

                # Check if data record is unique
                data_record_copy = copy.deepcopy(data_record)
                del data_record_copy[primary_key_name]

                sql_command = self.__create_sql_string(
                    DatabaseCommand.SELECT, 
                    database_table_name, 
                    where_expressions=data_record_copy)
                cursor.execute(sql_command)
                same_records_result = cursor.fetchall()

                if (only_insert_if_unique == False 
                    or (only_insert_if_unique and same_records_result == [])):
                    if primary_key_result == []:
                        sql_command = self.__create_sql_string(DatabaseCommand.INSERT_INTO, database_table_name, data_record=data_record)
                    else:
                        sql_command = self.__create_sql_string(DatabaseCommand.UPDATE, database_table_name, data_record=data_record)
                cursor.execute(sql_command)

                connection.commit()
            
        except Exception as error:
            print(f"During saving in the database an error occurred: {error}")

    def delete(self, database_table_name, where_expressions={}):
        """
        Deletes records from a database table.

        Args:
            database_table_name (str): The name of the database table where data should be deleted from.
            where_expressions (dict): Defines the where expressions of the command. Must include "column name"-"value" pairs.
        """

        try:
            with sqlite3.connect(self.database_name) as connection:
                cursor = connection.cursor()
                sql_command = self.__create_sql_string(
                    DatabaseCommand.DELETE_FROM, 
                    database_table_name, 
                    where_expressions=where_expressions)
                cursor.execute(sql_command)

                connection.commit()

        except Exception as error:
            print(f"During deleting from the database an error occurred: {error}")

    def load(self, database_table_name, where_expressions={}):
        """
        Loads and returns a database table.

        Args:
            database_table_name (str): The name of the database table where data should be loaded from.
            where_expressions (dict): Defines the where expressions of the command. Must include "column name"-"value" pairs.

        Returns:
            list: The loaded table.
        """

        try:
            with sqlite3.connect(self.database_name) as connection:
                cursor = connection.cursor()
                sql_command = self.__create_sql_string(
                    DatabaseCommand.SELECT, 
                    database_table_name, 
                    where_expressions=where_expressions)
                cursor.execute(sql_command)

                result = cursor.fetchall()
                return result
                
        except sqlite3.OperationalError as error:
            if "no such table: " in str(error):
                return []
            else:
                print(f"During loading from the database an error occurred: {error}")
                return None
            
        except Exception as error:
            print(f"During loading from the database an error occurred: {error}")
            return None
            
    def __create_primary_key(self, database_table_name, cursor):
        """
        Creates and returns a primary key.

        Args:
            database_table_name (str): The name of the database table where the primary key will become part of.
            cursor (sqlite3.Cursor): The cursor used for executing SQL commands.

        Returns:
            int: The primary key.
        """

        sql_command = self.__create_sql_string(
            DatabaseCommand.SELECT, 
            database_table_name)
        cursor.execute(sql_command)
        primary_key_result = cursor.fetchall()

        primary_key = 0
        existing_primary_keys = [
            result_row[0] 
            for result_row in primary_key_result]
        
        while primary_key in existing_primary_keys:
            primary_key += 1
        
        return primary_key

    def __create_sql_string(self, 
                            command, table_name, 
                            data_structure=None, data_record=None, 
                            foreign_keys={}, where_expressions={}):
        """
        Creates and returns specific SQL command strings ready to be executed.

        Args:
            command (DatabaseCommand): The command to create a string for.
            table_name (str): The name of the database table where data should be written to or read from.
            data_structure (dict): The data structure for creating database tables. Must include "column name"-"data type" pairs. Only used for command "DatabaseCommand.CREATE_TABLE".
            data_record (dict): The data record to save in the database. Must include "column name"-"value" pairs. Only used for commands "DatabaseCommand.INSERT_INTO" and "DatabaseCommand.UPDATE".
            foreign_keys (dict): The foreign keys of the database table. Must include "foreign key"-"reference" pairs. Only used for command "DatabaseCommand.CREATE_TABLE".
            where_expressions (dict): Defines the where expressions of the command. Must include "column name"-"value" pairs. Only used for commands "DatabaseCommand.DELETE_FROM" and "DatabaseCommand.SELECT".

        Returns:
            str: The SQL command string.
        """

        if command == DatabaseCommand.CREATE_TABLE:
            sql_string = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                """
            first_key = next(iter(data_structure))

            for key, value in data_structure.items():
                if key == first_key:
                    comma = ""
                    extension = "PRIMARY KEY"
                else:
                    comma = ",\n"
                    extension = "NOT NULL"
                sql_string += f"{comma}{key} {value} {extension}"

            for key, value in foreign_keys.items():
                sql_string += f",\nFOREIGN KEY({key}) REFERENCES {value}"

            sql_string += "\n)"
            return sql_string
        
        elif command == DatabaseCommand.INSERT_INTO:
            keys_string, values_string = self.__get_dictionary_string(data_record)
            sql_string = f"""
                INSERT INTO {table_name} ({keys_string}) 
                VALUES ({values_string})
                """
            return sql_string
        
        elif command == DatabaseCommand.UPDATE:
            set_string = ", ".join(
                [F"{key} = '{value}'" 
                 for (key, value) in list(data_record.items())[1:]])
            sql_string = f"""
                UPDATE {table_name} 
                SET {set_string} 
                WHERE {next(iter(data_record))} = '{next(iter(data_record.values()))}'
                """
            return sql_string
        
        elif command == DatabaseCommand.DELETE_FROM:
            sql_string = f"""
                DELETE FROM {table_name}
                """

            if where_expressions != {}:
                first_key = next(iter(where_expressions))

                for key, value in where_expressions.items():
                    if key == first_key:
                        sql_string += f"WHERE {key} = '{value}'"
                    else:
                        sql_string += f" AND {key} = '{value}'"

            return sql_string

        elif command == DatabaseCommand.SELECT:
            sql_string = f"""
                SELECT * FROM {table_name}
                """

            if where_expressions != {}:
                first_key = next(iter(where_expressions))

                for key, value in where_expressions.items():
                    if key == first_key:
                        sql_string += f"WHERE {key} = '{value}'"
                    else:
                        sql_string += f" AND {key} = '{value}'"

            return sql_string

    def __get_dictionary_string(self, dictionary):
        """
        Converts the dictionary keys and the dictionary values into comma seperated strings and returns both strings.

        Args:
            dictionary (dict): The dictionary to take the keys and values from.

        Returns:
            str: The comma seperated string of the keys.
            str: The comma seperated string of the values.
        """

        keys = [key for key in dictionary.keys()]
        values = [f'"{value}"' for value in dictionary.values()]

        keys_string = ", ".join(keys)
        values_string = ", ".join(values)

        return keys_string, values_string