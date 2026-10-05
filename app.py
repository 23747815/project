"""A basic tkinter interface for the Noongar Seasons Explorer."""

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

import pandas as pd
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


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

    def clear_graph(message):
        """Remove the previous season's lines and show a helpful title."""
        temperature_axes.clear()
        temperature_axes.set_title(message)
        temperature_axes.set_xlabel("Date")
        temperature_axes.set_ylabel("Temperature (°C)")
        graph_canvas.draw_idle()

    def update_graph(season_data, season):
        """Plot the same saved-season records used by the weather summary."""
        clear_graph(f"{season}: daily temperatures")
        # Parse and sort dates in a copy; the saved CSV stays unchanged.
        graph_data = season_data.copy()
        graph_data["Date"] = pd.to_datetime(graph_data["Date"], errors="coerce")
        graph_data = graph_data.dropna(subset=["Date"]).sort_values("Date")
        if graph_data.empty or not graph_data[["MinTemp", "MaxTemp"]].notna().any().any():
            clear_graph(f"No temperature data to plot for {season}.")
            return

        # Missing temperatures remain gaps rather than being filled with zero.
        temperature_axes.plot(
            graph_data["Date"], graph_data["MinTemp"],
            label="Minimum temperature", color="tab:blue", marker=".",
        )
        temperature_axes.plot(
            graph_data["Date"], graph_data["MaxTemp"],
            label="Maximum temperature", color="tab:red", marker=".",
        )
        date_ticks = mdates.AutoDateLocator(minticks=3, maxticks=6)
        temperature_axes.xaxis.set_major_locator(date_ticks)
        temperature_axes.xaxis.set_major_formatter(mdates.ConciseDateFormatter(date_ticks))
        temperature_axes.legend(fontsize="small")
        temperature_axes.grid(True, alpha=0.3)
        # Redraw the existing embedded canvas instead of opening a window.
        graph_canvas.draw_idle()

    # These callbacks run when the corresponding buttons are clicked.
    def explore_season():
        # Clear old results so they cannot be mistaken for a failed selection.
        results_text.set("No weather summary loaded.")
        clear_graph("No weather graph loaded.")
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
        required_columns = ["Date", "Season"] + measurements
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
            clear_graph(f"No recorded days for {season}.")
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
        update_graph(season_data, season)

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

    # Create one figure and embed its canvas as a normal Tkinter widget.
    # Each Explore click reuses this figure, so graphs do not accumulate.
    graph_frame = ttk.Frame(content)
    graph_frame.pack(fill="both", expand=True, pady=(0, 8))
    temperature_figure = Figure(figsize=(5, 2.5), dpi=100, layout="constrained")
    temperature_axes = temperature_figure.add_subplot(111)
    graph_canvas = FigureCanvasTkAgg(temperature_figure, master=graph_frame)
    graph_canvas.get_tk_widget().pack(fill="both", expand=True)
    clear_graph("Select a season to view daily temperatures.")

    ttk.Button(content, text="Quiz", command=show_quiz).pack(fill="x", pady=4)
    ttk.Button(content, text="Exit", command=window.destroy).pack(fill="x", pady=4)

    season_dropdown.focus_set()
    # The event loop keeps the window open and responds to user input.
    window.mainloop()


# Launch the GUI only when this file is run directly.
if __name__ == "__main__":
    main()
