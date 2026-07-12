const API_BASE = "";

const state = {
  file: null,
  fileName: sessionStorage.getItem("insightflow-file-name") || "",
  analysis: null,
  insights: null,
  charts: {}
};

const els = {
  themeButtons: document.querySelectorAll("[data-theme-toggle]"),
  fileInput: document.getElementById("dashboard-file"),
  sidebarFileText: document.getElementById("sidebarFileText"),
  analyzeBtn: document.getElementById("analyzeBtn"),
  generateInsightsBtn: document.getElementById("generateInsightsBtn"),
  datasetName: document.getElementById("datasetName"),
  datasetMeta: document.getElementById("datasetMeta"),
  rowBadge: document.getElementById("rowBadge"),
  colBadge: document.getElementById("colBadge"),
  modelBadge: document.getElementById("modelBadge"),
  kpiRecords: document.getElementById("kpiRecords"),
  kpiMetricTotal: document.getElementById("kpiMetricTotal"),
  kpiMetricAvg: document.getElementById("kpiMetricAvg"),
  kpiPeriodChange: document.getElementById("kpiPeriodChange"),
  kpiBestCategory: document.getElementById("kpiBestCategory"),
  previewHead: document.getElementById("previewHead"),
  previewBody: document.getElementById("previewBody"),
  columnCountBadge: document.getElementById("columnCountBadge"),
  aiStateBadge: document.getElementById("aiStateBadge"),
  insightSummary: document.getElementById("insightSummary"),
  insightList: document.getElementById("insightList"),
  riskList: document.getElementById("riskList"),
  actionList: document.getElementById("actionList"),
  questionInput: document.getElementById("questionInput"),
  askAiBtn: document.getElementById("askAiBtn"),
  assistantResponse: document.getElementById("assistantResponse"),
  promptChips: document.querySelectorAll(".prompt-chip"),
  trendChart: document.getElementById("trendChart"),
  categoryChart: document.getElementById("categoryChart"),
  statusChart: document.getElementById("statusChart"),
  radarChart: document.getElementById("radarChart")
};

let currentTheme = document.documentElement.getAttribute("data-theme") || "dark";

function applyTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  els.themeButtons.forEach((btn) => {
    btn.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    const icon = btn.querySelector(".theme-icon");
    if (icon) icon.textContent = theme === "dark" ? "◐" : "◑";
  });
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "—";
  const num = Number(value);
  if (Number.isNaN(num)) return String(value);
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(num);
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${Number(value).toFixed(2)}%`;
}

function setStatus(text, type = "default") {
  els.assistantResponse.textContent = text;
  els.assistantResponse.style.color =
    type === "error" ? "var(--color-danger)" :
    type === "success" ? "var(--color-text)" :
    "var(--color-text-muted)";
}

function destroyChart(chartKey) {
  if (state.charts[chartKey]) {
    state.charts[chartKey].destroy();
    state.charts[chartKey] = null;
  }
}

function getChartTextColor() {
  return getComputedStyle(document.documentElement).getPropertyValue("--color-text").trim();
}

function getChartMutedColor() {
  return getComputedStyle(document.documentElement).getPropertyValue("--color-text-muted").trim();
}

function getBorderColor() {
  return getComputedStyle(document.documentElement).getPropertyValue("--color-border").trim();
}

function buildLineChart(series) {
  destroyChart("trend");

  if (!series || !series.length) return;

  state.charts.trend = new Chart(els.trendChart, {
    type: "line",
    data: {
      labels: series.map((item) => item.period),
      datasets: [{
        label: "Metric",
        data: series.map((item) => item.value),
        borderColor: "#6ee7f9",
        backgroundColor: "rgba(110, 231, 249, 0.18)",
        fill: true,
        tension: 0.35,
        borderWidth: 2.5,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: getChartTextColor() }
        }
      },
      scales: {
        x: {
          ticks: { color: getChartMutedColor() },
          grid: { color: "rgba(255,255,255,0.05)" }
        },
        y: {
          ticks: { color: getChartMutedColor() },
          grid: { color: "rgba(255,255,255,0.05)" }
        }
      }
    }
  });
}

function buildCategoryChart(analysis) {
  destroyChart("category");

  const breakdowns = analysis?.category_breakdowns || {};
  const firstKey = Object.keys(breakdowns)[0];
  if (!firstKey || !breakdowns[firstKey]?.length) return;

  const rows = breakdowns[firstKey];
  const valueKey = rows[0].value !== undefined ? "value" : "count";

  state.charts.category = new Chart(els.categoryChart, {
    type: "bar",
    data: {
      labels: rows.map((row) => row[firstKey]),
      datasets: [{
        label: firstKey.replaceAll("_", " "),
        data: rows.map((row) => row[valueKey]),
        backgroundColor: [
          "#6ee7f9",
          "#7c89ff",
          "#22c55e",
          "#f59e0b",
          "#f43f5e",
          "#60a5fa",
          "#c084fc",
          "#34d399",
          "#fb7185",
          "#a3e635"
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: getChartTextColor() }
        }
      },
      scales: {
        x: {
          ticks: { color: getChartMutedColor() },
          grid: { color: "rgba(255,255,255,0.04)" }
        },
        y: {
          ticks: { color: getChartMutedColor() },
          grid: { color: "rgba(255,255,255,0.04)" }
        }
      }
    }
  });
}

function buildStatusChart(analysis) {
  destroyChart("status");

  const breakdowns = analysis?.category_breakdowns || {};
  const keys = Object.keys(breakdowns);
  const fallbackKey = keys.length > 1 ? keys[1] : keys[0];
  if (!fallbackKey || !breakdowns[fallbackKey]?.length) return;

  const rows = breakdowns[fallbackKey].slice(0, 6);
  const valueKey = rows[0].value !== undefined ? "value" : "count";

  state.charts.status = new Chart(els.statusChart, {
    type: "doughnut",
    data: {
      labels: rows.map((row) => row[fallbackKey]),
      datasets: [{
        data: rows.map((row) => row[valueKey]),
        backgroundColor: ["#6ee7f9", "#7c89ff", "#22c55e", "#f59e0b", "#f43f5e", "#60a5fa"],
        borderColor: "rgba(0,0,0,0)",
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: getChartTextColor(),
            padding: 14
          }
        }
      }
    }
  });
}

function buildRadarChart(analysis) {
  destroyChart("radar");

  const numericSummary = analysis?.numeric_summary || {};
  const keys = Object.keys(numericSummary).slice(0, 5);
  if (!keys.length) return;

  state.charts.radar = new Chart(els.radarChart, {
    type: "radar",
    data: {
      labels: keys.map((key) => key.replaceAll("_", " ")),
      datasets: [{
        label: "Average values",
        data: keys.map((key) => Number(numericSummary[key]?.mean || 0)),
        borderColor: "#7c89ff",
        backgroundColor: "rgba(124, 137, 255, 0.18)",
        pointBackgroundColor: "#6ee7f9",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: getChartTextColor() }
        }
      },
      scales: {
        r: {
          angleLines: { color: "rgba(255,255,255,0.06)" },
          grid: { color: "rgba(255,255,255,0.06)" },
          pointLabels: { color: getChartMutedColor() },
          ticks: {
            color: getChartMutedColor(),
            backdropColor: "transparent"
          }
        }
      }
    }
  });
}

function renderPreview(previewRows = []) {
  els.previewHead.innerHTML = "";
  els.previewBody.innerHTML = "";

  if (!previewRows.length) {
    els.previewBody.innerHTML = `<tr><td class="empty-cell">No preview data available.</td></tr>`;
    return;
  }

  const columns = Object.keys(previewRows[0]);
  const headRow = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    th.textContent = col;
    headRow.appendChild(th);
  });
  els.previewHead.appendChild(headRow);

  previewRows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((col) => {
      const td = document.createElement("td");
      const value = row[col];
      td.textContent = value === null || value === undefined ? "—" : value;
      tr.appendChild(td);
    });
    els.previewBody.appendChild(tr);
  });
}

function renderKpis(analysis, fileName, shape) {
  const kpis = analysis?.kpis || {};
  const bestCategory = kpis.best_category;

  els.datasetName.textContent = fileName || "Uploaded dataset";
  els.datasetMeta.textContent = `Detected ${shape.rows} rows and ${shape.columns} columns.`;
  els.rowBadge.textContent = `${shape.rows} rows`;
  els.colBadge.textContent = `${shape.columns} columns`;
  els.columnCountBadge.textContent = `${shape.columns} columns`;

  els.kpiRecords.textContent = formatNumber(kpis.total_records ?? shape.rows);
  els.kpiMetricTotal.textContent = formatNumber(kpis.total_metric);
  els.kpiMetricAvg.textContent = formatNumber(kpis.average_metric);
  els.kpiPeriodChange.textContent = formatPercent(kpis.period_change_pct);
  els.kpiBestCategory.textContent = bestCategory?.label ? `${bestCategory.label}` : "—";
}

function renderInsights(insights) {
  els.aiStateBadge.textContent = "Generated";
  els.insightSummary.textContent = insights.summary || "No summary available.";

  const fillList = (element, items) => {
    element.innerHTML = "";
    if (!items || !items.length) {
      element.innerHTML = "<li>No items available.</li>";
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      element.appendChild(li);
    });
  };

  fillList(els.insightList, insights.insights);
  fillList(els.riskList, insights.risks);
  fillList(els.actionList, insights.recommended_actions);
}

function renderAllCharts(analysis) {
  buildLineChart(analysis.time_series || []);
  buildCategoryChart(analysis);
  buildStatusChart(analysis);
  buildRadarChart(analysis);
}

async function analyzeCurrentFile() {
  if (!state.file) {
    setStatus("Please upload a file first.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", state.file, state.file.name);

  els.analyzeBtn.disabled = true;
  els.analyzeBtn.textContent = "Analyzing...";
  setStatus("Uploading file and running analysis...");

  try {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Analysis failed.");
    }

    state.analysis = data.analysis;
    state.fileName = data.filename;
    sessionStorage.setItem("insightflow-file-name", state.fileName);

    els.sidebarFileText.textContent = state.fileName;
    renderKpis(data.analysis, data.filename, data.shape);
    renderPreview(data.preview || []);
    renderAllCharts(data.analysis);

    els.aiStateBadge.textContent = "Ready";
    setStatus("Analysis complete. You can now generate AI insights.", "success");
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Something went wrong during analysis.", "error");
  } finally {
    els.analyzeBtn.disabled = false;
    els.analyzeBtn.textContent = "Analyze file";
  }
}

async function generateInsights() {
  if (!state.analysis) {
    setStatus("Analyze a file before generating AI insights.", "error");
    return;
  }

  els.generateInsightsBtn.disabled = true;
  els.generateInsightsBtn.textContent = "Generating...";
  els.aiStateBadge.textContent = "Generating";

  try {
    const response = await fetch(`${API_BASE}/api/insights`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: state.fileName || "uploaded file",
        analysis: state.analysis
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "AI insights failed.");
    }

    state.insights = data.insights;
    renderInsights(data.insights);
    setStatus("AI insights generated successfully.", "success");
  } catch (error) {
    console.error(error);
    els.aiStateBadge.textContent = "Error";
    setStatus(error.message || "Could not generate AI insights.", "error");
  } finally {
    els.generateInsightsBtn.disabled = false;
    els.generateInsightsBtn.textContent = "Generate AI insights";
  }
}

async function askQuestion(question) {
  if (!state.analysis) {
    setStatus("Analyze a file before asking AI questions.", "error");
    return;
  }

  const trimmedQuestion = (question || "").trim();
  if (!trimmedQuestion) {
    setStatus("Please type a question first.", "error");
    return;
  }

  els.askAiBtn.disabled = true;
  els.askAiBtn.textContent = "Thinking...";
  setStatus("AI is preparing an answer...");

  try {
    const response = await fetch(`${API_BASE}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: state.fileName || "uploaded file",
        analysis: state.analysis,
        question: trimmedQuestion
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Question answering failed.");
    }

    els.assistantResponse.textContent = data.answer || "No answer returned.";
    els.assistantResponse.style.color = "var(--color-text)";
  } catch (error) {
    console.error(error);
    setStatus(error.message || "Could not get an answer from AI.", "error");
  } finally {
    els.askAiBtn.disabled = false;
    els.askAiBtn.textContent = "Ask AI";
  }
}

function setCurrentFile(file) {
  state.file = file;
  els.sidebarFileText.textContent = file ? file.name : "No active dataset";
  if (file) {
    state.fileName = file.name;
    sessionStorage.setItem("insightflow-file-name", file.name);
    els.datasetName.textContent = file.name;
    els.datasetMeta.textContent = "File selected. Click analyze to process it.";
  }
}

function bindEvents() {
  els.themeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      applyTheme(currentTheme === "dark" ? "light" : "dark");
      if (state.analysis) {
        renderAllCharts(state.analysis);
      }
    });
  });

  if (els.fileInput) {
    els.fileInput.addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (file) setCurrentFile(file);
    });
  }

  els.analyzeBtn?.addEventListener("click", analyzeCurrentFile);
  els.generateInsightsBtn?.addEventListener("click", generateInsights);

  els.askAiBtn?.addEventListener("click", () => {
    askQuestion(els.questionInput.value);
  });

  els.promptChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      els.questionInput.value = chip.textContent.trim();
      askQuestion(chip.textContent.trim());
    });
  });
}

function initializeFromLanding() {
  const rememberedName = sessionStorage.getItem("insightflow-file-name");
  if (rememberedName) {
    els.sidebarFileText.textContent = rememberedName;
    els.datasetName.textContent = rememberedName;
    els.datasetMeta.textContent = "Please upload the file again and click analyze.";
  }
}

applyTheme(currentTheme);
bindEvents();
initializeFromLanding();