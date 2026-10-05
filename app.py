"""A basic tkinter interface for the Noongar Seasons Explorer."""

import tkinter as tk
from tkinter import messagebox, ttk


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

    # These callbacks run when the corresponding buttons are clicked.
    def explore_season():
        messagebox.showinfo(
            "Explore Season",
            f"You selected {selected_season.get()}.",
            parent=window,
        )

    def show_quiz():
        messagebox.showinfo("Quiz", "Quiz coming soon!", parent=window)

    ttk.Button(content, text="Explore Season", command=explore_season).pack(
        fill="x", pady=4
    )
    ttk.Button(content, text="Quiz", command=show_quiz).pack(fill="x", pady=4)
    ttk.Button(content, text="Exit", command=window.destroy).pack(fill="x", pady=4)

    season_dropdown.focus_set()
    # The event loop keeps the window open and responds to user input.
    window.mainloop()


# Launch the GUI only when this file is run directly.
if __name__ == "__main__":
    main()
