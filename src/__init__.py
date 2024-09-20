from enum import Enum

__all__ = ["__init__", "database_manager", "habit", "habit_manager"]


class Periodicity(Enum):
    DAILY = 1
    WEEKLY = 7

class StreakType(Enum):
    CURRENT = 1
    LONGEST = 2

class DatabaseTable(Enum):
    HABIT = 1
    CHECK_OFF_DATETIME = 2

class DatabaseCommand(Enum):
    CREATE_TABLE = 1
    INSERT_INTO = 2
    UPDATE = 3
    DELETE_FROM = 4
    SELECT = 5