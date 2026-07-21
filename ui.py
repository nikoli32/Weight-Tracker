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



        self.workouts = [
            "Arnold Press",
            "Barbell Bench Press",
            "Barbell Row",
            "Barbell Squat",
            "Barbell Romanian Deadlift",
            "Bicep Curl Machine",
            "Cable Chest Fly",
            "Cable Crossover",
            "Cable Curl",
            "Cable Lateral Raise",
            "Cable Row",
            "Chest Press Machine",
            "Deadlift",
            "Decline Bench Press",
            "Dumbbell Bench Press",
            "Dumbbell Row",
            "Dumbbell Shoulder Press",
            "Face Pull",
            "Front Squat",
            "Hammer Curl",
            "Hack Squat Machine",
            "Hamstring Curl Machine",
            "Incline Bench Press",
            "Incline Dumbbell Press",
            "Lat Pulldown",
            "Leg Extension Machine",
            "Leg Press Machine",
            "Leg Curl Machine",
            "Lying Leg Curl Machine",
            "Overhead Press",
            "Overhead Tricep Extension",
            "Pec Deck Machine",
            "Preacher Curl Machine",
            "Rear Delt Fly Machine",
            "Romanian Deadlift",
            "Seated Cable Row",
            "Seated Shoulder Press Machine",
            "Shrug Machine",
            "Smith Machine Bench Press",
            "Smith Machine Squat",
            "Tricep Pushdown",
            "Upright Row",
        ]

        self.workout_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="kg")



        self.create_entry_section()
        self.create_statistics_section()
        self.create_exercise_section()
        self.create_history_section()

        # Load data into interface
        self.refresh_ui()



    def create_entry_section(self):

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

        ttk.Label(entry_frame, text="Weight:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.weight_entry = ttk.Entry(entry_frame)
        self.weight_entry.grid(row=1, column=1, padx=5, pady=5)

        self.unit_combo = ttk.Combobox(
            entry_frame,
            textvariable=self.unit_var,
            values=["kg", "lbs"],
            width=6,
            state="readonly"
        )
        self.unit_combo.grid(row=1, column=2, padx=5)

        ttk.Label(entry_frame, text="Reps:").grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.reps_entry = ttk.Entry(entry_frame)
        self.reps_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.date_entry = ttk.Entry(entry_frame)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(
            entry_frame,
            text="Submit Workout",
            command=self.submit_workout
        ).grid(row=4, column=0, columnspan=3, pady=10)


    def create_statistics_section(self):

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

        exercise_frame = ttk.LabelFrame(self.root, text="Exercise Details")
        exercise_frame.pack(fill="both", expand=True, padx=10, pady=10)

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

        self.pr_label = ttk.Label(
            exercise_frame,
            text="Personal Record: N/A"
        )
        self.pr_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

        self.latest_workout_label = ttk.Label(
            exercise_frame,
            text="Latest Workout: N/A"
        )
        self.latest_workout_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5)

        ttk.Button(
            exercise_frame,
            text="Show Progress Graph",
            command=self.show_progress_graph
        ).grid(row=3, column=0, pady=10)

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

        for column in columns:
            self.history_tree.heading(column, text=column)
            self.history_tree.column(column, anchor="center")

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

            exercise_data = df[df["Workout"] == exercise]

            if exercise_data.empty:
                self.pr_label.config(
                    text="Personal Record: N/A"
                )

                self.latest_workout_label.config(
                    text="Latest Workout: N/A"
                )
                return

            max_weight = exercise_data["Weight Lifted (kg)"].max()

            self.pr_label.config(
                text=f"Personal Record: {max_weight}"
            )

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
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        try:
            df = data_handler.load_data(FILE_PATH)

            if df.empty:
                return

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

    def submit_workout(self):
        workout = self.workout_var.get()
        weight = self.weight_entry.get()
        reps = self.reps_entry.get()
        date = self.date_entry.get()
        unit = self.unit_var.get()

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