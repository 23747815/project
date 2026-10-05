"""A basic tkinter interface for the Noongar Seasons Explorer."""

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

import pandas as pd


def main():
    """Build the main window and wait for the user's actions."""
    window = tk.Tk()
    window.title("Noongar Seasons Explorer")

    # A padded frame keeps the widgets away from the window edges.
    content = ttk.Frame(window, padding=24)
    content.pack(fill="both", expand=True)

    ttk.Label(
        content,
        text="Noongar Seasons Explorer",
        font=("Arial", 20, "bold"),
    ).pack(pady=(0, 12))

    ttk.Label(
        content,
        text=(
            "Explore the six Noongar seasons and their associated "
            "weather information."
        ),
        wraplength=420,
        justify="center",
    ).pack(pady=(0, 20))

    ttk.Label(content, text="Select a season:").pack(pady=(0, 6))

    # StringVar stores the current selection. Birak is the starting value.
    selected_season = tk.StringVar(value="Birak")
    season_dropdown = ttk.Combobox(
        content,
        textvariable=selected_season,
        values=("Birak", "Bunuru", "Djeran", "Makuru", "Djilba", "Kambarang"),
        state="readonly",
    )
    season_dropdown.pack(pady=(0, 16))

    # Resolve the saved CSV relative to this script, not the terminal folder.
    csv_path = (
        Path(__file__).resolve().parent
        / "outputs" / "seasons" / "daily_weather_with_seasons.csv"
    )
    results_text = tk.StringVar(value="Select a season and click Explore Season.")

    def format_measurement(value, unit):
        """Show two decimal places, or explain that a measurement is missing."""
        if pd.isna(value):
            return "Not available"
        return f"{value:.2f} {unit}"

    # These callbacks run when the corresponding buttons are clicked.
    def explore_season():
        # Clear old results so they cannot be mistaken for a failed selection.
        results_text.set("No weather summary loaded.")
        try:
            weather = pd.read_csv(csv_path)
        except FileNotFoundError:
            messagebox.showerror(
                "Weather file not found",
                f"The saved weather CSV could not be found:\n{csv_path}",
                parent=window,
            )
            return
        except (OSError, ValueError, pd.errors.ParserError) as error:
            messagebox.showerror(
                "Unable to load weather data",
                f"The weather CSV could not be loaded.\n\n{error}",
                parent=window,
            )
            return

        measurements = ["MinTemp", "MaxTemp", "Rainfall", "Sunshine"]
        required_columns = ["Season"] + measurements
        missing_columns = [name for name in required_columns if name not in weather.columns]
        if missing_columns:
            messagebox.showerror(
                "Missing weather columns",
                "The CSV is missing: " + ", ".join(missing_columns),
                parent=window,
            )
            return

        # Reuse the saved Season labels; no seasons are assigned here.
        season = selected_season.get()
        season_data = weather.loc[weather["Season"] == season].copy()
        if season_data.empty:
            results_text.set(f"No recorded days were found for {season}.")
            return

        # Conversion affects only this in-memory copy, never the CSV file.
        # Missing or non-numeric measurements are excluded from calculations.
        for column in measurements:
            season_data[column] = pd.to_numeric(season_data[column], errors="coerce")

        average_min = season_data["MinTemp"].mean()
        average_max = season_data["MaxTemp"].mean()
        # min_count=1 prevents all-missing rainfall from becoming a false zero.
        total_rainfall = season_data["Rainfall"].sum(min_count=1)
        average_sunshine = season_data["Sunshine"].mean()

        results_text.set(
            f"Season: {season}\n\n"
            f"Recorded days: {len(season_data)}\n"
            f"Average minimum temperature: {format_measurement(average_min, '°C')}\n"
            f"Average maximum temperature: {format_measurement(average_max, '°C')}\n"
            f"Total rainfall: {format_measurement(total_rainfall, 'mm')}\n"
            f"Average sunshine: {format_measurement(average_sunshine, 'hours/day')}\n\n"
            "Measurements use available values; missing values are excluded."
        )

    def show_quiz():
        messagebox.showinfo("Quiz", "Quiz coming soon!", parent=window)

    ttk.Button(content, text="Explore Season", command=explore_season).pack(
        fill="x", pady=4
    )

    # Display the selected season's summary inside the main window.
    results_frame = ttk.LabelFrame(content, text="Weather summary", padding=12)
    results_frame.pack(fill="x", pady=12)
    ttk.Label(
        results_frame,
        textvariable=results_text,
        justify="left",
        wraplength=420,
    ).pack(anchor="w")

    ttk.Button(content, text="Quiz", command=show_quiz).pack(fill="x", pady=4)
    ttk.Button(content, text="Exit", command=window.destroy).pack(fill="x", pady=4)

    season_dropdown.focus_set()
    # The event loop keeps the window open and responds to user input.
    window.mainloop()


# Launch the GUI only when this file is run directly.
if __name__ == "__main__":
    main()
