# Habit_Tracker

An application for tracking habits.

## Note

Installation, usage and testing was only tested on Windows 11, Anaconda version 4.12.0 and with the environment 'habit_tracker_env' (installation described in section 'Installation').

## Installation

To install an environment with the necessary dependencies, use the following 'Anaconda Prompt (anaconda3)' command:

```powershell
conda create --name habit_tracker_env --file requirements.txt -c conda-forge
```

## Preparation

To activate the environment installed in section 'Installation', use the following 'Anaconda Prompt (anaconda3)' command:

```powershell
conda activate habit_tracker_env
```

Note: This must be done everytime after restarting 'Anaconda Prompt (anaconda3)'.

## Usage

### Running the application

To run the application, in 'Anaconda Prompt (anaconda3)' navigate to the folder 'Habit_Tracker' and use the following 'Anaconda Prompt (anaconda3)' command:

```powershell
python main.py
```

Note: Assumes that environment 'habit_tracker_env' is activated (activation described in section 'Preparation').

### Using the application

For navigating the menus use the up and down arrow keys.
When the right menu option is highlighted, use the enter key for selection.

## Testing

To run the tests, in 'Anaconda Prompt (anaconda3)' navigate to the folder 'Habit_Tracker' and use the following 'Anaconda Prompt (anaconda3)' command:

```powershell
pytest tests
```

Note: Assumes that environment 'habit_tracker_env' is activated (activation described in section 'Preparation').
