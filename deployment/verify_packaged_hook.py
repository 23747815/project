"""Opt-in acceptance checks inside the actual frozen GUI; normal launches do nothing.

Set NOONGAR_DEPLOYMENT_TEST to an absolute JSON output path to run these checks.
This deployment hook is separate from, and does not edit, app.py.
"""
import os

if os.environ.get("NOONGAR_DEPLOYMENT_TEST"):
    import gc
    import json
    from pathlib import Path
    import sys
    import traceback
    import tkinter as tk
    from tkinter import messagebox, ttk
    import webbrowser

    output_path = Path(os.environ["NOONGAR_DEPLOYMENT_TEST"])
    original_mainloop = tk.Misc.mainloop

    def descendants(widget):
        for child in widget.winfo_children():
            yield child
            yield from descendants(child)

    def fail_message(*args, **kwargs):
        raise AssertionError(f"Unexpected GUI error: {args}")

    def checked_mainloop(window, *args, **kwargs):
        def check():
            result = {"frozen": bool(getattr(sys, "frozen", False)), "executable": sys.executable}
            try:
                import pandas as pd
                from matplotlib.figure import Figure
                messagebox.showerror = fail_message
                widgets = list(descendants(window))
                buttons = {w.cget("text"): w for w in widgets if isinstance(w, ttk.Button)}
                combo = next(w for w in widgets if isinstance(w, ttk.Combobox))
                data_path = Path(sys._MEIPASS) / "outputs/seasons/daily_weather_with_seasons.csv"
                data = pd.read_csv(data_path)
                result["csv_records"] = len(data)
                result["seasons"] = []
                for season in combo.cget("values"):
                    combo.set(season)
                    buttons["Explore Season"].invoke()
                    window.update()
                    labels = [str(w.cget("text")) for w in descendants(window) if isinstance(w, ttk.Label)]
                    summary = next(text for text in labels if text.startswith(f"Season: {season}"))
                    subset = data.loc[data.Season == season]
                    assert f"Recorded days: {len(subset)}" in summary
                    for value in (subset.MinTemp.mean(), subset.MaxTemp.mean(), subset.Rainfall.sum(min_count=1), subset.Sunshine.mean()):
                        assert f"{value:.2f}" in summary
                    figures = [obj for obj in gc.get_objects() if isinstance(obj, Figure)]
                    axes = next(fig.axes[0] for fig in figures if fig.axes and fig.axes[0].get_title() == f"{season}: daily temperatures")
                    assert len(axes.lines) == 2
                    assert len(axes.lines[0].get_xdata()) == len(subset)
                    for text in ("Quiz", "Exit", "View Full Analysis Report"):
                        button = buttons[text]
                        assert button.winfo_viewable()
                        assert button.winfo_rooty() + button.winfo_height() <= window.winfo_rooty() + window.winfo_height()
                    result["seasons"].append({"season": season, "days": len(subset), "summary": "passed", "graph": "passed", "controls": "visible"})

                buttons["Quiz"].invoke()
                window.update()
                quiz = next(w for w in window.winfo_children() if isinstance(w, tk.Toplevel))
                answers = ["Birak", "Bunuru", "Djeran", "Makuru", "Djilba"]
                for index, correct in enumerate(answers):
                    controls = list(descendants(quiz))
                    choices = [w for w in controls if isinstance(w, ttk.Radiobutton)]
                    assert len(choices) == 4
                    quiz_buttons = {w.cget("text"): w for w in controls if isinstance(w, ttk.Button)}
                    if index == 0:
                        quiz_buttons["Submit Answer"].invoke()
                        assert any(w.cget("text") == "Please select an answer first." for w in controls if isinstance(w, ttk.Label))
                    chosen = next(w for w in choices if (w.cget("text") == correct) == (index != 4))
                    chosen.invoke()
                    quiz_buttons["Submit Answer"].invoke()
                    assert quiz_buttons["Submit Answer"].instate(["disabled"])
                    expected = "Correct!" if index != 4 else "Incorrect."
                    assert any(str(w.cget("text")).startswith(expected) for w in controls if isinstance(w, ttk.Label))
                    quiz_buttons["Submit Answer"].invoke()
                    quiz_buttons["Show Results" if index == 4 else "Next Question"].invoke()
                    window.update()
                assert any(w.cget("text") == "Quiz complete! You scored 4/5." for w in descendants(quiz) if isinstance(w, ttk.Label))
                next(w for w in descendants(quiz) if isinstance(w, ttk.Button) and w.cget("text") == "Close Quiz").invoke()
                result["quiz"] = "passed: required selection, feedback, locked answers, 4/5 final score, close"

                original_open = webbrowser.open
                opened = []
                def record_open(url, *a, **kw):
                    accepted = original_open(url, *a, **kw)
                    opened.append({"url": url, "browser_dispatch_accepted": accepted})
                    return accepted
                webbrowser.open = record_open
                buttons["View Full Analysis Report"].invoke()
                report = Path(sys._MEIPASS) / "outputs/seasons/report.html"
                assert opened and opened[0]["url"] == report.as_uri()
                assert opened[0]["browser_dispatch_accepted"]
                result["report"] = opened[0]
                result["status"] = "passed"
                buttons["Exit"].invoke()
                result["exit"] = "main window destroyed by Exit button"
            except Exception:
                result["status"] = "failed"
                result["error"] = traceback.format_exc()
                window.destroy()
            finally:
                output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        window.after(500, check)
        return original_mainloop(window, *args, **kwargs)

    tk.Misc.mainloop = checked_mainloop
