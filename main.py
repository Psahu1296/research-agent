import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import ResearchRequest, ResearchResponse
from graph import research_graph
from memory.long_term import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("DB ready")
    yield

app = FastAPI(title="Research Agent", lifespan=lifespan)

@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/research", response_model=ResearchResponse)
async def run_research(req: ResearchRequest):
    session_id = req.session_id or str(uuid.uuid4())
    initial_state = {
        "topic": req.topic,
        "subtasks": [],
        "current_subtask_index": 0,
        "search_results": [],
        "final_report": "",
        "session_id": session_id,
    }
    result = await research_graph.ainvoke(initial_state)
    return ResearchResponse(
        topic=result["topic"],
        subtasks=result["subtasks"],
        report=result["final_report"],
    )
