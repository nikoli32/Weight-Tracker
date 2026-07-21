# ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

import data_handler

FILE_PATH = "progress.xlsx"


class GymTrackerUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Gym Progress Tracker")
        self.root.geometry("1000x700")

        # ----------------------------
        # Variables
        # ----------------------------

        self.workouts = [
            "Squats",
            "Bench Press",
            "Deadlifts",
            "Overhead Press",
            "Barbell Rows",
            "Chest Flyes",
            "Leg Curls",
            "Hammer Curls",
            "Tricep Dips",
            "Lunges",
            "Plank",
            "Russian Twists"
        ]

        self.workout_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="kg")

        # ----------------------------
        # Build UI
        # ----------------------------

        self.create_entry_section()
        self.create_statistics_section()
        self.create_exercise_section()
        self.create_history_section()

        # Load data into interface
        self.refresh_ui()

    #################################################
    # UI Creation
    #################################################

    def create_entry_section(self):
        """
        Creates the workout entry form.
        """

        entry_frame = ttk.LabelFrame(self.root, text="Add Workout")
        entry_frame.pack(fill="x", padx=10, pady=10)

        # Workout
        ttk.Label(entry_frame, text="Workout:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.workout_combo = ttk.Combobox(
            entry_frame,
            textvariable=self.workout_var,
            values=self.workouts,
            state="readonly"
        )
        self.workout_combo.current(0)
        self.workout_combo.grid(row=0, column=1, padx=5, pady=5)

        # Weight
        ttk.Label(entry_frame, text="Weight:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.weight_entry = ttk.Entry(entry_frame)
        self.weight_entry.grid(row=1, column=1, padx=5, pady=5)

        # Unit
        self.unit_combo = ttk.Combobox(
            entry_frame,
            textvariable=self.unit_var,
            values=["kg", "lbs"],
            width=6,
            state="readonly"
        )
        self.unit_combo.grid(row=1, column=2, padx=5)

        # Reps
        ttk.Label(entry_frame, text="Reps:").grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.reps_entry = ttk.Entry(entry_frame)
        self.reps_entry.grid(row=2, column=1, padx=5, pady=5)

        # Date
        ttk.Label(entry_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.date_entry = ttk.Entry(entry_frame)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        # Submit button
        ttk.Button(
            entry_frame,
            text="Submit Workout",
            command=self.submit_workout
        ).grid(row=4, column=0, columnspan=3, pady=10)


    def create_statistics_section(self):
        """
        Displays overall workout statistics.
        """

        stats_frame = ttk.LabelFrame(self.root, text="Statistics")
        stats_frame.pack(fill="x", padx=10, pady=10)

        self.total_workouts_label = ttk.Label(
            stats_frame,
            text="Total Workouts: 0"
        )
        self.total_workouts_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.exercise_count_label = ttk.Label(
            stats_frame,
            text="Exercises Tracked: 0"
        )
        self.exercise_count_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.latest_date_label = ttk.Label(
            stats_frame,
            text="Latest Workout: N/A"
        )
        self.latest_date_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")


    def create_exercise_section(self):
        """
        Displays exercise-specific information.
        """

        exercise_frame = ttk.LabelFrame(self.root, text="Exercise Details")
        exercise_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Exercise selector
        ttk.Label(exercise_frame, text="Exercise:").grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.exercise_combo = ttk.Combobox(
            exercise_frame,
            values=self.workouts,
            state="readonly"
        )

        self.exercise_combo.current(0)
        self.exercise_combo.grid(row=0, column=1, padx=5, pady=5)

        # Personal Record
        self.pr_label = ttk.Label(
            exercise_frame,
            text="Personal Record: N/A"
        )
        self.pr_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

        # Latest Workout
        self.latest_workout_label = ttk.Label(
            exercise_frame,
            text="Latest Workout: N/A"
        )
        self.latest_workout_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5)

        # Graph button
        ttk.Button(
            exercise_frame,
            text="Show Progress Graph",
            command=self.show_progress_graph
        ).grid(row=3, column=0, pady=10)

        # Graph area (placeholder)
        self.graph_frame = ttk.Frame(exercise_frame)
        self.graph_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=10,
            pady=10
        )

        exercise_frame.columnconfigure(2, weight=1)
        exercise_frame.rowconfigure(4, weight=1)




    def create_history_section(self):
        """
        Displays workout history in a Treeview.
        """

        history_frame = ttk.LabelFrame(self.root, text="Workout History")
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = (
            "Date",
            "Workout",
            "Weight",
            "Reps"
        )

        self.history_tree = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            height=12
        )

        # Column headings
        for column in columns:
            self.history_tree.heading(column, text=column)
            self.history_tree.column(column, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            history_frame,
            orient="vertical",
            command=self.history_tree.yview
        )

        self.history_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.history_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Delete button
        ttk.Button(
            history_frame,
            text="Delete Selected Workout",
            command=self.delete_selected_workout
        ).pack(pady=10)




    def refresh_ui(self):
        self.refresh_statistics()
        self.refresh_exercise_info()
        self.refresh_history()




    def refresh_statistics(self):
        """
        Updates statistics labels.
        """
        pass

    def refresh_statistics(self):
        stats = data_handler.get_statistics(FILE_PATH)

        self.total_workouts_label.config(
            text=f"Total Workouts: {stats['total_workouts']}"
        )

        self.exercise_count_label.config(
            text=f"Exercises Tracked: {stats['exercise_count']}"
        )

        latest_date = stats["latest_date"]

        if latest_date is None or pd.isna(latest_date):
            latest_text = "N/A"
        else:
            latest_text = latest_date.strftime("%Y-%m-%d")

        self.latest_date_label.config(
            text=f"Latest Workout: {latest_text}"
        )




    def refresh_history(self):
        """
        Reloads workout history into Treeview.
        """
        pass

    #################################################
    # Workout Actions
    #################################################

    def submit_workout(self):
        """
        Validates input and saves a workout.
        """
        pass

    def delete_selected_workout(self):
        """
        Deletes the selected workout.
        """
        pass

    #################################################
    # Graph
    #################################################

    def show_progress_graph(self):
        """
        Draws progress graph for selected exercise.
        """
        pass

    #################################################
    # Utility
    #################################################

    def clear_inputs(self):
        """
        Clears input fields after submission.
        """
        pass


#################################################
# Main
#################################################

def create_app():
    root = tk.Tk()

    GymTrackerUI(root)

    return root


if __name__ == "__main__":
    app = create_app()
    app.mainloop()