from enum import Enum
import questionary
from src.habit_manager import HabitManager, Periodicity, StreakType


class Command(Enum):
    CREATE_HABIT = 1
    GET_HABITS = 2
    CHECK_OFF = 3
    GET_STREAK = 4
    DELETE_HABIT = 5
    STOP_APPLICATION = 6


def get_habit_string(habit, advanced=False):
    """
    Returns a string containing the metadata of a habit. Meant for printing the habit.

    Args:
        habit (dict): The habit metadata. Must include "attribute name"-"value" pairs.
        advanced (bool): If True, a longer string including all habit metadata will get returned.

    Returns:
        str: The string containing habit metadata.
    """

    habit_id = habit["habit_id"]
    name = habit["name"]
    description = habit["description"]
    periodicity = habit["periodicity"]
    created = habit["creation_datetime"].replace("T", " ")

    if not advanced:
        return f"{name}: {description} ({periodicity})"
    else:
        return f"{habit_id} {name}: {description} ({periodicity}) Created: {created}"

def cli():
    """
    Provides a command line interface to the user in order to use the habit tracker.
    """

    command_choices = [{"name": command.name.capitalize().replace("_", " "), 
                        "value": command} 
                       for command in Command]
    periodicity_choices = [{"name": periodicity.name.capitalize().replace("_", " "), 
                            "value": periodicity} 
                           for periodicity in Periodicity]
    streak_type_choices = [{"name": streak_type.name.capitalize().replace("_", " "), 
                            "value": streak_type} 
                           for streak_type in StreakType]

    run_application = True
    
    try:
        habit_manager = HabitManager("habit.db")
    except:
        run_application = False
        print("Because of an occured error the application will be stopped to prevent wrong behavior.")

    while run_application:
        command = questionary.select(
                    "Choose an action:", 
                    choices=command_choices
                    ).ask()
        
        if command == Command.CREATE_HABIT:
            habit_name = questionary.text(
                "Input habit name:"
                ).ask()
            habit_description = questionary.text(
                "Input habit description:"
                ).ask()
            habit_periodicity = questionary.select(
                    "Choose a habit periodicity:", 
                    choices=periodicity_choices
                    ).ask()

            habit_manager.create_habit(habit_name, 
                                       habit_description, 
                                       habit_periodicity)
            print("Habit has been created.\n")

        elif command == Command.GET_HABITS:
            choices = [{"name": "All", "value": "None"}] + periodicity_choices

            periodicity = questionary.select(
                    "Choose a habit periodicity:", 
                    choices=choices
                    ).ask()
            periodicity = (None 
                           if periodicity == "None" 
                           else periodicity)

            habits = habit_manager.get_all_habits(periodicity)
            for habit in habits:
                print(get_habit_string(habit, advanced=True))
            print("")

        elif command == Command.CHECK_OFF:
            habits = habit_manager.get_all_habits(periodicity=None)
            choices = [{"name": get_habit_string(habit), 
                        "value": habit["habit_id"]} 
                        for habit in habits]
            
            if choices != []:
                habit_id = questionary.select(
                        "Choose a habit:", 
                        choices=choices
                        ).ask()

                habit_manager.check_off(habit_id)
                print("Habit has been checked off.\n")

            else:
                print("No habits to check off exist at the moment, please create a habit first!\n")

        elif command == Command.GET_STREAK:
            habits = habit_manager.get_all_habits(periodicity=None)
            choices = (
                [{"name": "All", "value": "None"}]
                + [{"name": get_habit_string(habit),
                    "value": habit["habit_id"]}
                    for habit in habits]
                )

            habit_id = questionary.select(
                    "Choose a habit:", 
                    choices=choices
                    ).ask()
            habit_id = (None 
                        if habit_id == "None" 
                        else habit_id)

            streak_type = questionary.select(
                    "Choose a streak type:", 
                    choices=streak_type_choices
                    ).ask()
            
            print(f"Streak: {habit_manager.get_streak(streak_type, habit_id)}\n")

        elif command == Command.DELETE_HABIT:
            habits = habit_manager.get_all_habits(periodicity=None)
            choices = [{"name": get_habit_string(habit), 
                        "value": habit["habit_id"]} 
                        for habit in habits]

            if choices != []:
                habit_id = questionary.select(
                        "Choose a habit:", 
                        choices=choices
                        ).ask()
                
                habit_manager.delete_habit(habit_id)
                print("Habit has been deleted.\n")

            else:
                print("No habits to delete exist at the moment!\n")

        elif command == Command.STOP_APPLICATION:
            del habit_manager
            run_application = False

    print("Application has been stopped.\n")

if __name__ == "__main__":
    cli()