"""A basic tkinter interface for the Noongar Seasons Explorer."""

import tkinter as tk
import webbrowser
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

    # Display only the supplied descriptions; these do not classify weather data.
    season_descriptions = {
        "Birak": "December–January. Warming weather and easing rain. Morning easterlies can give way to afternoon south-westerlies.",
        "Bunuru": "February–March. Intense heat, little rain, and coastal afternoon breezes.",
        "Djeran": "April–May. Relief from heat, cooler damp mornings, and gentler winds.",
        "Makuru": "June–July. Cold, wet conditions, with winds from the west/south.",
        "Djilba": "August–September. A transition period with a mixture of cold, clear, wet, windy and warmer days.",
        "Kambarang": "October–November. Warming weather and longer dry intervals.",
    }
    description_text = tk.StringVar(value="Select a season and click Explore Season.")

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
        # Update the description on every click, even if weather data is unavailable.
        description_text.set(season_descriptions[selected_season.get()])
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
        """Open an independent quiz without changing the main window."""
        # Each question stores its text, four choices and the correct choice.
        questions = [
            (
                "Which season is associated with December-January?",
                ("Bunuru", "Birak", "Makuru", "Kambarang"),
                "Birak",
            ),
            (
                "Which season has intense heat, little rain and coastal afternoon breezes?",
                ("Djeran", "Djilba", "Bunuru", "Makuru"),
                "Bunuru",
            ),
            (
                "Which season brings relief from heat, cooler damp mornings and gentler winds?",
                ("Djeran", "Birak", "Kambarang", "Djilba"),
                "Djeran",
            ),
            (
                "Which season is cold and wet, with winds from the west or south?",
                ("Kambarang", "Bunuru", "Birak", "Makuru"),
                "Makuru",
            ),
            (
                "Which season is a transition with a mixture of cold, clear, wet, windy and warmer days?",
                ("Makuru", "Kambarang", "Djilba", "Djeran"),
                "Djilba",
            ),
        ]

        # Toplevel shares the existing event loop; the main app stays usable.
        quiz_window = tk.Toplevel(window)
        quiz_window.title("Noongar Seasons Quiz")
        quiz_content = ttk.Frame(quiz_window, padding=24)
        quiz_content.pack(fill="both", expand=True)

        question_index = 0
        score = 0
        answered = False
        selected_answer = tk.StringVar(master=quiz_window, value="")

        progress_label = ttk.Label(quiz_content)
        progress_label.pack(anchor="w", pady=(0, 8))
        question_label = ttk.Label(quiz_content, wraplength=420, justify="left")
        question_label.pack(anchor="w", pady=(0, 12))

        answer_buttons = []
        for _ in range(4):
            answer_button = ttk.Radiobutton(
                quiz_content, variable=selected_answer,
            )
            answer_button.pack(anchor="w", pady=4)
            answer_buttons.append(answer_button)

        feedback_label = ttk.Label(quiz_content, wraplength=420, justify="left")
        feedback_label.pack(anchor="w", pady=12)

        def display_question():
            """Reset the choices and feedback for the current question."""
            nonlocal answered
            answered = False
            selected_answer.set("")
            question, choices, correct_answer = questions[question_index]
            progress_label.config(text=f"Question {question_index + 1} of {len(questions)}")
            question_label.config(text=question)
            for button, choice in zip(answer_buttons, choices):
                button.config(text=choice, value=choice, state="normal")
            feedback_label.config(text="")
            submit_button.config(state="normal")
            next_button.config(
                state="disabled",
                text="Show Results" if question_index == len(questions) - 1 else "Next Question",
            )

        def submit_answer():
            """Score each question once and let the user read the feedback."""
            nonlocal score, answered
            if answered:
                return
            if not selected_answer.get():
                feedback_label.config(text="Please select an answer first.")
                return

            correct_answer = questions[question_index][2]
            if selected_answer.get() == correct_answer:
                score += 1
                feedback_label.config(text="Correct!")
            else:
                feedback_label.config(text=f"Incorrect. The correct answer is {correct_answer}.")
            answered = True
            # Lock the answer so repeated clicks cannot increase the score.
            for button in answer_buttons:
                button.config(state="disabled")
            submit_button.config(state="disabled")
            next_button.config(state="normal")

        def next_question():
            """Advance after submission, or replace the quiz with the score."""
            nonlocal question_index
            if not answered:
                return
            question_index += 1
            if question_index < len(questions):
                display_question()
            else:
                # Only quiz widgets are removed; the main window is untouched.
                for widget in quiz_content.winfo_children():
                    widget.destroy()
                ttk.Label(
                    quiz_content,
                    text=f"Quiz complete! You scored {score}/{len(questions)}.",
                ).pack(pady=(0, 12))
                ttk.Button(
                    quiz_content, text="Close Quiz", command=quiz_window.destroy,
                ).pack(fill="x")

        submit_button = ttk.Button(quiz_content, text="Submit Answer", command=submit_answer)
        submit_button.pack(fill="x", pady=4)
        next_button = ttk.Button(quiz_content, text="Next Question", command=next_question)
        next_button.pack(fill="x", pady=4)
        display_question()

    def open_report():
        """Open the existing HTML analysis report in the default web browser."""
        report_path = Path(__file__).resolve().parent / "outputs" / "seasons" / "report.html"
        if not report_path.is_file():
            messagebox.showerror(
                "Analysis report not found",
                f"The analysis report could not be found:\n{report_path}",
                parent=window,
            )
            return
        # Convert the local path to a file URL, including any spaces in the path.
        webbrowser.open(report_path.as_uri())

    # Pack the controls first so the results cannot take their vertical space.
    controls_frame = ttk.Frame(content)
    controls_frame.pack(fill="x")
    ttk.Button(controls_frame, text="Explore Season", command=explore_season).pack(
        fill="x", pady=4
    )
    ttk.Button(controls_frame, text="Quiz", command=show_quiz).pack(fill="x", pady=4)
    ttk.Button(
        controls_frame, text="View Full Analysis Report", command=open_report,
    ).pack(fill="x", pady=4)
    ttk.Button(controls_frame, text="Exit", command=window.destroy).pack(fill="x", pady=4)

    # The summary and graph share only the space remaining below the controls.
    results_area = ttk.Frame(content)
    results_area.pack(fill="both", expand=True)

    # Keep season information inside the results area, below the main controls.
    about_frame = ttk.LabelFrame(results_area, text="About this season", padding=12)
    about_frame.pack(fill="x", pady=(12, 0))
    ttk.Label(
        about_frame,
        textvariable=description_text,
        justify="left",
        wraplength=420,
    ).pack(anchor="w")

    # Display the selected season's summary inside the main window.
    results_frame = ttk.LabelFrame(results_area, text="Weather summary", padding=12)
    results_frame.pack(fill="x", pady=12)
    ttk.Label(
        results_frame,
        textvariable=results_text,
        justify="left",
        wraplength=420,
    ).pack(anchor="w")

    # Create one figure and embed its canvas as a normal Tkinter widget.
    # Each Explore click reuses this figure, so graphs do not accumulate.
    graph_frame = ttk.Frame(results_area)
    graph_frame.pack(fill="both", expand=True, pady=(0, 8))
    temperature_figure = Figure(figsize=(5, 2.5), dpi=100, layout="constrained")
    temperature_axes = temperature_figure.add_subplot(111)
    graph_canvas = FigureCanvasTkAgg(temperature_figure, master=graph_frame)
    graph_canvas.get_tk_widget().pack(fill="both", expand=True)
    clear_graph("Select a season to view daily temperatures.")

    season_dropdown.focus_set()
    # The event loop keeps the window open and responds to user input.
    window.mainloop()


# Launch the GUI only when this file is run directly.
if __name__ == "__main__":
    main()
