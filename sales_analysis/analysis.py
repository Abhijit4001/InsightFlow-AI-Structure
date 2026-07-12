from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from .data_loader import load_dataframe


COMMON_DATE_HINTS = ["date", "order_date", "purchase_date", "created_at", "month", "year"]
COMMON_REVENUE_HINTS = ["sales", "revenue", "amount", "total", "profit", "price"]
COMMON_QUANTITY_HINTS = ["quantity", "qty", "units", "count", "volume"]
COMMON_CATEGORY_HINTS = ["category", "segment", "product", "product_name", "item", "channel", "region", "state", "city"]


def to_native(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def records_native(records: List[dict]) -> List[dict]:
    return [{k: to_native(v) for k, v in row.items()} for row in records]


def detect_date_column(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    for hint in COMMON_DATE_HINTS:
        if hint in df.columns:
            return hint
    return None


def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=[np.number]).columns.tolist()


def detect_primary_metric(df: pd.DataFrame) -> Optional[str]:
    numeric_cols = detect_numeric_columns(df)
    for hint in COMMON_REVENUE_HINTS:
        for col in numeric_cols:
            if hint in col:
                return col
    return numeric_cols[0] if numeric_cols else None


def detect_quantity_metric(df: pd.DataFrame) -> Optional[str]:
    numeric_cols = detect_numeric_columns(df)
    for hint in COMMON_QUANTITY_HINTS:
        for col in numeric_cols:
            if hint in col:
                return col
    return None


def detect_category_columns(df: pd.DataFrame, limit: int = 4) -> List[str]:
    object_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    ranked = []

    for hint in COMMON_CATEGORY_HINTS:
        for col in object_cols:
            if hint in col and col not in ranked:
                ranked.append(col)

    for col in object_cols:
        if col not in ranked and df[col].nunique(dropna=True) <= min(30, len(df)):
            ranked.append(col)

    return ranked[:limit]


def basic_overview(df: pd.DataFrame) -> Dict:
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def numeric_summary(df: pd.DataFrame) -> Dict:
    numeric_cols = detect_numeric_columns(df)
    result = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        result[col] = {
            "sum": to_native(series.sum()),
            "mean": to_native(series.mean()),
            "median": to_native(series.median()),
            "min": to_native(series.min()),
            "max": to_native(series.max()),
            "std": to_native(series.std()),
        }

    return result


def category_breakdowns(df: pd.DataFrame, metric_col: Optional[str], category_cols: List[str]) -> Dict:
    breakdowns = {}

    for col in category_cols:
        if metric_col and metric_col in df.columns:
            grouped = (
                df.groupby(col, dropna=False)[metric_col]
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            grouped.columns = [col, "value"]
            breakdowns[col] = records_native(grouped.to_dict(orient="records"))
        else:
            counts = df[col].fillna("Unknown").value_counts().head(10).reset_index()
            counts.columns = [col, "count"]
            breakdowns[col] = records_native(counts.to_dict(orient="records"))

    return breakdowns


def build_time_series(df: pd.DataFrame, date_col: Optional[str], metric_col: Optional[str]) -> List[dict]:
    if not date_col or not metric_col:
        return []

    temp = df.copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
    temp = temp.dropna(subset=[date_col, metric_col])

    if temp.empty:
        return []

    temp["time_bucket"] = temp[date_col].dt.to_period("M").astype(str)

    trend = (
        temp.groupby("time_bucket")[metric_col]
        .sum()
        .reset_index()
        .sort_values("time_bucket")
    )
    trend.columns = ["period", "value"]

    return records_native(trend.to_dict(orient="records"))


def correlation_data(df: pd.DataFrame) -> List[dict]:
    numeric_cols = detect_numeric_columns(df)
    if len(numeric_cols) < 2:
        return []

    corr = df[numeric_cols].corr(numeric_only=True).round(3)
    records = []

    for i, row_name in enumerate(corr.index):
        for j, col_name in enumerate(corr.columns):
            records.append({
                "x": row_name,
                "y": col_name,
                "value": to_native(corr.iloc[i, j])
            })

    return records


def top_insight_cards(
    df: pd.DataFrame,
    metric_col: Optional[str],
    quantity_col: Optional[str],
    date_col: Optional[str],
    category_cols: List[str]
) -> Dict:
    cards = {
        "total_records": int(len(df)),
        "primary_metric": metric_col,
        "total_metric": None,
        "average_metric": None,
        "total_quantity": None,
        "best_category": None,
        "latest_period_value": None,
        "previous_period_value": None,
        "period_change_pct": None,
    }

    if metric_col and metric_col in df.columns:
        cards["total_metric"] = to_native(df[metric_col].fillna(0).sum())
        cards["average_metric"] = to_native(df[metric_col].fillna(0).mean())

    if quantity_col and quantity_col in df.columns:
        cards["total_quantity"] = to_native(df[quantity_col].fillna(0).sum())

    if metric_col and category_cols:
        cat = category_cols[0]
        grouped = (
            df.groupby(cat, dropna=False)[metric_col]
            .sum()
            .sort_values(ascending=False)
        )
        if not grouped.empty:
            cards["best_category"] = {
                "column": cat,
                "label": to_native(grouped.index[0]),
                "value": to_native(grouped.iloc[0])
            }

    series = build_time_series(df, date_col, metric_col)
    if len(series) >= 2:
        latest = series[-1]["value"]
        previous = series[-2]["value"]
        cards["latest_period_value"] = latest
        cards["previous_period_value"] = previous
        if previous not in [0, None]:
            cards["period_change_pct"] = round(((latest - previous) / previous) * 100, 2)

    return cards


def detect_outliers(df: pd.DataFrame, metric_col: Optional[str]) -> List[dict]:
    if not metric_col or metric_col not in df.columns:
        return []

    series = df[metric_col].dropna()
    if len(series) < 5:
        return []

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[(df[metric_col] < lower) | (df[metric_col] > upper)].copy()
    if outliers.empty:
        return []

    cols = [c for c in df.columns[:6]]
    return records_native(outliers[cols].head(10).to_dict(orient="records"))


def analyze_dataset(raw_df: pd.DataFrame) -> Dict:
    df = load_dataframe(raw_df)

    date_col = detect_date_column(df)
    metric_col = detect_primary_metric(df)
    quantity_col = detect_quantity_metric(df)
    category_cols = detect_category_columns(df)

    result = {
        "overview": basic_overview(df),
        "detected_columns": {
            "date": date_col,
            "primary_metric": metric_col,
            "quantity": quantity_col,
            "categories": category_cols,
        },
        "kpis": top_insight_cards(df, metric_col, quantity_col, date_col, category_cols),
        "numeric_summary": numeric_summary(df),
        "category_breakdowns": category_breakdowns(df, metric_col, category_cols),
        "time_series": build_time_series(df, date_col, metric_col),
        "correlation_matrix": correlation_data(df),
        "outliers": detect_outliers(df, metric_col),
        "sample_rows": records_native(df.head(10).to_dict(orient="records")),
    }

    return result