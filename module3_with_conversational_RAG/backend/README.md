# Company Handbook Q&A – Backend

> FastAPI · LangGraph · Groq · Qdrant · PostgreSQL

---

## Architecture

```
User question
     │
     ▼
FastAPI  POST /api/ask
     │
     ▼
LangGraph pipeline
  ┌─────────────────────────────────────────┐
  │  retrieve_node                          │
  │    embed question (MiniLM-L6-v2)        │
  │    cosine search → Qdrant top-k chunks  │
  │                                         │
  │  generate_node                          │
  │    build RAG prompt                     │
  │    call Groq (llama3-70b-8192)          │
  │                                         │
  │  format_node                            │
  │    assemble AskResponse dict            │
  └─────────────────────────────────────────┘
     │
     ▼
Persist QALog → PostgreSQL
     │
     ▼
Return structured JSON response
```

---

## Quick Start

### 1 – Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Docker + Compose | v2+ |
| Groq API key | [console.groq.com](https://console.groq.com) |

---

### 2 – Clone & configure

```bash
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

---

### 3 – Start infrastructure

```bash
docker compose up -d
# Postgres on :5432  |  Qdrant on :6333
```

---

### 4 – Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### 5 – Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```



Interactive docs → http://localhost:8000/docs

---

### 6 – Ingest the handbook

```bash
curl -X POST http://localhost:8000/api/ingest
```

Drop additional `.txt` or `.pdf` files into `data/handbook/` and call `/api/ingest` again.  
Re-ingesting a file replaces its existing chunks.

---

### 7 – Ask a question

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many days of annual leave do I get?", "top_k": 4}'
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Postgres + Qdrant connectivity |
| POST | `/api/ingest` | Ingest documents from `data/handbook/` |
| GET | `/api/documents` | List ingested documents |
| POST | `/api/ask` | Ask a question, get a structured answer |
| GET | `/api/history` | Recent Q&A log entries |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory & startup
│   ├── config.py            # Pydantic-settings (env vars)
│   ├── models/
│   │   ├── schemas.py       # Request / response Pydantic models
│   │   └── db_models.py     # SQLAlchemy ORM (Document, Chunk, QALog)
│   ├── db/
│   │   ├── postgres.py      # Engine, session, init_db()
│   │   └── qdrant.py        # Client, init_collection(), health check
│   ├── services/
│   │   ├── embeddings.py    # SentenceTransformer wrapper
│   │   ├── ingestion.py     # Load → chunk → embed → upsert
│   │   └── retriever.py     # Cosine search in Qdrant
│   ├── graph/
│   │   ├── state.py         # QAState TypedDict
│   │   ├── nodes.py         # retrieve / generate / format nodes
│   │   └── pipeline.py      # Compile & run the LangGraph
│   └── routers/
│       ├── qa.py            # /api/ask  /api/history
│       └── ingest.py        # /api/ingest  /api/documents
├── data/handbook/           # Drop .txt / .pdf files here
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

---

## Environment Variables

| Variable | Default | Notes |
|----------|---------|-------|
| `GROQ_API_KEY` | – | **Required** |
| `GROQ_MODEL` | `llama3-70b-8192` | Any Groq-supported model |
| `POSTGRES_*` | `postgres/postgres/handbook_db/localhost/5432` | |
| `QDRANT_HOST` | `localhost` | |
| `QDRANT_PORT` | `6333` | |
| `QDRANT_COLLECTION` | `handbook_chunks` | |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | 384-dim, CPU-friendly |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
