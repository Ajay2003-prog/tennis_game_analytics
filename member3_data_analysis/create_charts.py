"""Create Member 3 charts from the generated summary CSV files.

The script reads only files inside member3_data_analysis/outputs/ and writes
PNG images to member3_data_analysis/outputs/charts/. It does not read or
modify the original SportRadar source datasets.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ANALYSIS_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ANALYSIS_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"


def read_summary(filename: str) -> pd.DataFrame:
    """Read one existing summary CSV and fail clearly if it is unavailable."""
    path = OUTPUT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Summary file not found: {path}. Run analyze_data.py first."
        )
    return pd.read_csv(path)


def add_value_labels(ax: plt.Axes, bars: object) -> None:
    """Add integer data labels to a horizontal bar chart."""
    for bar in bars:
        value = bar.get_width()
        ax.text(
            value + max(value * 0.01, 1),
            bar.get_y() + bar.get_height() / 2,
            f"{int(value):,}",
            va="center",
            fontsize=9,
        )


def save_horizontal_bar(
    data: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
    xlabel: str,
    filename: str,
    top_n: int | None = None,
) -> None:
    """Save a consistently styled horizontal bar chart."""
    chart_data = data.sort_values(value_column, ascending=False).copy()
    if top_n is not None:
        chart_data = chart_data.head(top_n)
    chart_data = chart_data.sort_values(value_column, ascending=True)

    fig_height = max(4.5, 0.42 * len(chart_data) + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))
    bars = ax.barh(
        chart_data[label_column].astype(str),
        chart_data[value_column],
        color="#2E6F95",
        edgecolor="#1E4057",
        linewidth=0.6,
    )
    add_value_labels(ax, bars)
    ax.set_title(title, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.tight_layout()
    fig.savefig(CHART_DIR / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Read summary tables and create all five requested charts."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    by_type = read_summary("competition_counts_by_type.csv")
    by_gender = read_summary("competition_counts_by_gender.csv")
    by_category = read_summary("competition_counts_by_category.csv")
    by_country = read_summary("venue_counts_by_country.csv")
    by_complex = read_summary("venues_per_complex.csv")

    save_horizontal_bar(
        by_type,
        "type",
        "competition_count",
        "Competition Counts by Type",
        "Number of competitions",
        "competition_counts_by_type.png",
    )
    save_horizontal_bar(
        by_gender,
        "gender",
        "competition_count",
        "Competition Counts by Gender",
        "Number of competitions",
        "competition_counts_by_gender.png",
    )
    save_horizontal_bar(
        by_category,
        "category_name",
        "competition_count",
        "Top 10 Competition Categories",
        "Number of competitions",
        "top_10_competition_categories.png",
        top_n=10,
    )
    save_horizontal_bar(
        by_country,
        "country_name",
        "venue_count",
        "Top 10 Countries by Venue Count",
        "Number of venues",
        "top_10_countries_by_venue_count.png",
        top_n=10,
    )
    save_horizontal_bar(
        by_complex,
        "complex_name",
        "venue_count",
        "Top 10 Complexes by Number of Venues",
        "Number of venues",
        "top_10_complexes_by_venue_count.png",
        top_n=10,
    )

    print("Charts generated successfully:")
    for chart_path in sorted(CHART_DIR.glob("*.png")):
        print(f"- {chart_path} ({chart_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
