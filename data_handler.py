# data_handler.py
import pandas as pd

def load_data(file_path):
    try:
        return pd.read_excel(file_path, parse_dates=['Date'])
    except FileNotFoundError:
        return pd.DataFrame(columns=['Workout', 'Weight Lifted (kg)', 'Number of Reps', 'Date'])

def save_data(data, file_path):
    df = load_data(file_path)
    new_row = pd.DataFrame([data])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    updated_df.to_excel(file_path, index=False)