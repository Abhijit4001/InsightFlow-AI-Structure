from pathlib import Path
from typing import Dict

import pandas as pd


def export_summary_report(analysis: Dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    overview = analysis.get("overview", {})
    kpis = analysis.get("kpis", {})
    detected = analysis.get("detected_columns", {})

    rows.append({"section": "overview", "key": "rows", "value": overview.get("rows")})
    rows.append({"section": "overview", "key": "columns", "value": overview.get("columns")})
    rows.append({"section": "detected", "key": "date", "value": detected.get("date")})
    rows.append({"section": "detected", "key": "primary_metric", "value": detected.get("primary_metric")})
    rows.append({"section": "detected", "key": "quantity", "value": detected.get("quantity")})

    for key, value in kpis.items():
        rows.append({"section": "kpis", "key": key, "value": str(value)})

    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    return str(path)