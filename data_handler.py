# data_handler.py

import os
import pandas as pd

FILE_COLUMNS = [
    "Workout",
    "Weight Lifted (kg)",
    "Number of Reps",
    "Date"
]

WORKOUT_GROUPS_COLUMNS = [
    "Group Name",
    "Exercises",
    "Weights",
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


def load_workout_groups(file_path):
    """Load workout groups from the Excel file"""
    # Check if file exists and has workout groups data
    try:
        df = pd.read_excel(file_path)
        
        # Filter for workout groups (where we have Group Name column)
        group_df = df[df['Workout'] == 'WORKOUT_GROUP']
        return group_df
        
    except Exception as e:
        print(f"Error loading workout groups: {e}")
        return pd.DataFrame(columns=WORKOUT_GROUPS_COLUMNS)


def save_workout_group(group_name, exercises, file_path):
    """Save a workout group with its exercises"""
    # First load existing data
    df = load_data(file_path)
    
    # Create group entry
    group_entry = {
        "Workout": "WORKOUT_GROUP",
        "Weight Lifted (kg)": group_name,
        "Number of Reps": str(exercises),
        "Date": pd.Timestamp.now()
    }
    
    # Add to dataframe
    new_row = pd.DataFrame([group_entry])
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Save back to file
    save_dataframe(df, file_path)


def update_workout_group_weights(group_name, new_weights, file_path):
    """Update weights for exercises in a workout group"""
    # This is a simplified implementation - in a real app you'd want more sophisticated handling
    pass


def get_all_workout_groups(file_path):
    """Get all saved workout groups"""
    try:
        df = pd.read_excel(file_path)
        
        # Filter for workout groups
        groups_df = df[df["Workout"] == "WORKOUT_GROUP"]
        
        if groups_df.empty:
            return []
            
        groups = []
        for _, row in groups_df.iterrows():
            exercises = row["Number of Reps"] if isinstance(row["Number of Reps"], str) and row["Number of Reps"] != "" else []
            # Handle case where exercises might be a string representation of a list
            if isinstance(exercises, str):
                try:
                    # Try to evaluate as Python literal (list or dict)
                    import ast
                    exercises = ast.literal_eval(exercises)
                except:
                    # If that fails, treat as single exercise
                    exercises = [exercises] if exercises else []
            elif not isinstance(exercises, list):
                exercises = [str(exercises)] if pd.notna(exercises) else []
                
            groups.append({
                "name": row["Weight Lifted (kg)"],
                "exercises": exercises,
                "date": row["Date"]
            })
        
        return groups
        
    except Exception as e:
        print(f"Error getting workout groups: {e}")
        return []


def save_data(workout, file_path):


    df = load_data(file_path)

    new_row = pd.DataFrame([workout])

    for column in FILE_COLUMNS:
        if column not in new_row.columns:
            new_row[column] = pd.NA

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


def delete_row(index, file_path):

    df = load_data(file_path)

    if index < 0 or index >= len(df):
        return False

    df = df.drop(index=index).reset_index(drop=True)

    save_dataframe(df, file_path)

    return True


def delete_workout(file_path, date, workout, weight, reps):
    """Delete a specific workout from the data"""
    df = load_data(file_path)
    
    # Find the row to delete based on all criteria
    mask = (
        (df["Date"] == date) &
        (df["Workout"] == workout) &
        (df["Weight Lifted (kg)"] == weight) &
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