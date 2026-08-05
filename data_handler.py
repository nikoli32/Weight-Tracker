# data_handler.py

import os
import pandas as pd
import json
from pathlib import Path

FILE_COLUMNS = [
    "Workout",
    "Weight Lifted (lbs)",
    "Number of Reps",
    "Date",
    "To Failure",
    "Notes"
]

WORKOUT_GROUPS_SHEET_NAME = "WorkoutGroups"

def get_default_file_path():
    """Get the default file path for storing workout data."""
    # Use user's home directory to avoid publishing to GitHub
    home_dir = Path.home()
    # Create a folder for our application data (if it doesn't exist)
    app_data_dir = home_dir / "GymTracker"
    app_data_dir.mkdir(exist_ok=True)
    # Return the path to the Excel file within this directory
    return str(app_data_dir / "progress.xlsx")

def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=FILE_COLUMNS)

    try:
        df = pd.read_excel(file_path)
        
        for column in FILE_COLUMNS:
            if column not in df.columns:
                if column == "To Failure":
                    df[column] = False  # Default to False for "To Failure" column
                else:
                    df[column] = ""  # Default to empty string for other columns

        df = df[FILE_COLUMNS]

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        df = df.dropna(how="all")

        df = df.sort_values("Date", ascending=False, na_position="last")

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Error loading '{file_path}': {e}")
        return pd.DataFrame(columns=FILE_COLUMNS)




def save_data(workout, file_path):
    df = load_data(file_path)

    new_row = pd.DataFrame([workout])

    for column in FILE_COLUMNS:
        if column not in new_row.columns:
            if column == "To Failure":
                new_row[column] = False  # Default to False for "To Failure" column
            else:
                new_row[column] = ""  # Default to empty string for other columns

    new_row = new_row[FILE_COLUMNS]

    df = pd.concat([df, new_row], ignore_index=True)

    save_dataframe(df, file_path)


def get_workouts_by_exercise(file_path, exercise):
    df = load_data(file_path)
    return df[df["Workout"] == exercise].copy()


def save_dataframe(df, file_path):
    df = df.copy()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df.to_excel(file_path, index=False)


def delete_workout(file_path, date, workout, weight, reps):
    """Delete a specific workout from the data"""
    df = load_data(file_path)
    
    # Convert date to datetime for comparison if it's not already
    if isinstance(date, str):
        try:
            import datetime
            date = pd.to_datetime(date).date()
        except:
            pass  # If conversion fails, keep original date
    
    # Find the row to delete based on all criteria
    mask = (
        (df["Date"].dt.date == date) &
        (df["Workout"] == workout) &
        (df["Weight Lifted (lbs)"] == weight) &
        (df["Number of Reps"] == reps)
    )
    
    # If we found a matching row, delete it
    if df[mask].shape[0] > 0:
        df = df[~mask]
        save_dataframe(df, file_path)
        return True
    
    return False


def get_workouts(file_path):
    return load_data(file_path)


def get_personal_record(file_path, exercise):
    df = get_workouts_by_exercise(file_path, exercise)

    if df.empty:
        return None

    return df["Weight Lifted (lbs)"].max()


def get_latest_workout(file_path, exercise):
    df = get_workouts_by_exercise(file_path, exercise)

    if df.empty:
        return None

    return df.iloc[0]


def get_statistics(file_path):
    df = load_data(file_path)

    if df.empty:
        return {
            "total_workouts": 0,
            "exercise_count": 0,
            "latest_date": None,
        }

    return {
        "total_workouts": len(df),
        "exercise_count": df["Workout"].nunique(),
        "latest_date": df["Date"].max(),
    }