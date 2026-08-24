# ui.py

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

import data_handler
import customtkinter as ctk

# Use dynamic file path to avoid publishing to GitHub
FILE_PATH = data_handler.get_default_file_path()


class GymTrackerUI:
    def __init__(self, root):
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Light", "Dark"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

        self.root = root
        self.root.title("Gym Progress Tracker")
        self.root.geometry("1000x700")
        
        # Fix for DPI scaling issues on some systems
        try:
            self.root.wm_attributes("-zoomfactor", 1.0)
        except:
            pass  # Ignore if not supported on this system

        # Create a main scrollable frame to contain all content
        self.main_frame = ctk.CTkScrollableFrame(root, width=1000, height=700)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Load existing workouts
        self.workouts = data_handler.get_workouts(FILE_PATH)["Workout"].unique().tolist()
        self.workout_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="lbs")

        # Create all sections inside the scrollable frame
        self.create_entry_section()
        self.create_statistics_section()
        self.create_exercise_section()
        self.create_history_section()
        self.create_mutli_entry_button()
        
        # Refresh all sections to display existing data
        self.refresh_ui()
        
        # Initialize exercise section with no selection and refresh if needed
        self.exercise_combo.set("")  # Ensure it's empty initially
        
        # Also update the exercise combo box values to include current workouts
        self.exercise_combo.configure(values=self.workouts)

    def create_entry_section(self):
        entry_frame = ctk.CTkFrame(self.main_frame)
        entry_frame.pack(fill="x", padx=10, pady=10)

        # Workout
        ctk.CTkLabel(entry_frame, text="Workout:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Create a combobox with existing workouts for selection, with ability to type new ones
        self.workout_combo = ctk.CTkComboBox(
            entry_frame,
            values=self.workouts,
            state="normal",  # Allow both selection and typing
            width=300
        )
        self.workout_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Weight
        ctk.CTkLabel(entry_frame, text="Weight:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.weight_entry = ctk.CTkEntry(entry_frame)
        self.weight_entry.grid(row=1, column=1, padx=5, pady=5)

        self.unit_combo = ctk.CTkComboBox(
            entry_frame,
            values=["kg", "lbs"],
            width=60,
            state="readonly"
        )
        self.unit_combo.set("lbs")  # Set default value
        self.unit_combo.grid(row=1, column=2, padx=5)

        # Reps
        ctk.CTkLabel(entry_frame, text="Reps:").grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.reps_entry = ctk.CTkEntry(entry_frame)
        self.reps_entry.grid(row=2, column=1, padx=5, pady=5)

        # Date
        ctk.CTkLabel(entry_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.date_entry = ctk.CTkEntry(entry_frame)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkButton(
            entry_frame,
            text="Set Current Date",
            command=self.set_current_date
        ).grid(row=3, column=2, padx=5, pady=5)

        # To Failure Checkbox
        self.to_failure_var = tk.BooleanVar()
        ctk.CTkCheckBox(
            entry_frame,
            text="To Failure",
            variable=self.to_failure_var
        ).grid(row=4, column=0, columnspan=3, pady=5, sticky="w")

        # Notes field
        ctk.CTkLabel(entry_frame, text="Notes (max 300 chars):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        
        self.notes_text = ctk.CTkTextbox(entry_frame, height=80, width=400)
        self.notes_text.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Add character counter
        self.notes_char_count = ctk.CTkLabel(entry_frame, text="0/300")
        self.notes_char_count.grid(row=6, column=1, padx=5, pady=2, sticky="w")
        
        # Bind event to update character count
        self.notes_text.bind('<KeyRelease>', self.update_notes_char_count)

        ctk.CTkButton(
            entry_frame,
            text="Submit Workout",
            command=self.submit_workout
        ).grid(row=7, column=0, columnspan=3, pady=10)
        
        # Add View Raw Data button
        ctk.CTkButton(
            entry_frame,
            text="View Raw Data",
            command=self.view_raw_data
        ).grid(row=8, column=0, columnspan=3, pady=10)

    def set_current_date(self):
        from datetime import date
        today = date.today()
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today.strftime("%Y-%m-%d"))

    def update_notes_char_count(self, event=None):
        """Update the character count for the notes field."""
        current_length = len(self.notes_text.get("1.0", "end-1c"))
        self.notes_char_count.configure(text=f"{current_length}/300")
        
        # If we exceed 300 characters, truncate the text
        if current_length > 300:
            # Get the text and limit it to 300 characters
            text = self.notes_text.get("1.0", "end-1c")
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", text[:300])
            # Update the character count again after truncation
            self.notes_char_count.config(text="300/300")

    def create_statistics_section(self):
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)

        self.total_workouts_label = ctk.CTkLabel(
            stats_frame,
            text="Total Workouts: 0"
        )
        self.total_workouts_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.exercise_count_label = ctk.CTkLabel(
            stats_frame,
            text="Exercises Tracked: 0"
        )
        self.exercise_count_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.latest_date_label = ctk.CTkLabel(
            stats_frame,
            text="Latest Workout: N/A"
        )
        self.latest_date_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

    def create_exercise_section(self):
        exercise_frame = ctk.CTkFrame(self.main_frame)
        exercise_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(exercise_frame, text="Exercise:").grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="w"
        )

        self.exercise_combo = ctk.CTkComboBox(
            exercise_frame,
            values=self.workouts,
            state="readonly"
        )
        
        # Set to empty string initially - no selection
        self.exercise_combo.set("")
        self.exercise_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Bind event to refresh exercise info when selection changes
        self.exercise_combo.bind('<<ComboboxSelected>>', self.on_exercise_select)

        self.pr_label = ctk.CTkLabel(
            exercise_frame,
            text="Personal Record: N/A"
        )
        self.pr_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

        self.latest_workout_label = ctk.CTkLabel(
            exercise_frame,
            text="Latest Workout: N/A"
        )
        self.latest_workout_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5)

        ctk.CTkButton(
            exercise_frame,
            text="Show Progress Graph",
            command=self.show_progress_graph
        ).grid(row=3, column=0, pady=10)

        self.graph_frame = ctk.CTkFrame(exercise_frame)
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

    def create_mutli_entry_button(self):
        ctk.CTkButton(
            self.main_frame,
            text="Add Multiple Workouts",
            command=self.open_multi_entry_window
        ).pack(pady=10)


    def create_history_section(self):
        history_frame = ctk.CTkFrame(self.main_frame)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = (
            "Date",
            "Workout",
            "Weight Lifted (lbs)",
            "Number of Reps"
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

        ctk.CTkButton(
            history_frame,
            text="Delete Selected Workout",
            command=self.delete_selected_workout
        ).pack(pady=10)

    def refresh_ui(self):
        self.refresh_statistics()
        # Only refresh exercise info if an exercise is selected
        if self.exercise_combo.get():
            self.refresh_exercise_info()
        self.refresh_history()

    def refresh_statistics(self):
        stats = data_handler.get_statistics(FILE_PATH)

        self.total_workouts_label.configure(
            text=f"Total Workouts: {stats['total_workouts']}"
        )

        self.exercise_count_label.configure(
            text=f"Exercises Tracked: {stats['exercise_count']}"
        )

        latest_date = stats["latest_date"]

        if latest_date is None or pd.isna(latest_date):
            latest_text = "N/A"
        else:
            latest_text = latest_date.strftime("%Y-%m-%d")

        self.latest_date_label.configure(
            text=f"Latest Workout: {latest_text}"
        )

    def refresh_exercise_info(self):
        exercise = self.exercise_combo.get()

        if not exercise:
            # Clear the labels when no exercise is selected
            self.pr_label.configure(
                text="Personal Record: N/A"
            )
            self.latest_workout_label.configure(
                text="Latest Workout: N/A"
            )
            return

        try:
            df = data_handler.load_data(FILE_PATH)

            if df.empty:
                self.pr_label.configure(
                    text="Personal Record: N/A"
                )

                self.latest_workout_label.configure(
                    text="Latest Workout: N/A"
                )
                return

            exercise_data = df[df["Workout"] == exercise]

            if exercise_data.empty:
                self.pr_label.configure(
                    text="Personal Record: N/A"
                )

                self.latest_workout_label.configure(
                    text="Latest Workout: N/A"
                )
                return

            # Check if the column exists
            if "Weight Lifted (lbs)" not in df.columns:
                print("Column 'Weight Lifted (lbs)' not found in DataFrame")
                self.pr_label.configure(
                    text="Personal Record: N/A"
                )

                self.latest_workout_label.configure(
                    text="Latest Workout: N/A"
                )
                return

            max_weight = exercise_data["Weight Lifted (lbs)"].max()

            self.pr_label.configure(
                text=f"Personal Record: {max_weight}"
            )

            latest = exercise_data.sort_values(
                by="Date",
                ascending=False
            ).iloc[0]

            # Ensure all columns exist before accessing them
            if "Weight Lifted (lbs)" not in latest or "Number of Reps" not in latest or "Date" not in latest:
                print("Missing expected columns in latest workout data")
                self.latest_workout_label.configure(
                    text="Latest Workout: N/A"
                )
                return

            self.latest_workout_label.configure(
                text=(
                    f"Latest Workout: "
                    f"{latest['Weight Lifted (lbs)']} x {latest['Number of Reps']} "
                    f"({latest['Date']})"
                )
            )

        except Exception as e:
            print(f"Error refreshing exercise info: {e}")
            import traceback
            traceback.print_exc()

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
                        row["Weight Lifted (lbs)"],
                        row["Number of Reps"]
                    )
                )

        except Exception as e:
            # Don't show the error in UI since we handle it gracefully
            pass

        

    def submit_workout(self):
        workout = self.workout_combo.get().strip()
        weight = self.weight_entry.get()
        reps = self.reps_entry.get()
        date = self.date_entry.get()
        unit = self.unit_var.get()

        if not workout or not weight or not reps or not date:
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

        # Get notes from the text widget
        notes = self.notes_text.get("1.0", "end-1c")
        
        data_handler.save_data(
            {
                "Workout": workout,
                "Weight Lifted (lbs)": weight,
                "Number of Reps": reps,
                "Date": date,
                "To Failure": self.to_failure_var.get(),
                "Notes": notes
            },
            FILE_PATH
        )

        messagebox.showinfo(
            "Success",
            "Workout added!"
        )

        # Update the workouts list with new workout if it's not already there
        if workout not in self.workouts:
            self.workouts.append(workout)
            self.workout_combo.configure(values=self.workouts)
            
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

        # Get the full item data including the index
        item_data = self.history_tree.item(selected[0])
        values = item_data["values"]

        # Verify we have the expected number of values
        if len(values) < 4:
            messagebox.showerror(
                "Data Error",
                "Unable to delete workout: Invalid data format."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {values[1]} workout from {values[0]}?"
        )

        if confirm:
            try:
                # Ensure proper data types for deletion
                date_val = values[0]
                workout_val = values[1] 
                weight_val = float(values[2])  # Convert to float for comparison
                reps_val = int(values[3])      # Convert to int for comparison
                
                data_handler.delete_workout(
                    FILE_PATH,
                    date_val,
                    workout_val,
                    weight_val,
                    reps_val
                )

                self.refresh_ui()
            except Exception as e:
                messagebox.showerror(
                    "Delete Error",
                    f"Failed to delete workout: {str(e)}"
                )
                print(f"Error deleting workout: {e}")

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

            # Plot points with different colors based on "To Failure" status
            # First, we'll plot the connecting lines between points
            dates = df["Date"]
            weights = df["Weight Lifted (lbs)"]
            
            # Plot lines connecting all points
            ax.plot(dates, weights, color='gray', linestyle='-', linewidth=1, alpha=0.7)
            
            # Then plot the individual points on top
            for i, row in df.iterrows():
                color = 'red' if row['To Failure'] else 'blue'
                ax.plot(row["Date"], row["Weight Lifted (lbs)"], marker="o", color=color, markersize=8)

            # Add legend for the colors
            from matplotlib.patches import Patch
            legend_elements = [Patch(color='blue', label='Normal'),
                               Patch(color='red', label='To Failure')]
            ax.legend(handles=legend_elements)

            ax.set_title(
                f"{exercise} Progress"
            )

            ax.set_xlabel(
                "Date"
            )

            ax.set_ylabel(
                "Weight Lifted (lbs)"
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
        # Clear the workout combobox (which also clears the entry part)
        self.workout_combo.set('')
        
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
        
    def on_exercise_select(self, event):
        # This method is called when an exercise is selected
        self.refresh_exercise_info()
        
    def view_raw_data(self):
        """Open the Excel file containing the workout data."""
        import subprocess
        import os
        
        try:
            # Try to open the Excel file with the default application
            if os.name == 'nt':  # Windows
                os.startfile(FILE_PATH)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.run(['open', FILE_PATH])  # macOS
            else:
                subprocess.run(['xdg-open', FILE_PATH])  # Linux
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not open the file: {str(e)}"
            )

    def open_multi_entry_window(self):
        """Open a new window for adding multiple workouts at once."""
        multi_entry_window = ctk.CTkToplevel(self.root)
        multi_entry_window.title("Add Multiple Workouts")
        multi_entry_window.geometry("600x400")

        # Instructions
        ctk.CTkLabel(
            multi_entry_window,
            text="Enter workouts in the following format (one per line):\n"
                 "Workout, Weight, Reps, Date (YYYY-MM-DD), To Failure (True/False), Notes"
        ).pack(pady=10)

        # Textbox for multiple entries
        self.multi_entry_text = ctk.CTkTextbox(multi_entry_window, height=200, width=550)
        self.multi_entry_text.pack(pady=10)

        # Submit button
        ctk.CTkButton(
            multi_entry_window,
            text="Submit Workouts",
            command=self.submit_multiple_workouts
        ).pack(pady=10)


def create_app():
    root = ctk.CTk()

    GymTrackerUI(root)

    return root


if __name__ == "__main__":
    app = create_app()
    app.mainloop()