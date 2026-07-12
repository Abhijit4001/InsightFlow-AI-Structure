import os
import json
import uuid
import traceback
from pathlib import Path
from typing import Optional
from fastapi.staticfiles import StaticFiles

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from groq import Groq

from sales_analysis.analysis import analyze_dataset
from sales_analysis.insights import build_ai_context, generate_ai_insights, answer_user_question

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="InsightFlow AI Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def clean_value(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value):
            return None
        return float(value)
    if pd.isna(value):
        return None
    return value


def normalize_records(records):
    normalized = []
    for record in records:
        normalized.append({k: clean_value(v) for k, v in record.items()})
    return normalized


def read_uploaded_file(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file_path)
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    raise ValueError("Unsupported file type. Please upload CSV or Excel.")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "groq_configured": bool(GROQ_API_KEY),
        "model": GROQ_MODEL
    }


@app.post("/api/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        ext = Path(file.filename).suffix.lower()
        if ext not in [".csv", ".xlsx", ".xls"]:
            return JSONResponse(
                status_code=400,
                content={"error": "Only CSV, XLSX, and XLS files are supported."}
            )

        file_id = str(uuid.uuid4())[:8]
        saved_path = DATA_DIR / f"{file_id}_{file.filename}"

        with open(saved_path, "wb") as f:
            f.write(await file.read())

        df = read_uploaded_file(saved_path)
        analysis_result = analyze_dataset(df)

        preview = df.head(12).replace({np.nan: None}).to_dict(orient="records")

        return {
            "file_id": file_id,
            "filename": file.filename,
            "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "columns": list(df.columns),
            "preview": normalize_records(preview),
            "analysis": analysis_result
        }

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/insights")
async def ai_insights(payload: dict):
    try:
        if not client:
            return JSONResponse(
                status_code=400,
                content={"error": "Groq API key missing. Add GROQ_API_KEY to .env"}
            )

        analysis = payload.get("analysis", {})
        filename = payload.get("filename", "uploaded file")

        context_text = build_ai_context(analysis, filename)
        insights = generate_ai_insights(client, GROQ_MODEL, context_text)

        return {"insights": insights}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/ask")
async def ask_question(payload: dict):
    try:
        if not client:
            return JSONResponse(
                status_code=400,
                content={"error": "Groq API key missing. Add GROQ_API_KEY to .env"}
            )

        question = payload.get("question", "").strip()
        analysis = payload.get("analysis", {})
        filename = payload.get("filename", "uploaded file")

        if not question:
            return JSONResponse(status_code=400, content={"error": "Question is required."})

        context_text = build_ai_context(analysis, filename)
        answer = answer_user_question(client, GROQ_MODEL, context_text, question)

        return {"answer": answer}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory=".", html=True), name="frontend")
# app.mount("/", StaticFiles(directory=".", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("app:app", host=host, port=port, reload=True)