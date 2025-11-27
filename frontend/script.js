const API_BASE = "http://localhost:8000/api/tasks";

const state = {
  tasks: [],
};

const taskForm = document.getElementById("taskForm");
const bulkJson = document.getElementById("bulkJson");
const bulkAddBtn = document.getElementById("bulkAddBtn");
const tasksList = document.getElementById("tasksList");
const analyzeBtn = document.getElementById("analyzeBtn");
const suggestBtn = document.getElementById("suggestBtn");
const resultsDiv = document.getElementById("results");
const errorDiv = document.getElementById("error");
const strategySelect = document.getElementById("strategySelect");

taskForm.addEventListener("submit", (e) => {
  e.preventDefault();
  addSingleTask();
});

bulkAddBtn.addEventListener("click", addBulkTasks);
analyzeBtn.addEventListener("click", analyzeTasks);
suggestBtn.addEventListener("click", suggestTasks);

function addSingleTask() {
  clearError();

  const title = document.getElementById("title").value.trim();
  const due = document.getElementById("dueDate").value;
  const hours = parseFloat(document.getElementById("hours").value);
  const importance = parseInt(document.getElementById("importance").value, 10);
  const depsRaw = document.getElementById("dependencies").value.trim();

  if (!title || !due || !hours || !importance) {
    showError("Please fill all required fields.");
    return;
  }

  const dependencies =
    depsRaw.length === 0
      ? []
      : depsRaw
          .split(",")
          .map((x) => parseInt(x.trim(), 10))
          .filter((x) => !Number.isNaN(x));

  const task = {
    id: Date.now(),
    title,
    due_date: new Date(due).toISOString(),
    estimated_hours: hours,
    importance,
    dependencies,
  };

  state.tasks.push(task);
  renderTasks();
  taskForm.reset();
}

function addBulkTasks() {
  clearError();
  if (!bulkJson.value.trim()) {
    showError("Paste a JSON array of tasks first.");
    return;
  }
  try {
    const arr = JSON.parse(bulkJson.value);
    if (!Array.isArray(arr)) {
      showError("Bulk JSON must be an array.");
      return;
    }
    arr.forEach((t, idx) => {
      if (!t.id) t.id = Date.now() + idx;
    });
    state.tasks = state.tasks.concat(arr);
    renderTasks();
    bulkJson.value = "";
  } catch (e) {
    showError("Invalid JSON: " + e.message);
  }
}

function renderTasks() {
  if (state.tasks.length === 0) {
    tasksList.innerHTML = "<p>No tasks yet.</p>";
    return;
  }
  tasksList.innerHTML = state.tasks
    .map(
      (t) => `
      <div class="task">
        <div><strong>${escapeHtml(t.title)}</strong></div>
        <div>Due: ${new Date(t.due_date).toLocaleString()}</div>
        <div>Effort: ${t.estimated_hours}h | Importance: ${t.importance}/10</div>
        ${
          t.dependencies && t.dependencies.length
            ? `<div>Depends on: ${t.dependencies.join(", ")}</div>`
            : ""
        }
      </div>
    `
    )
    .join("");
}

async function analyzeTasks() {
  if (state.tasks.length === 0) {
    showError("Add at least one task first.");
    return;
  }
  clearError();
  resultsDiv.innerHTML = "Analyzing...";

  try {
    const strategy = strategySelect.value;
    const res = await fetch(`${API_BASE}/analyze/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ strategy, tasks: state.tasks }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "API error");
    }
    const data = await res.json();
    renderResults(data.tasks, `Analyzed with strategy: ${strategy}`);
  } catch (e) {
    showError(e.message);
    resultsDiv.innerHTML = "";
  }
}

async function suggestTasks() {
  if (state.tasks.length === 0) {
    showError("Add at least one task first.");
    return;
  }
  clearError();
  resultsDiv.innerHTML = "Fetching suggestions...";

  try {
    const res = await fetch(`${API_BASE}/suggest/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tasks: state.tasks }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || "API error");
    }
    const data = await res.json();
    renderResults(
      data.suggested_tasks,
      "Suggested top 3 tasks for today (with explanations)."
    );
  } catch (e) {
    showError(e.message);
    resultsDiv.innerHTML = "";
  }
}

function renderResults(tasks, heading) {
  if (!tasks || tasks.length === 0) {
    resultsDiv.innerHTML = "<p>No results.</p>";
    return;
  }
  const html = tasks
    .map((t) => {
      const lvl = priorityLevel(t.priority_score);
      return `
      <div class="task-result ${lvl}">
        <div>
          <strong>${escapeHtml(t.title)}</strong>
          <span class="badge ${lvl}">${lvl.toUpperCase()}</span>
        </div>
        <div>Score: ${t.priority_score.toFixed?.(2) ?? t.priority_score}</div>
        <div>Due: ${new Date(t.due_date).toLocaleString()}</div>
        <div>Effort: ${t.estimated_hours}h | Importance: ${t.importance}/10</div>
        <div>Explanation: ${escapeHtml(t.explanation || "")}</div>
      </div>
    `;
    })
    .join("");
  resultsDiv.innerHTML = `<p>${heading}</p>${html}`;
}

function priorityLevel(score) {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
}

function showError(msg) {
  errorDiv.textContent = msg;
}

function clearError() {
  errorDiv.textContent = "";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = String(str);
  return div.innerHTML;
}
