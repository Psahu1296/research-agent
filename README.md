# research-agent

Multi-agent research pipeline built with LangGraph. Given a topic, it decomposes the question into subtasks, searches the web per subtask, synthesizes a structured report, and persists sessions to Postgres for long-term memory.

## Architecture

```
POST /research
      │
      ▼
 supervisor ──► subtask list
      │
      ▼
 searcher (loops once per subtask, DuckDuckGo)
      │
      ▼
 analyst (synthesizes findings + injects past sessions from Postgres)
      │
      ▼
 save_memory ──► Postgres (long-term memory)
      │
      ▼
 JSON report
```

**Agents:**
- `supervisor` — LLM decomposes topic into 3–5 focused subtasks
- `searcher` — DuckDuckGo search per subtask; loops until all subtasks are covered
- `analyst` — LLM synthesizes all findings into a structured markdown report; injects the 2 most recent Postgres sessions as memory context

**Stack:** FastAPI · LangGraph · LangChain · OpenAI · DuckDuckGo (ddgs) · SQLAlchemy async · PostgreSQL · asyncpg

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4.1-nano
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

Run:
```bash
uvicorn main:app --reload --port 8002
```

## API

### `POST /research`

Full pipeline, returns complete JSON.

```bash
curl -X POST http://localhost:8002/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "LangGraph multi-agent systems"}'
```

Response:
```json
{
  "topic": "LangGraph multi-agent systems",
  "subtasks": ["What is LangGraph?", "How do agents communicate?", ...],
  "report": "## Summary\n..."
}
```

### `POST /research/stream`

Same pipeline, streams SSE events as each stage completes.

```bash
curl -X POST http://localhost:8002/research/stream \
  -H "Content-Type: application/json" \
  -d '{"topic": "LangGraph multi-agent systems"}' \
  --no-buffer
```

SSE event types:

| `type` | `data` |
|--------|--------|
| `status` | Human-readable milestone string |
| `subtask` | One subtask (emitted N times after planning) |
| `searching` | Subtask currently being searched |
| `report` | Full markdown report (at end) |
| `done` | Empty — pipeline complete |

### `GET /`

Health check.

## Key Design Decisions

- **Conditional loop edge:** LangGraph routes `searcher → searcher` until `current_subtask_index == len(subtasks)`, then routes to `analyst`. No manual loops.
- **Long-term memory:** Analyst receives the 2 most recent Postgres sessions as context, so the agent learns across separate research runs.
- **Free search:** DuckDuckGo via `ddgs` — no API key, no cost.
- **`Annotated[list, operator.add]`** on `search_results` in state — LangGraph merges instead of overwriting on each searcher loop.
