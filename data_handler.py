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

    if not os.path.exists(file_path):
        return pd.DataFrame(columns=FILE_COLUMNS)

    try:
        df = pd.read_excel(file_path)

        for column in FILE_COLUMNS:
            if column not in df.columns:
                df[column] = pd.NA

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
            new_row[column] = pd.NA

    new_row = new_row[FILE_COLUMNS]

    df = pd.concat([df, new_row], ignore_index=True)

    save_dataframe(df, file_path)


def save_dataframe(df, file_path):

    df = df.copy()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df.to_excel(file_path, index=False)


def delete_row(index, file_path):

    df = load_data(file_path)

    if index < 0 or index >= len(df):
        return False

    df = df.drop(index=index).reset_index(drop=True)

    save_dataframe(df, file_path)

    return True


def get_workouts(file_path):

    return load_data(file_path)


def get_workouts_by_exercise(file_path, exercise):

    df = load_data(file_path)

    return df[df["Workout"] == exercise].copy()


def get_personal_record(file_path, exercise):

    df = get_workouts_by_exercise(file_path, exercise)

    if df.empty:
        return None

    return df["Weight Lifted (kg)"].max()


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