import json
from typing import Dict


def build_ai_context(analysis: Dict, filename: str) -> str:
    overview = analysis.get("overview", {})
    detected = analysis.get("detected_columns", {})
    kpis = analysis.get("kpis", {})
    numeric_summary = analysis.get("numeric_summary", {})
    category_breakdowns = analysis.get("category_breakdowns", {})
    time_series = analysis.get("time_series", [])
    outliers = analysis.get("outliers", [])

    payload = {
        "filename": filename,
        "overview": overview,
        "detected_columns": detected,
        "kpis": kpis,
        "numeric_summary": numeric_summary,
        "category_breakdowns": category_breakdowns,
        "time_series": time_series[:24],
        "outliers": outliers[:10],
    }
    return json.dumps(payload, indent=2, default=str)


def generate_ai_insights(client, model: str, context_text: str) -> Dict:
    system_prompt = """
You are a senior data analyst.
You will receive structured dataset analysis in JSON.
Return strict JSON with this shape:
{
  "summary": "short executive summary",
  "insights": [
    "insight 1",
    "insight 2",
    "insight 3",
    "insight 4"
  ],
  "risks": [
    "risk 1",
    "risk 2"
  ],
  "recommended_actions": [
    "action 1",
    "action 2",
    "action 3"
  ]
}
Keep insights specific to the data. Do not hallucinate columns or metrics.
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Analyze this dataset summary and generate insights:\n\n{context_text}"
            },
        ],
    )

    content = response.choices[0].message.content
    return json.loads(content)


def answer_user_question(client, model: str, context_text: str, question: str) -> str:
    system_prompt = """
You are a helpful data analyst assistant.
Answer only from the provided dataset summary context.
If the answer cannot be inferred from the context, say that clearly.
Keep the answer concise, practical, and specific.
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_completion_tokens=700,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Dataset context:\n{context_text}\n\nQuestion: {question}"
            },
        ],
    )

    return response.choices[0].message.content.strip()