import pandas as pd


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(col).strip().lower().replace(" ", "_").replace("-", "_")
        for col in df.columns
    ]
    return df


def try_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if any(token in col for token in ["date", "time", "month", "year"]):
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except Exception:
                pass
    return df


def load_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_column_names(df)
    df = try_parse_dates(df)
    return df