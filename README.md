# InsightFlow AI Dashboard

InsightFlow AI is a modern analytics dashboard that lets you upload CSV or Excel files, generate summary metrics and charts, and ask AI for insights using the Groq API.

## Features

- Upload CSV, XLSX, and XLS files
- Auto-detect date, metric, quantity, and category columns
- KPI cards for records, totals, averages, and trend change
- Interactive charts with Chart.js
- AI-generated executive summary, insights, risks, and recommended actions
- Ask AI questions about your uploaded dataset

## Project Structure

```bash
INSIGHTFLOW-AI-STRUCTURE/
│── .env
│── app.py
│── server.py
│── dashboard.html
│── index.html
│── package.json
│── requirements.txt
│── assets/
│   ├── css/
│   └── js/
│── data/
│── output/
│── sales_analysis/
│   ├── __init__.py
│   ├── analysis.py
│   ├── data_loader.py
│   ├── insights.py
│   ├── report.py
│   └── visualizer.py
```

## Setup

### 1. Create virtual environment

```bash
python -m venv .venv
```

### 2. Activate virtual environment

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
APP_HOST=127.0.0.1
APP_PORT=8000
```

## Run the app

### Option 1: Run with uvicorn

```bash
uvicorn app:app --reload
```

### Option 2: Run with Python

```bash
python server.py
```

### Option 3: Run with npm script

```bash
npm run dev
```

## Open in browser

```txt
http://127.0.0.1:8000
```

## API Endpoints

- `GET /api/health`
- `POST /api/analyze`
- `POST /api/insights`
- `POST /api/ask`

## Notes

- Upload and analysis work best directly from `dashboard.html`.
- `index.html` can be kept as a landing page.
- Make sure your Groq API key is valid before using AI insights or AI Q&A.