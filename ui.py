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

    def refresh_exercise_info(self):
        exercise = self.exercise_combo.get()

        if not exercise:
            return

        try:
            df = data_handler.load_data(FILE_PATH)

            if df.empty:
                self.pr_label.config(
                    text="Personal Record: N/A"
                )

                self.latest_workout_label.config(
                    text="Latest Workout: N/A"
                )
                return

            # Filter selected exercise
            exercise_data = df[df["Workout"] == exercise]

            if exercise_data.empty:
                self.pr_label.config(
                    text="Personal Record: N/A"
                )

                self.latest_workout_label.config(
                    text="Latest Workout: N/A"
                )
                return

            # Personal record
            max_weight = exercise_data["Weight Lifted (kg)"].max()

            self.pr_label.config(
                text=f"Personal Record: {max_weight}"
            )

            # Latest workout
            latest = exercise_data.sort_values(
                by="Date",
                ascending=False
            ).iloc[0]

            self.latest_workout_label.config(
                text=(
                    f"Latest Workout: "
                    f"{latest['Weight']} x {latest['Reps']} "
                    f"({latest['Date']})"
                )
            )

        except Exception as e:
            print(f"Error refreshing exercise info: {e}")



    def refresh_history(self):
        # Clear existing rows
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        try:
            df = data_handler.load_data(FILE_PATH)

            if df.empty:
                return

            # Sort newest first
            df = df.sort_values(
                by="Date",
                ascending=False
            )

            for _, row in df.iterrows():

                self.history_tree.insert(
                    "",
                    "end",
                    values=(
                        row["Date"],
                        row["Workout"],
                        row["Weight Lifted (kg)"],
                        row["Number of reps"]
                    )
                )

        except Exception as e:
            print(f"Error refreshing history: {e}")

    #################################################
    # Workout Actions
    #################################################

    def submit_workout(self):
        workout = self.workout_var.get()
        weight = self.weight_entry.get()
        reps = self.reps_entry.get()
        date = self.date_entry.get()
        unit = self.unit_var.get()

        # Validation
        if not weight or not reps or not date:
            messagebox.showerror(
                "Missing Information",
                "Please fill out all fields."
            )
            return

        try:
            weight = float(weight)
            reps = int(reps)

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Weight must be a number and reps must be an integer."
            )
            return


        # Save workout
        data_handler.save_data(
            {
                "Workout": workout,
                "Weight Lifted (kg)": weight,
                "Number of reps": reps,
                "Date": date
            },
            FILE_PATH
        )


        messagebox.showinfo(
            "Success",
            "Workout added!"
        )

        self.clear_inputs()
        self.refresh_ui()

    def delete_selected_workout(self):
        selected = self.history_tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a workout to delete."
            )
            return


        values = self.history_tree.item(
            selected[0],
            "values"
        )


        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {values[1]} workout from {values[0]}?"
        )


        if confirm:

            data_handler.delete_workout(
                FILE_PATH,
                values[0],
                values[1],
                values[2],
                values[3]
            )

            self.refresh_ui()


    def show_progress_graph(self):
        """
        Draws progress graph for selected exercise.
        """

        exercise = self.exercise_combo.get()

        if not exercise:
            return


        try:

            df = data_handler.load_data(FILE_PATH)

            df = df[df["Workout"] == exercise]


            if df.empty:
                messagebox.showinfo(
                    "No Data",
                    "No workouts recorded for this exercise."
                )
                return


            df = df.sort_values(
                by="Date"
            )


            # Remove old graph
            for widget in self.graph_frame.winfo_children():
                widget.destroy()


            fig, ax = plt.subplots(
                figsize=(6,3)
            )


            ax.plot(
                df["Date"],
                df["Weight Lifted (kg)"],
                marker="o"
            )


            ax.set_title(
                f"{exercise} Progress"
            )

            ax.set_xlabel(
                "Date"
            )

            ax.set_ylabel(
                "Weight Lifted (kg)"
            )


            plt.xticks(
                rotation=45
            )

            fig.tight_layout()


            canvas = FigureCanvasTkAgg(
                fig,
                master=self.graph_frame
            )

            canvas.draw()

            canvas.get_tk_widget().pack(
                fill="both",
                expand=True
            )


        except Exception as e:
            print(f"Graph error: {e}")


    def clear_inputs(self):
        """
        Clears input fields after submission.
        """

        self.weight_entry.delete(
            0,
            tk.END
        )

        self.reps_entry.delete(
            0,
            tk.END
        )

        self.date_entry.delete(
            0,
            tk.END
        )

        self.workout_combo.current(0)
        self.unit_combo.current(0)


def create_app():
    root = tk.Tk()

    GymTrackerUI(root)

    return root


if __name__ == "__main__":
    app = create_app()
    app.mainloop()