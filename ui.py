# ui.py
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import data_handler
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_app():
    app = tk.Tk()
    app.title("Gym Progress Tracker")
    
    # Data entry fields
    workout_label = tk.Label(app, text="Workout:")
    workout_label.pack(pady=5)
    
    workouts = [
        "Squats", "Bench Press", "Deadlifts", "Overhead Press",
        "Barbell Rows", "Chest Flyes", "Leg Curls", "Hammer Curls",
        "Tricep Dips", "Lunges", "Plank", "Russian Twists"
    ]
    
    workout_var = tk.StringVar(app)
    workout_var.set(workouts[0])
    workout_menu = ttk.Combobox(app, textvariable=workout_var, values=workouts)
    workout_menu.pack(pady=5)
    
    weight_label = tk.Label(app, text="Weight Lifted:")
    weight_label.pack(pady=5)
    
    weight_entry = tk.Entry(app)
    weight_entry.pack(pady=5)
    
    unit_var = tk.StringVar(app)
    unit_var.set("kg")
    unit_menu = ttk.Combobox(app, textvariable=unit_var, values=["kg", "lbs"])
    unit_menu.pack(pady=5)
    
    reps_label = tk.Label(app, text="Number of Reps:")
    reps_label.pack(pady=5)
    
    reps_entry = tk.Entry(app)
    reps_entry.pack(pady=5)
    
    date_label = tk.Label(app, text="Date (YYYY-MM-DD):")
    date_label.pack(pady=5)
    
    date_entry = tk.Entry(app)
    date_entry.pack(pady=5)
    
    def on_submit():
        workout = workout_var.get()
        weight = weight_entry.get()
        unit = unit_var.get()
        reps = reps_entry.get()
        date = date_entry.get()
        
        if not workout or not weight or not reps or not date:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        try:
            weight = float(weight)
            reps = int(reps)
            pd.to_datetime(date)  # Validate date format
        except ValueError:
            messagebox.showerror("Value Error", "Weight must be a number, Reps must be an integer, and Date must be in YYYY-MM-DD format.")
            return
        
        # Convert weight if necessary
        if unit == "lbs":
            weight = weight * 0.45359237  # Convert lbs to kg
        
        data_handler.save_data({
            'Workout': workout,
            'Weight Lifted (kg)': weight,
            'Number of Reps': reps,
            'Date': date
        }, 'progress.xlsx')
        
        messagebox.showinfo("Submitted", "Data submitted successfully!")
    
    submit_button = tk.Button(app, text="Submit Data", command=on_submit)
    submit_button.pack(pady=10)
    return app