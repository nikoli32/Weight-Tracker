# data_handler.py

import os
import pandas as pd

FILE_COLUMNS = [
    "Workout",
    "Weight Lifted (kg)",
    "Number of Reps",
    "Date"
]


def load_data(file_path):
    """
    Loads workout data from an Excel file.
    If the file doesn't exist or is invalid, returns an empty DataFrame.
    """

    if not os.path.exists(file_path):
        return pd.DataFrame(columns=FILE_COLUMNS)

    try:
        df = pd.read_excel(file_path)

        # Ensure every expected column exists
        for column in FILE_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA

        df = df[FILE_COLUMNS]

        # Convert Date column safely
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Sort newest first
        df = df.sort_values("Date", ascending=False, na_position="last")

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Error loading '{file_path}': {e}")
        return pd.DataFrame(columns=FILE_COLUMNS)


def save_data(workout, file_path):
    """
    Appends a workout to the workbook.
    """

    df = load_data(file_path)

    new_row = pd.DataFrame([workout])

    # Make sure all columns exist
    for column in FILE_COLUMNS:
        if column not in new_row.columns:
            new_row[column] = pd.NA

    new_row = new_row[FILE_COLUMNS]

    df = pd.concat([df, new_row], ignore_index=True)

    save_dataframe(df, file_path)


def save_dataframe(df, file_path):
    """
    Saves an entire DataFrame back to Excel.
    """

    df = df.copy()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df.to_excel(file_path, index=False)


def delete_row(index, file_path):
    """
    Deletes a workout by DataFrame index.
    """

    df = load_data(file_path)

    if index < 0 or index >= len(df):
        return False

    df = df.drop(index=index).reset_index(drop=True)

    save_dataframe(df, file_path)

    return True


def get_workouts(file_path):
    """
    Returns all workouts.
    """

    return load_data(file_path)


def get_workouts_by_exercise(file_path, exercise):
    """
    Returns only workouts for a specific exercise.
    """

    df = load_data(file_path)

    return df[df["Workout"] == exercise].copy()


def get_personal_record(file_path, exercise):
    """
    Returns the heaviest weight lifted for an exercise.
    """

    df = get_workouts_by_exercise(file_path, exercise)

    if df.empty:
        return None

    return df["Weight Lifted (kg)"].max()


def get_latest_workout(file_path, exercise):
    """
    Returns the most recent workout for an exercise.
    """

    df = get_workouts_by_exercise(file_path, exercise)

    if df.empty:
        return None

    return df.iloc[0]


def get_statistics(file_path):
    """
    Returns basic statistics used by the UI.
    """

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