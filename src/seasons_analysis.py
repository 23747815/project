"""Explore Perth weather through the six Noongar seasons.

Run from any directory: python path/to/src/seasons_analysis.py
Or from the project root: python -m src.seasons_analysis

At the start of each run the extended combiner rebuilds data/bom_weather.csv
from the local raw files. Nothing is downloaded and importing this module
does not regenerate data or open charts. Outputs go to outputs/seasons/.
"""

import argparse
from html import escape
from pathlib import Path
import sys

import matplotlib

# Save figures without needing a desktop session (also works in the IDE).
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.combine_data_extended import combine_weather_data
from src.data_loader import load_weather_data
from src.seasons import (
    SEASON_ORDER,
    add_seasons_column,
    get_noongar_season,
    monthly_statistics,
    seasonal_statistics,
    wind_direction_frequencies,
    wind_shift_summary,
)

BOM_CALENDAR = (
    "https://www.bom.gov.au/resources/indigenous-weather-knowledge/"
    "indigenous-seasonal-calendars/nyoongar-calendar"
)
BOM_OBSERVATIONS = "https://www.bom.gov.au/climate/dwo/IDCJDW0000.pdf"

# Presentation colours only, not traditional cultural colour associations.
SEASON_COLORS = dict(zip(SEASON_ORDER, [
    "#B74729", "#CC8B15", "#41754C", "#366B91", "#80609A", "#328C87",
]))
SEASON_MONTHS = {
    "Birak": "Dec–Jan", "Bunuru": "Feb–Mar", "Djeran": "Apr–May",
    "Makuru": "Jun–Jul", "Djilba": "Aug–Sep", "Kambarang": "Oct–Nov",
}
# Brief paraphrases of weather tendencies from the linked Bureau calendar.
SEASON_CONTEXT = {
    "Birak": "Warming and easing rain; morning easterlies can give way to afternoon south-westerlies.",
    "Bunuru": "Intense heat, little rain, and coastal afternoon breezes.",
    "Djeran": "Relief from heat, cooler damp mornings, and gentler winds.",
    "Makuru": "Cold, wet conditions, with winds from the west and south.",
    "Djilba": "A transition with a mixture of cold, clear, wet, windy and warmer days.",
    "Kambarang": "Warming weather and longer dry intervals.",
}


def style_charts():
    """Use a consistent, readable style for exported teaching figures."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.labelcolor": "#34434A", "text.color": "#203139",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.alpha": 0.16, "axes.axisbelow": True,
        "figure.facecolor": "#FAFAF6", "axes.facecolor": "#FAFAF6",
        "savefig.facecolor": "#FAFAF6", "svg.fonttype": "none",
    })


def save_chart(fig, output_dir, filename, title, note, date_range):
    """Save both an easy-to-view PNG and a scalable SVG."""
    fig.suptitle(title, x=0.07, ha="left", fontsize=18, fontweight="bold", y=0.98)
    # Keep the same physical separation on both short and tall figures.
    fig.text(0.07, 0.98 - 0.42 / fig.get_figheight(), f"Perth observations · {date_range}", fontsize=10)
    fig.text(0.07, 0.018, note, fontsize=9, va="bottom", linespacing=1.5)
    fig.tight_layout(rect=(0.02, 0.105, 0.99, 0.915), h_pad=2.4, w_pad=2.5)
    for extension in ("png", "svg"):
        fig.savefig(output_dir / f"{filename}.{extension}", dpi=165)
    plt.close(fig)
    return {"filename": filename, "title": title, "note": note}


def season_axis(ax):
    ax.set_xticks(range(6), [f"{s}\n{SEASON_MONTHS[s]}" for s in SEASON_ORDER], fontsize=9)
    ax.grid(axis="x", visible=False)


def season_bars(ax, values, title, ylabel, percent=False):
    ax.bar(range(6), values, color=[SEASON_COLORS[s] for s in SEASON_ORDER], width=0.65)
    season_axis(ax)
    ax.set(title=title, ylabel=ylabel)
    if percent:
        ax.set_ylim(0, 100)
    else:
        ax.set_ylim(bottom=0)
        ax.margins(y=0.16)
    for position, value in enumerate(values):
        if pd.notna(value):
            ax.annotate(f"{value:.1f}", (position, value), xytext=(0, 5),
                        textcoords="offset points", ha="center", fontsize=9)


def shade_seasons(axes, dates):
    """Shade each contiguous two-month season in calendar time."""
    start, end = dates.min().normalize(), dates.max().normalize() + pd.Timedelta(days=1)
    boundaries = [start]
    for month in pd.date_range(start.replace(day=1), end, freq="MS"):
        if start < month < end and get_noongar_season(month) != get_noongar_season(month - pd.Timedelta(days=1)):
            boundaries.append(month)
    boundaries.append(end)
    for left, right in zip(boundaries[:-1], boundaries[1:]):
        season = get_noongar_season(left)
        for ax in axes:
            ax.axvspan(left, right, color=SEASON_COLORS[season], alpha=0.10, linewidth=0)
        axes[0].text(left + (right - left) / 2, 1.015, season,
                     transform=axes[0].get_xaxis_transform(), ha="center", fontsize=9)
    for ax in axes:
        ax.set_xlim(start, end)


def plot_timeline(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
    # Use seven calendar days, rather than seven available records, per window.
    daily = df.set_index("Date").reindex(pd.date_range(df.Date.min(), df.Date.max()))
    for column, label, colour in (("MaxTemp", "Maximum", "#B74729"), ("MinTemp", "Minimum", "#366B91")):
        axes[0].plot(daily.index, daily[column], color=colour, alpha=0.22, linewidth=0.8)
        axes[0].plot(daily.index, daily[column].rolling(7, min_periods=4).mean(),
                     color=colour, label=f"{label}: trailing 7-day mean", linewidth=2)
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].legend(loc="upper right", fontsize=9, ncol=2)
    axes[1].bar(daily.index, daily.Rainfall, color="#366B91", width=1)
    axes[1].set_ylabel("Recorded rainfall (mm)")
    axes[2].plot(daily.index, daily.Sunshine, color="#CC8B15", alpha=0.22, linewidth=0.8)
    axes[2].plot(daily.index, daily.Sunshine.rolling(7, min_periods=4).mean(), color="#9C6C0C", linewidth=2)
    axes[2].set_ylabel("Sunshine (hours)")
    shade_seasons(axes, df.Date)
    axes[2].xaxis.set_major_locator(mdates.MonthLocator())
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    return save_chart(fig, output_dir, "01_weather_through_the_year", "A year of weather, seen through six seasons",
                      "Bands use approximate calendar seasons. Thin lines show daily observations; smooth lines need ≥4 observed days in 7.\nRainfall is recorded to 9 am; sunshine covers a different observation window. The source dates are retained.", date_range)


def plot_temperatures(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, column, title in zip(axes[0], ["MaxTemp", "MinTemp"], ["Daytime maximum temperatures", "Overnight minimum temperatures"]):
        values = [df.loc[df.Season == s, column].dropna().to_numpy() for s in SEASON_ORDER]
        boxes = ax.boxplot(values, positions=range(6), patch_artist=True, widths=0.55,
                           medianprops={"color": "#172D35", "linewidth": 2},
                           flierprops={"marker": ".", "markersize": 4})
        for patch, season in zip(boxes["boxes"], SEASON_ORDER):
            patch.set_facecolor(SEASON_COLORS[season])
            patch.set_alpha(0.65)
        season_axis(ax)
        ax.set_xticklabels([f"{s}\n{SEASON_MONTHS[s]} · n={len(v)}" for s, v in zip(SEASON_ORDER, values)], fontsize=8)
        ax.set(title=title, ylabel="Temperature (°C)")
    season_bars(axes[1, 0], stats.HotDayPercent, "How often does the maximum reach 35°C?", "Observed maximums (%)", True)
    season_bars(axes[1, 1], stats.CoolNightPercent, "How often does the minimum fall below 10°C?", "Observed minimums (%)", True)
    return save_chart(fig, output_dir, "02_temperature_distributions", "Heat and cool nights: more than an average",
                      "Boxes: middle 50%; line: median; whiskers: up to 1.5×IQR; dots: more extreme days.\n35°C and 10°C are teaching thresholds, not definitions of Noongar seasons. Missing temperatures are excluded per measure.", date_range)


def plot_rainfall(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, column, title, label, percent in [
        (axes[0, 0], "TotalRainfall", "Total recorded rainfall", "Rainfall (mm)", False),
        (axes[0, 1], "MeanRainfall", "Rain per observed day", "Mean rainfall (mm/day)", False),
        (axes[1, 0], "WetDayPercent", "Days with at least 1 mm", "Observed rainfall days (%)", True),
        (axes[1, 1], "LongestDrySpell", "Longest run below 1 mm/day", "Consecutive recorded days", False),
    ]:
        season_bars(ax, stats[column], title, label, percent)
    counts = ", ".join(f"{s}: {int(stats.loc[s, 'RainfallDays'])}" for s in SEASON_ORDER)
    return save_chart(fig, output_dir, "03_rain_and_dry_spells", "Wet seasons and dry intervals",
                      f"Rainfall observations — {counts}. Totals depend on coverage; means and percentages use observed days.\nDry spells stop at missing rain, gaps or a season boundary; December–January remains one Birak. <1 mm may include light rain.", date_range)


def plot_sky(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    season_bars(axes[0], stats.MeanSunshine, "Daily bright sunshine", "Mean hours/day")
    x = np.arange(6)
    for offset, column, label, colour in [(-0.18, "MeanCloud9am", "9 am", "#366B91"), (0.18, "MeanCloud3pm", "3 pm", "#80609A")]:
        axes[1].bar(x + offset, stats[column], width=0.34, label=label, color=colour)
    season_axis(axes[1])
    axes[1].set(title="Cloud cover at two observation times", ylabel="Mean cloud amount (oktas)", ylim=(0, 8))
    axes[1].legend()
    for offset, column, label, colour in [(-0.18, "MeanRainfall", "Rain · Metro", "#366B91"), (0.18, "MeanEvaporation", "Pan evaporation · Airport", "#CC8B15")]:
        axes[2].bar(x + offset, stats[column], width=0.34, label=label, color=colour)
    season_axis(axes[2])
    axes[2].set(title="Rain and evaporative conditions", ylabel="Mean recorded mm/day")
    axes[2].legend(fontsize=8)
    return save_chart(fig, output_dir, "04_sun_cloud_and_evaporation", "Clearer skies and drying conditions",
                      "Sunshine hours depend on daylight length as well as cloud (0 oktas = clear, 8 = overcast). Rain: Perth Metro; other panels: Perth Airport.\nPan evaporation indicates atmospheric drying conditions; this cross-station comparison is not a soil-water balance.", date_range)


def plot_cooling_and_humidity(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    season_bars(axes[0], stats.MeanMinTemp, "Cooler overnight conditions", "Mean minimum (°C)")
    x = np.arange(6)
    for offset, column, label, colour in [(-0.18, "MeanHumidity9am", "9 am", "#366B91"), (0.18, "MeanHumidity3pm", "3 pm", "#328C87")]:
        axes[1].bar(x + offset, stats[column], width=0.34, label=label, color=colour)
    season_axis(axes[1])
    axes[1].set(title="Morning and afternoon humidity", ylabel="Mean relative humidity (%)", ylim=(0, 100))
    axes[1].legend()
    for column, label, colour in [("MeanWindSpeed9am", "9 am", "#366B91"), ("MeanWindSpeed3pm", "3 pm", "#328C87"), ("MeanMaxGustSpeed", "Daily maximum gust", "#B74729")]:
        axes[2].plot(x, stats[column], "o-", color=colour, label=label)
    season_axis(axes[2])
    axes[2].set(title="Breezes and gusts", ylabel="Mean speed (km/h)", ylim=(0, None))
    axes[2].legend(fontsize=8)
    return save_chart(fig, output_dir, "05_cool_mornings_and_breezes", "Exploring Djeran's cooler, damper mornings",
                      "These measurements explore the seasonal cooling and humidity pattern; they do not directly measure dew.\nA gust is a brief peak, not a sustained daily wind speed. A recorded calm is included as 0 km/h; unknown winds remain missing.", date_range)


def plot_wind_directions(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(2, 1, figsize=(13, 9))
    frequencies = [wind_direction_frequencies(df, c) for c in ("WindDirection9am", "WindDirection3pm")]
    maximum = max(10, max(float(f.max().max()) if f.notna().any().any() else 0 for f in frequencies))
    for ax, frequency, label, column in zip(axes, frequencies, ["9 am", "3 pm"], ["WindDirection9am", "WindDirection3pm"]):
        mesh = ax.imshow(frequency.to_numpy(dtype=float), cmap="YlGnBu", vmin=0, vmax=maximum, aspect="auto")
        counts = df[column].astype("string").str.strip().str.upper().isin([c.upper() for c in frequency.columns]).groupby(df.Season).sum()
        ax.set_yticks(range(6), [f"{s} (n={int(counts.get(s, 0))})" for s in SEASON_ORDER])
        ax.set_xticks(range(len(frequency.columns)), frequency.columns, fontsize=9)
        ax.set_title(f"{label}: direction the wind comes FROM", loc="left")
        ax.grid(False)
        for row in range(6):
            for col in range(len(frequency.columns)):
                value = frequency.iloc[row, col]
                if pd.notna(value) and value >= 1:
                    ax.text(col, row, f"{value:.0f}", ha="center", va="center", fontsize=8,
                            color="white" if value > maximum * 0.55 else "#203139")
        fig.colorbar(mesh, ax=ax, label="Observed directions (%)", pad=0.015)
        frequency.to_csv(output_dir / f"wind_directions_{label.replace(' ', '')}.csv", float_format="%.3f")
    return save_chart(fig, output_dir, "06_morning_and_afternoon_winds", "Do morning and afternoon winds differ?",
                      "Each row sums to 100% over valid compass directions plus Calm; n is the number of classified observations.\nTwo snapshots at Perth Metro can illustrate a wind shift, but cannot confirm sea-breeze timing, cause or coastal cooling.", date_range)


def plot_weather_mix(df, stats, output_dir, date_range):
    fig, axes = plt.subplots(2, 3, figsize=(13, 9), sharex=True, sharey=True)
    for ax, season in zip(axes.flat, SEASON_ORDER):
        subset = df.loc[df.Season == season].dropna(subset=["MaxTemp", "Sunshine", "Rainfall"])
        for wet, colour, marker in [(False, "#CC8B15", "o"), (True, "#366B91", "^")]:
            points = subset.loc[(subset.Rainfall >= 1) == wet]
            ax.scatter(points.MaxTemp, points.Sunshine, color=colour, marker=marker, s=28, alpha=0.65, edgecolors="none")
        spread = stats.loc[season, "MaxTempStd"]
        ax.set_title(f"{season} · {SEASON_MONTHS[season]}\nn={len(subset)}, max-temp SD={spread:.1f}°C", fontsize=11)
        ax.set(xlabel="Maximum temperature (°C)", ylabel="Sunshine (hours)", ylim=(0, None))
    axes[0, 0].legend(handles=[
        Line2D([], [], color="#CC8B15", marker="o", linestyle="none", label="Rainfall <1 mm"),
        Line2D([], [], color="#366B91", marker="^", linestyle="none", label="Rainfall ≥1 mm"),
    ], loc="lower right", fontsize=8)
    return save_chart(fig, output_dir, "07_mix_of_daily_weather", "Djilba and the mix of daily weather",
                      "Each point is one source-date record with all three measurements. SD uses all observed daily maximums in the season.\nSunshine and rainfall have different recording windows and stations: these are broad patterns, not same-hour relationships.", date_range)


def plot_monthly_transitions(df, stats, output_dir, date_range):
    monthly = monthly_statistics(df)
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
    x = np.arange(len(monthly))
    colours = [SEASON_COLORS[get_noongar_season(date)] for date in monthly.index]
    axes[0].plot(x, monthly.MeanMaxTemp, "o-", color="#B74729", label="Mean maximum")
    axes[0].plot(x, monthly.MeanMinTemp, "o-", color="#366B91", label="Mean minimum")
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].legend(ncol=2)
    axes[1].bar(x, monthly.TotalRainfall, color=colours, width=0.65)
    axes[1].set_ylabel("Recorded rain (mm)")
    axes[2].bar(x, monthly.MeanSunshine, color=colours, width=0.65)
    axes[2].set_ylabel("Mean sunshine (h/day)")
    axes[2].set_xticks(x, [f"{d:%b %Y}\n{get_noongar_season(d)}" for d in monthly.index], fontsize=8)
    for ax in axes:
        ax.grid(axis="x", visible=False)
    return save_chart(fig, output_dir, "08_monthly_transitions", "Seasons change gradually: compare neighbouring months",
                      "Monthly averages show changes hidden by a two-month seasonal mean. Rainfall bars are observed totals, not estimates for missing days.\nLook for cooling through Djeran and warming through Kambarang; allow this individual year to differ from a typical pattern.", date_range)


def data_quality(df):
    """Describe measurement coverage without replacing missing observations."""
    columns = [c for c in df.columns if c not in ("Date", "Season", "SourceFile")]
    quality = pd.DataFrame({"ObservedDays": df[columns].count(), "MissingDays": df[columns].isna().sum()})
    quality["CoveragePercent"] = 100 * quality.ObservedDays / len(df)
    quality.index.name = "Measurement"
    return quality


def build_findings(stats, shifts):
    """Describe measured results, including mismatches with expectations."""
    if stats.MeanMaxTemp.dropna().empty or stats.TotalRainfall.dropna().empty:
        return ["There are insufficient temperature or rainfall observations for the headline comparison. "
                "Use the coverage table and individual graphs to see which measurements are available."]
    warmest = stats.MeanMaxTemp.idxmax()
    coolest = stats.MeanMaxTemp.idxmin()
    wettest = stats.TotalRainfall.idxmax()
    return [
        f"The highest seasonal mean maximum was {stats.loc[warmest, 'MeanMaxTemp']:.1f}°C in {warmest}. "
        f"Bunuru averaged {stats.loc['Bunuru', 'MeanMaxTemp']:.1f}°C. "
        f"Mean minimums were {stats.loc['Birak', 'MeanMinTemp']:.1f}°C in Birak and {stats.loc['Bunuru', 'MeanMinTemp']:.1f}°C in Bunuru; "
        "which season is hottest can depend on the measure. This sample need not exactly match the broad description.",
        f"{coolest} had the lowest mean maximum ({stats.loc[coolest, 'MeanMaxTemp']:.1f}°C). "
        f"{wettest} had the largest observed rainfall total ({stats.loc[wettest, 'TotalRainfall']:.1f} mm). "
        f"Makuru recorded {stats.loc['Makuru', 'TotalRainfall']:.1f} mm and {stats.loc['Makuru', 'WetDayPercent']:.1f}% wet days.",
        f"From Bunuru to Djeran, the mean minimum changed from {stats.loc['Bunuru', 'MeanMinTemp']:.1f}°C "
        f"to {stats.loc['Djeran', 'MeanMinTemp']:.1f}°C, while 9 am relative humidity changed from "
        f"{stats.loc['Bunuru', 'MeanHumidity9am']:.1f}% to {stats.loc['Djeran', 'MeanHumidity9am']:.1f}%. These are not direct dew measurements.",
        f"From Djilba to Kambarang, the mean maximum changed from {stats.loc['Djilba', 'MeanMaxTemp']:.1f}°C "
        f"to {stats.loc['Kambarang', 'MeanMaxTemp']:.1f}°C. The longest within-season run below 1 mm/day "
        f"changed from {stats.loc['Djilba', 'LongestDrySpell']:.0f} to {stats.loc['Kambarang', 'LongestDrySpell']:.0f} days.",
        f"The narrowly defined morning-east to afternoon-south-west pattern occurred on "
        f"{shifts.loc['Birak', 'EastToSWPercent']:.1f}% of paired observations in Birak and "
        f"{shifts.loc['Bunuru', 'EastToSWPercent']:.1f}% in Bunuru. See the full direction distributions before drawing conclusions.",
    ]


def write_report(df, stats, monthly, quality, shifts, charts, output_dir, date_range):
    """Create a local HTML teaching report and a plain-text findings file."""
    findings = build_findings(stats, shifts)
    expected_days = len(pd.date_range(df.Date.min(), df.Date.max()))
    missing_dates = expected_days - df.Date.nunique()
    context_rows = "".join(
        f'<tr><th style="border-left:5px solid {SEASON_COLORS[s]}">{s}<small>{SEASON_MONTHS[s]}</small></th>'
        f'<td>{escape(SEASON_CONTEXT[s])}</td></tr>' for s in SEASON_ORDER
    )
    chart_html = "".join(
        f'<section id="{chart["filename"]}"><h2>{escape(chart["title"])}</h2>'
        f'<a href="{chart["filename"]}.png"><img loading="lazy" src="{chart["filename"]}.png" '
        f'alt="{escape(chart["title"])}"></a><p>{escape(chart["note"]).replace(chr(10), "<br>")}</p>'
        f'<p class="downloads"><a href="{chart["filename"]}.png">PNG</a> · '
        f'<a href="{chart["filename"]}.svg">Scalable SVG</a></p></section>' for chart in charts
    )
    table_columns = ["Days", "TemperatureDays", "RainfallDays", "MeanMinTemp", "MeanMaxTemp", "TotalRainfall", "WetDayPercent", "MeanSunshine", "LongestDrySpell"]
    table = stats[table_columns].rename(columns={
        "Days": "Records", "TemperatureDays": "Max temp n", "RainfallDays": "Rain n",
        "MeanMinTemp": "Min °C", "MeanMaxTemp": "Max °C", "TotalRainfall": "Rain mm",
        "WetDayPercent": "Wet days %", "MeanSunshine": "Sun h/day", "LongestDrySpell": "Dry run days",
    }).to_html(float_format=lambda x: f"{x:.1f}", na_rep="—", border=0)
    links = "".join(f'<a href="#{c["filename"]}">{i:02d} {escape(c["title"])}</a>' for i, c in enumerate(charts, 1))
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Six seasons · Perth weather</title>
<style>
:root {{ color-scheme: light; }} * {{ box-sizing: border-box; }}
body {{ margin:0; font:16px/1.65 system-ui,sans-serif; color:#203139; background:#efefe7; }}
main {{ max-width:1280px; margin:auto; padding:32px; }}
header {{ padding:42px; background:#163c3c; color:#fafaf6; border-radius:16px; }}
h1 {{ font-size:clamp(32px,5vw,60px); line-height:1.1; margin:10px 0 24px; }}
h2 {{ font-size:25px; line-height:1.3; }} .eyebrow {{ letter-spacing:0.16em; text-transform:uppercase; font-size:12px; }}
section {{ background:#fafaf6; padding:28px; border-radius:12px; margin:22px 0; }}
section img {{ display:block; width:100%; height:auto; }} a {{ color:#246569; }} header a {{ color:#b4dfd5; }}
nav {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:8px; margin:22px 0; }}
nav a {{ background:#fafaf6; border-radius:6px; padding:10px 14px; text-decoration:none; font-size:14px; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }} th,td {{ padding:10px; text-align:left; border-bottom:1px solid #dce0d6; }}
th small {{ display:block; font-weight:normal; color:#65756d; }} .table-wrap {{ overflow-x:auto; }}
.downloads {{ font-size:13px; }} li {{ margin-bottom:10px; }} .callout {{ border-left:4px solid #cc8b15; padding-left:18px; }}
summary {{ cursor:pointer; font-weight:bold; }} @media(max-width:600px) {{ main {{ padding:12px; }} header,section {{ padding:18px; }} }}
@media print {{ body {{ background:white; }} nav,.downloads {{ display:none; }} section {{ break-inside:avoid; }} }}
</style></head><body><main>
<header><div class="eyebrow">Weather observations · Learning with data</div><h1>One year.<br>Six seasonal perspectives.</h1>
<p>Perth · {escape(date_range)} · {len(df)} daily records</p>
<p>Explore temperature, rain, sunshine and winds alongside the <a href="{BOM_CALENDAR}">Bureau's Nyoongar seasonal calendar</a>.</p></header>
<section><h2>How to read this demonstration</h2>
<p>The Noongar calendar belongs to the peoples of south-west Australia. Its seasons respond to local environmental signs and can vary in length;
the two-month bins here are an approximate teaching guide. Weather data cannot represent the full ecological and cultural knowledge in the calendar.</p>
<p class="callout">This is a descriptive comparison of the supplied Perth data, not a long-term climatology, a test of traditional knowledge,
or a rule for detecting the start of a season. Results that differ from the broad descriptions remain visible.</p>
<table>{context_rows}</table><p>Weather descriptions paraphrased from the linked Bureau calendar. Chart colours are presentation choices.</p></section>
<section><h2>What this sample shows</h2><ul>{''.join('<li>' + escape(f) + '</li>' for f in findings)}</ul></section>
<nav aria-label="Charts">{links}</nav>{chart_html}
<section><h2>Compare the six seasons</h2><div class="table-wrap">{table}</div>
<p>Temperatures and sunshine are means; rain is a total. Wet = ≥1 mm; dry run = consecutive recorded days below 1 mm within a season.</p>
<p><a href="seasonal_statistics.csv">Full seasonal statistics</a> · <a href="monthly_statistics.csv">Monthly statistics</a> ·
<a href="wind_shift_summary.csv">Paired wind-shift counts</a> · <a href="daily_weather_with_seasons.csv">Daily data with seasons</a></p></section>
<section><h2>Coverage, methods and limitations</h2>
<ul><li>{len(df)} unique source dates across {expected_days} calendar days; {missing_dates} absent dates. No weather values were filled or interpolated.</li>
<li>Each mean and percentage uses observations available for that measurement. Counts are in the exported tables. Zero rainfall is an observation; missing rainfall is unknown.</li>
<li>Totals are observed totals and are affected by season length and missing records. For this sample, compare daily means and wet-day percentages too.</li>
<li>Raw-file metadata assigns temperature, humidity, wind, pressure and rain to Perth Metro (009225), and sunshine, cloud and evaporation to Perth Airport (009021).</li>
<li>Recorded dates are retained. Rainfall and pan evaporation cover the 24 hours to 9 am; sunshine covers the 24 hours to midnight.
See the <a href="{BOM_OBSERVATIONS}">Bureau's observation notes</a>. Same-row measurements need not describe precisely the same hours.</li>
<li>Daily minimums cover the period ending at 9 am, while maximums cover the period starting at 9 am. The exported MeanDailyRange is a same-source-date difference, not a strictly coincident diurnal range.</li>
<li>Sunshine hours also change with available daylight. Cloud observations offer a separate view of sky conditions.</li>
<li>Illustrative thresholds: wet day ≥1 mm, hot day maximum ≥35°C, cool night minimum &lt;10°C. These are not cultural season definitions.</li>
<li>Wind directions describe where wind comes from. The paired proxy requires 9 am ENE/E/ESE and 3 pm SSW/SW/WSW on a date with both directions known (including calm as a valid observation).</li>
<li>Dry runs end at a wet day, missing rain, a gap in dates, or the end of a season occurrence. December and January form one Birak. Runs may be truncated at the dataset edges.</li>
<li>Seasonal summaries pool available occurrences if additional years are later supplied; totals would then need year-by-year comparisons. This report currently describes the local sample only.</li></ul>
<details><summary>Measurement coverage</summary><div class="table-wrap">{quality.to_html(float_format=lambda x: f'{x:.1f}', na_rep='—', border=0)}</div></details>
<p><a href="data_quality.csv">Download coverage</a> · <a href="findings.md">Read the findings as text</a></p></section>
<footer>Source: local BOM monthly CSV files, retained under data/raw_data. Generated by src/seasons_analysis.py. No external scripts or fonts are required.</footer>
</main></body></html>'''
    (output_dir / "report.html").write_text(html, encoding="utf-8")
    notes = [
        "# Noongar seasons: Perth weather demonstration", "", date_range, "",
        f"Source calendar: {BOM_CALENDAR}", "",
        "One supplied year; approximate month bins; not a long-term climate estimate or a test of traditional knowledge.",
        "Temperature/rain/humidity/wind: Perth Metro. Sunshine/cloud/evaporation: Perth Airport.", "",
        *[f"- {finding}" for finding in findings], "",
        "Wet day >=1 mm; hot day >=35°C maximum; cool night <10°C minimum. Missing observations excluded per measure.",
        f"Observation windows: {BOM_OBSERVATIONS}",
        "See report.html for complete methods, data coverage and charts.",
    ]
    (output_dir / "findings.md").write_text("\n".join(notes) + "\n", encoding="utf-8")


def run_analysis(output_dir=None):
    """Rebuild the extended CSV first, then save all tables, figures and report."""
    # Regeneration is deliberately the first data-processing step of every run.
    combine_weather_data()
    df = load_weather_data(PROJECT_ROOT / "data" / "bom_weather.csv", drop_missing=False)
    if df.empty:
        raise ValueError("There are no dated weather observations to analyse.")
    if df.Date.duplicated().any():
        raise ValueError("The analysis needs at most one observation row per date.")
    df = add_seasons_column(df)
    output_dir = Path(output_dir) if output_dir is not None else PROJECT_ROOT / "outputs" / "seasons"
    output_dir.mkdir(parents=True, exist_ok=True)
    date_range = f"{df.Date.min():%d %b %Y} – {df.Date.max():%d %b %Y}"
    stats = seasonal_statistics(df)
    monthly = monthly_statistics(df)
    quality = data_quality(df)
    shifts = wind_shift_summary(df)
    for name, table in [("seasonal_statistics", stats), ("monthly_statistics", monthly),
                        ("data_quality", quality), ("wind_shift_summary", shifts)]:
        table.to_csv(output_dir / f"{name}.csv", float_format="%.3f")
    df.to_csv(output_dir / "daily_weather_with_seasons.csv", index=False)
    style_charts()
    charts = [plot(df, stats, output_dir, date_range) for plot in (
        plot_timeline, plot_temperatures, plot_rainfall, plot_sky,
        plot_cooling_and_humidity, plot_wind_directions, plot_weather_mix, plot_monthly_transitions,
    )]
    write_report(df, stats, monthly, quality, shifts, charts, output_dir, date_range)
    print(f"\nAnalysed {len(df)} days ({date_range}).")
    print(stats[["MeanMaxTemp", "TotalRainfall", "WetDayPercent", "MeanSunshine"]].round(2).to_string())
    print(f"\nSaved {len(charts)} charts (PNG + SVG), data tables, and report:")
    print(output_dir / "report.html")
    return output_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="Output folder (default: project/outputs/seasons)")
    args = parser.parse_args()
    run_analysis(args.output_dir)


if __name__ == "__main__":
    main()
