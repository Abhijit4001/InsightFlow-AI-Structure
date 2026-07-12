from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


sns.set_theme(style="whitegrid")


def _ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def save_time_series_chart(analysis: Dict, output_dir: str, filename: str = "monthly_trend.png") -> str:
    _ensure_dir(output_dir)
    series = analysis.get("time_series", [])
    if not series:
        return ""

    df = pd.DataFrame(series)
    plt.figure(figsize=(10, 5))
    plt.plot(df["period"], df["value"], marker="o", linewidth=2)
    plt.xticks(rotation=45, ha="right")
    plt.title("Trend Over Time")
    plt.xlabel("Period")
    plt.ylabel("Value")
    plt.tight_layout()

    path = str(Path(output_dir) / filename)
    plt.savefig(path, dpi=160)
    plt.close()
    return path


def save_category_chart(analysis: Dict, output_dir: str, category_key: str = None, filename: str = "category_breakdown.png") -> str:
    _ensure_dir(output_dir)
    breakdowns = analysis.get("category_breakdowns", {})
    if not breakdowns:
        return ""

    category_key = category_key or list(breakdowns.keys())[0]
    rows = breakdowns.get(category_key, [])
    if not rows:
        return ""

    df = pd.DataFrame(rows)
    value_col = "value" if "value" in df.columns else "count"

    plt.figure(figsize=(10, 5))
    sns.barplot(data=df, x=category_key, y=value_col, palette="viridis")
    plt.xticks(rotation=35, ha="right")
    plt.title(f"Top {category_key.replace('_', ' ').title()}")
    plt.xlabel(category_key.replace("_", " ").title())
    plt.ylabel(value_col.title())
    plt.tight_layout()

    path = str(Path(output_dir) / filename)
    plt.savefig(path, dpi=160)
    plt.close()
    return path


def save_correlation_heatmap(analysis: Dict, output_dir: str, filename: str = "correlation_heatmap.png") -> str:
    _ensure_dir(output_dir)
    records = analysis.get("correlation_matrix", [])
    if not records:
        return ""

    df = pd.DataFrame(records)
    pivot = df.pivot(index="y", columns="x", values="value")

    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, cmap="coolwarm", fmt=".2f", square=True)
    plt.title("Correlation Heatmap")
    plt.tight_layout()

    path = str(Path(output_dir) / filename)
    plt.savefig(path, dpi=160)
    plt.close()
    return path