# data_handler.py

import os
import pandas as pd
import json

FILE_COLUMNS = [
    "Workout",
    "Weight Lifted (lbs)",
    "Number of Reps",
    "Date",
    "To Failure"
]

WORKOUT_GROUPS_SHEET_NAME = "WorkoutGroups"

def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=FILE_COLUMNS)

    try:
        df = pd.read_excel(file_path)
        
        for column in FILE_COLUMNS:
            if column not in df.columns:
                df[column] = False  # Default to False for "To Failure" column

        df = df[FILE_COLUMNS]

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        df = df.dropna(how="all")

        df = df.sort_values("Date", ascending=False, na_position="last")

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Error loading '{file_path}': {e}")
        return pd.DataFrame(columns=FILE_COLUMNS)


def save_workout_group(group_name, exercises, weights, file_path):
    """Save a workout group with its exercises and weights"""
    try:
        # Load existing groups if they exist
        groups_df = pd.DataFrame(columns=["Group Name", "Exercises", "Weights", "Date"])
        
        # Try to read the existing groups sheet
        try:
            existing_groups_df = pd.read_excel(file_path, sheet_name=WORKOUT_GROUPS_SHEET_NAME)
            groups_df = existing_groups_df
        except:
            # If no groups sheet exists, create a new one with proper columns
            pass
        
        # Create new group entry
        group_entry = {
            "Group Name": group_name,
            "Exercises": json.dumps(exercises),  # Store exercises as JSON string
            "Weights": json.dumps(weights),      # Store weights as JSON string
            "Date": pd.Timestamp.now()
        }
        
        # Add to dataframe
        new_row = pd.DataFrame([group_entry])
        groups_df = pd.concat([groups_df, new_row], ignore_index=True)
        
        # Save back to file with the groups in a separate sheet
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write workout data to main sheet (if it exists)
            try:
                df = load_data(file_path)
                if not df.empty:
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
            except:
                pass
            
            # Write groups to separate sheet
            groups_df.to_excel(writer, sheet_name=WORKOUT_GROUPS_SHEET_NAME, index=False)
            
    except Exception as e:
        print(f"Error saving workout group: {e}")


def update_workout_group_weights(group_name, new_weights, file_path):
    """Update weights for exercises in a workout group"""
    try:
        # Load existing groups
        groups = get_all_workout_groups(file_path)
        
        # Find and update the specific group
        updated_groups = []
        group_found = False
        
        for group in groups:
            if group["name"] == group_name:
                group["weights"] = new_weights
                group_found = True
            updated_groups.append(group)
            
        if not group_found:
            print(f"Group '{group_name}' not found")
            return
            
        # Save the updated groups back to file
        save_all_workout_groups(updated_groups, file_path)
        
    except Exception as e:
        print(f"Error updating workout group weights: {e}")


def get_all_workout_groups(file_path):
    """Get all saved workout groups"""
    try:
        # Try to read the workout groups sheet
        df = pd.read_excel(file_path, sheet_name=WORKOUT_GROUPS_SHEET_NAME)
        
        if df.empty:
            return []
            
        groups = []
        for _, row in df.iterrows():
            # Parse exercises and weights from JSON strings
            try:
                exercises = json.loads(row["Exercises"]) if isinstance(row["Exercises"], str) else []
                weights = json.loads(row["Weights"]) if isinstance(row["Weights"], str) else []
            except:
                exercises = []
                weights = []
                
            groups.append({
                "name": row["Group Name"],
                "exercises": exercises,
                "weights": weights,
                "date": row["Date"]
            })
        
        return groups
        
    except Exception as e:
        print(f"Error getting workout groups: {e}")
        return []


def save_all_workout_groups(groups, file_path):
    """Save all workout groups to the Excel file"""
    try:
        # Create DataFrame from groups
        if not groups:
            df = pd.DataFrame(columns=["Group Name", "Exercises", "Weights", "Date"])
        else:
            data = []
            for group in groups:
                data.append({
                    "Group Name": group["name"],
                    "Exercises": json.dumps(group["exercises"]),
                    "Weights": json.dumps(group["weights"]),
                    "Date": group["date"]
                })
            df = pd.DataFrame(data)
        
        # Save to Excel file
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            # Write groups to separate sheet
            df.to_excel(writer, sheet_name=WORKOUT_GROUPS_SHEET_NAME, index=False)
            
    except Exception as e:
        print(f"Error saving all workout groups: {e}")


def save_data(workout, file_path):
    df = load_data(file_path)

    new_row = pd.DataFrame([workout])

    for column in FILE_COLUMNS:
        if column not in new_row.columns:
            if column == "To Failure":
                new_row[column] = False  # Default to False for "To Failure" column
            else:
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