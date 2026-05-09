The issue is the code blocks inside the README are breaking the formatting. Here is the complete fixed version — Ctrl+A → Delete → Paste → Ctrl+S:
# 🎬 StreamVault AI Insights
### Secure AI-Powered Internal Analytics Assistant

> A production-grade, multi-source AI analytics assistant for StreamVault Entertainment's leadership team. Built with FastAPI + Groq (Llama 3.3) + React.

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐   │
│  │  Chat UI    │  │  Charts Tab  │  │  Documents Search Tab    │   │
│  │  (AI Asst.) │  │  (Recharts)  │  │  (PDF Content Browser)   │   │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬─────────────┘   │
│         └────────────────┼─────────────────────────┘                │
│                          │ HTTP/REST (axios)                         │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│                      BACKEND (FastAPI / Python)                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  POST /api/chat/    GET /api/analytics/*   GET /api/documents │   │
│  └───────────────────┬──────────────────────────────────────────┘   │
│  ┌───────────────────▼────────────────────────────────────────────┐ │
│  │              AI Orchestration Service (3-Step Loop)             │ │
│  │  Step 1: Router Call  model outputs JSON to pick a tool        │ │
│  │  Step 2: Tool Executor  fetches real data from DB or PDFs      │ │
│  │  Step 3: Answer Call  model writes final answer from data      │ │
│  └───────────────────┬────────────────────────────────────────────┘ │
│  ┌───────────────────▼────────────────────────────────────────────┐ │
│  │  query_structured_data  search_documents  get_top_titles        │ │
│  │  get_trending_analysis  compare_titles    get_regional          │ │
│  │  get_genre_performance                                          │ │
│  └──────────┬──────────────────────────────┬───────────────────── │
│  ┌──────────▼────────────┐  ┌──────────────▼──────────────────┐   │
│  │  SQLite Database      │  │  PDF Document Store             │   │
│  │  movies               │  │  quarterly_executive_report.pdf  │   │
│  │  viewers              │  │  campaign_performance_summary    │   │
│  │  watch_activity       │  │  audience_behavior_report        │   │
│  │  reviews              │  │  content_roadmap                 │   │
│  │  marketing_spend      │  │  policy_guidelines               │   │
│  │  regional_performance │  │                                  │   │
│  └───────────────────────┘  └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free Groq API key from https://console.groq.com — no credit card required
- (Optional) Docker + Docker Compose

---

### Step 1 — Get Free Groq API Key
1. Go to https://console.groq.com
2. Sign up for free
3. Click **API Keys** then **Create API Key**
4. Copy the key starting with `gsk_`

### Step 2 — Set Up Environment

```bash
git clone <your-repo-url>
cd secure-ai-insights
cp .env.example .env
```

Open `.env` and set:

```
ANTHROPIC_API_KEY=gsk_your_groq_key_here
```

### Step 3 — Start the Backend

```bash
cd backend
pip install -r requirements.txt
pip install groq
```

Windows:

```cmd
C:\Users\<you>\AppData\Local\Programs\Python\Python312\python.exe -m uvicorn app.main:app --reload --port 8000
```

Linux / Mac:

```bash
uvicorn app.main:app --reload --port 8000
```

On startup the backend will:
- Load all 6 CSV files into SQLite automatically
- Index all 5 PDF documents
- Print: `=== Ready to serve requests ===`

API docs: http://localhost:8000/docs

### Step 4 — Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

### Option B — Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

---

## 🗂️ Project Structure

```
secure-ai-insights/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup lifecycle
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── database.py          # SQLite, CSV ingestion, safe query guard
│   │   ├── routers/
│   │   │   ├── chat.py          # POST /api/chat/
│   │   │   ├── analytics.py     # GET /api/analytics/*
│   │   │   └── documents.py     # GET /api/documents/*
│   │   ├── services/
│   │   │   ├── ai_service.py    # Groq 3-step manual routing loop
│   │   │   └── pdf_service.py   # PDF extraction and keyword index
│   │   └── tools/
│   │       └── executor.py      # Tool implementations, safe read-only
│   ├── data/
│   │   ├── csv/                 # 6 synthetic CSV files
│   │   ├── pdf/                 # 5 synthetic PDF reports
│   │   └── db/                  # SQLite DB auto-created on startup
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Layout, sidebar, tab navigation
│   │   ├── App.css              # Dark theme design system
│   │   ├── api.js               # Axios client
│   │   └── components/
│   │       ├── ChatPanel.jsx    # AI chat with tool trace display
│   │       ├── ChartsPanel.jsx  # 6 live chart visualizations
│   │       ├── DocumentsPanel.jsx  # PDF search interface
│   │       └── StatsBar.jsx     # Live KPI stats bar
│   ├── vite.config.js
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🛠️ API Reference

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Send message, get AI answer with tool trace |
| GET | `/api/chat/suggested-questions` | Preset example questions |

**Request:**

```json
{
  "message": "Which titles performed best in 2025?",
  "conversation_history": []
}
```

**Response:**

```json
{
  "answer": "Based on the database, the top title is Stellar Run...",
  "tool_trace": [{"tool": "get_top_titles", "input": {}, "result_preview": "10 rows returned"}],
  "model": "llama-3.3-70b",
  "sources_used": ["get_top_titles"]
}
```

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/overview-stats` | Dashboard KPIs |
| GET | `/api/analytics/top-titles` | Top titles by views |
| GET | `/api/analytics/genre-trends` | Genre performance over time |
| GET | `/api/analytics/regional-heatmap` | City engagement data |
| GET | `/api/analytics/marketing-efficiency` | Spend vs conversions |
| GET | `/api/analytics/audience-segments` | Viewer segment breakdown |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents/` | List all indexed PDFs |
| GET | `/api/documents/search?q=...` | Keyword search across documents |

---

## 🔒 Security Architecture

### 1. Tool-Based Access Control
The AI never touches the database directly. Every request flows through:

```
User Query → AI Model → Tool Call → Executor → Safe Query → DB or PDFs
```

### 2. SQL Injection Prevention
- Only SELECT statements allowed, enforced in `database.py`
- Blocked keywords: `DROP, DELETE, INSERT, UPDATE, ALTER, CREATE, EXEC`
- User inputs sanitized before SQL interpolation
- Hard cap of 500 rows per query

### 3. Input Validation
- All API inputs validated by Pydantic with strict constraints
- Message max length: 2000 characters
- Role field restricted to `user` or `assistant` only

### 4. Secret Management
- API key loaded from `.env` only, never hardcoded in source
- `.env` in `.gitignore`, never committed to version control
- Docker uses environment variable injection

### 5. CORS Protection
- Explicit allowed origins configured in `config.py`
- Only GET and POST methods accepted

### 6. Data Privacy
- Dataset is fully synthetic, no real PII included
- All tool results logged in trace for auditability

---

## 🤖 AI Tool Calling Architecture

**Model:** Llama 3.3 70B via Groq Cloud API (free tier)

### 3-Step Manual Routing Pattern

```
Step 1 — Router Call (no function calling)
          Model outputs plain JSON: {"tool": "name", "args": {}}
          We parse it ourselves — eliminates all Groq 400 errors

Step 2 — Execute the selected tool
          Fetch real data from SQLite database or PDF index

Step 3 — Answer Call (no function calling)
          Model writes the final answer using the fetched data
```

> This approach avoids Groq's native function calling entirely, which is known to cause malformed syntax errors with Llama 3. All tool routing is handled by parsing plain JSON output from the model.

### Available Tools

| Tool | Source | Purpose |
|------|--------|---------|
| `get_top_titles` | SQLite | Top movies by total views |
| `get_trending_analysis` | SQLite | Recent vs historical view comparison |
| `compare_titles` | SQLite | Side-by-side movie comparison |
| `get_regional_engagement` | SQLite | City-level engagement metrics |
| `get_genre_performance` | SQLite | Genre trends over time |
| `search_documents` | PDF index | Qualitative insights from reports |
| `query_structured_data` | SQLite | Custom ad-hoc SELECT queries |

---

## 📊 Example Questions

| Question | Tool Used | Source |
|----------|-----------|--------|
| Which titles performed best in 2025? | `get_top_titles` | SQL |
| Why is Stellar Run trending recently? | `get_trending_analysis` | SQL |
| Compare Dark Orbit vs Last Kingdom | `compare_titles` | SQL |
| Which city had strongest engagement? | `get_regional_engagement` | SQL |
| What explains weak comedy performance? | `get_genre_performance` | SQL |
| What recommendations for leadership? | `search_documents` | PDF |

---

## ⚙️ Configuration

All settings in `backend/app/config.py`, loaded from `.env`:

```env
# Your Groq API key from console.groq.com (free, no card)
ANTHROPIC_API_KEY=gsk_your_groq_key_here

DEBUG=false
MAX_TOKENS=2048
ALLOWED_ORIGINS=["http://localhost:3000"]
```

> The variable is named `ANTHROPIC_API_KEY` for legacy compatibility but stores your Groq API key.

---

## 📦 Tech Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| AI Model | Llama 3.3 70B via Groq | Free, fast inference, strong reasoning |
| AI API | Groq Cloud | Free tier, OpenAI-compatible |
| Backend | FastAPI + Python 3.12 | Fast, async, excellent typing |
| Database | SQLite + SQLAlchemy | Zero-config, no server needed |
| PDF Parsing | PyPDF2 | Lightweight text extraction |
| Frontend | React 18 + Vite | Fast HMR, modern tooling |
| Charts | Recharts | Composable, responsive |
| HTTP Client | Axios | Clean interceptors and error handling |
| Containers | Docker + Compose | Portable deployment |

---

## 🧪 Assumptions and Tradeoffs

### Assumptions
1. SQLite is appropriate for demo scale. Production would use PostgreSQL.
2. Keyword PDF search works for 5 documents. Production would use vector embeddings.
3. No authentication implemented. Assumed to run behind VPN or SSO in production.
4. All data is synthetically generated, not from a real business system.
5. Manual JSON routing used instead of native function calling to avoid Llama 3 instability.

### Tradeoffs

| Decision | Chosen | Alternative | Reason |
|----------|--------|-------------|--------|
| AI Provider | Groq free tier | OpenAI, paid APIs | Zero cost, sufficient capability |
| Tool Routing | Manual JSON parsing | Groq function calling | Eliminates 400 errors from Llama 3 |
| PDF Search | Keyword matching | Vector embeddings | No GPU or extra install needed |
| Database | SQLite | PostgreSQL | No infrastructure overhead for demo |
| Frontend state | React useState | Redux or Zustand | Unnecessary complexity at this scale |
| Auth | None | JWT or OAuth | Out of scope for internal demo tool |

---

## 📈 Extending the Project

- **Switch model** — change `llama-3.3-70b-versatile` in `ai_service.py` to any Groq-supported model
- **Add vector search** — replace `pdf_service.py` with ChromaDB and sentence-transformers
- **Add PostgreSQL** — update `DATABASE_URL` in `.env`, SQLAlchemy handles the rest
- **Add authentication** — use `python-jose` and FastAPI dependency injection for JWT
- **Add streaming** — use `groq.stream()` with FastAPI `StreamingResponse` for real-time output
- **Add Redis caching** — cache frequent analytics queries to reduce latency
- **Add more tools** — implement in `executor.py` and register in `ai_service.py`

---

*Built for Futures First — Quantitative Engineer Assessment*