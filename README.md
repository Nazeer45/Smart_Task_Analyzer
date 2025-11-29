# Smart Task Analyzer

A mini full-stack application that intelligently scores and prioritizes tasks based on **urgency**, **importance**, **effort**, and **dependencies**.  
It helps users decide what to work on first, with multiple strategies and human-readable explanations for each task.

---

## 🚀 Setup Instructions

### Backend (Django + DRF)

```bash
cd backend
```

**Create virtual environment (recommended)**

```bash
python -m venv venv
```

**Activate environment**

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Apply migrations**

```bash
python manage.py migrate
```

**Run tests**

```bash
python manage.py test
```

**Start server**

```bash
python manage.py runserver
```

Your API will be available at:

- `http://localhost:8000/api/tasks/analyze/`
- `http://localhost:8000/api/tasks/suggest/`

> **Note:**  
> `/api/tasks/suggest/` is implemented as **POST** (not GET) because it requires a JSON body of tasks, which aligns with proper HTTP semantics.

---

### Frontend (HTML/CSS/JavaScript)

```bash
cd frontend
```

Start a simple static server:

```bash
python -m http.server 8080
```

Open in browser:

- `http://localhost:8080`

---

## 🧠 Algorithm Explanation

The Smart Task Analyzer computes a **priority score** for each task by combining:

- **Urgency**
- **Importance**
- **Effort**
- **Dependency impact**

The backend returns:

- A **0–100 priority score**
- A **score breakdown**
- A **human-readable explanation**

---

## 📊 Scoring Formula

Each factor receives a 0–10 score, and weights are applied:


	PRIORITY_SCORE = (urgency_score × urgency_weight) + (importance_score × importance_weight) + (effort_score × effort_weight) + (dependency_score × dependency_weight)


Final result is multiplied by 10 to get a 0–100 range.

---

## 🧩 Factors

### **1. Urgency**
- Based on `due_date`
- Overdue → max urgency  
- Today/tomorrow → high  
- Far deadlines → logarithmic decay

### **2. Importance**
- Direct user input (1–10)
- No transformation — preserves user intent

### **3. Effort**
- Inverse of `estimated_hours`
- Short tasks → higher score
- Long tasks → lower score

### **4. Dependencies**
- Tasks that block others receive higher scores
- DFS detects circular dependencies

---

## 🎛 Weight Strategies

### **Smart Balance (default)**
- Urgency: 0.35  
- Importance: 0.35  
- Effort: 0.20  
- Dependency: 0.10  

### **Fastest Wins**
- Urgency: 0.10  
- Importance: 0.10  
- Effort: 0.70  
- Dependency: 0.10  

### **High Impact**
- Urgency: 0.20  
- Importance: 0.60  
- Effort: 0.10  
- Dependency: 0.10  

### **Deadline Driven**
- Urgency: 0.60  
- Importance: 0.20  
- Effort: 0.10  
- Dependency: 0.10  

---

## 💬 Explanations

Each task receives a natural-language explanation such as:

- "High urgency due to near deadline"  
- "Very important task"  
- "Quick win – low effort"  
- "Blocks multiple tasks"

Both **analyze** and **suggest** endpoints include explanations.

---

## 🔌 API Endpoints

### **POST `/api/tasks/analyze/`**

Analyze and sort tasks by priority.

**Request example:**

```json
{
  "strategy": "smart_balance",
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "due_date": "2025-12-01T10:00:00",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}
```

**Response example:**

```json
{
  "strategy": "smart_balance",
  "count": 1,
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "priority_score": 78.5,
      "score_breakdown": {
        "urgency": 9.0,
        "importance": 8.0,
        "effort": 6.7,
        "dependency": 0.0
      },
      "explanation": "High urgency (due very soon) - Very important task"
    }
  ]
}
```

---

### **POST `/api/tasks/suggest/`**

Returns the top 3 tasks the user should work on today.

**Request:**

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "due_date": "2025-12-01T10:00:00",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ]
}
```

**Response:**

```json
{
  "suggested_tasks": [
    {
      "id": 1,
      "title": "Fix login bug",
      "priority_score": 78.5,
      "score_breakdown": { "...": "..." },
      "explanation": "High urgency (due very soon) - Very important task"
    }
  ],
  "reason": "Top 3 tasks picked for today based on urgency, importance, effort and dependencies."
}
```

---

## ⚙️ Design Decisions & Trade-offs

- **POST instead of GET for `/suggest/`**  
  Required to send JSON task lists.

- **Capped urgency for overdue tasks**  
  Keeps scores readable.

- **Effort weighted moderately**  
  Quick wins help but don't overshadow critical tasks.

- **Frontend stores tasks in memory**  
  Simplifies assignment; no DB required.

- **Backend generates explanations**  
  Ensures consistent reasoning everywhere.

---

## 🧪 Tests

Unit tests cover:

- Overdue urgency  
- Quick-win effort scoring  
- Circular dependency detection  
- Strategy differences  
- Weight validation  

Run:

```bash
cd backend
python manage.py test
```