import uuid
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from models import ResearchRequest, ResearchResponse
from graph import research_graph
from memory.long_term import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("DB ready")
    yield

app = FastAPI(title="Research Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest unchanged

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

@app.post("/research/stream")
async def stream_research(req: ResearchRequest):
    session_id = req.session_id or str(uuid.uuid4())
    initial_state = {
        "topic": req.topic,
        "subtasks": [],
        "current_subtask_index": 0,
        "search_results": [],
        "final_report": "",
        "session_id": session_id,
    }

    async def event_generator():
        async for event in research_graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            name = event.get("name", "")

            if kind == "on_chain_start" and name == "supervisor":
                yield f"data: {json.dumps({'type': 'status', 'data': 'Planning subtasks...'})}\n\n"

            elif kind == "on_chain_end" and name == "supervisor":
                subtasks = event["data"].get("output", {}).get("subtasks", [])
                for t in subtasks:
                    yield f"data: {json.dumps({'type': 'subtask', 'data': t})}\n\n"

            elif kind == "on_chain_start" and name == "searcher":
                state_in = event["data"].get("input", {})
                idx = state_in.get("current_subtask_index", 0)
                subtasks = state_in.get("subtasks", [])
                if idx < len(subtasks):
                    yield f"data: {json.dumps({'type': 'searching', 'data': subtasks[idx]})}\n\n"

            elif kind == "on_chain_start" and name == "analyst":
                yield f"data: {json.dumps({'type': 'status', 'data': 'Synthesizing report...'})}\n\n"

            elif kind == "on_chain_end" and name == "analyst":
                report = event["data"].get("output", {}).get("final_report", "")
                if report:
                    yield f"data: {json.dumps({'type': 'report', 'data': report})}\n\n"

            elif kind == "on_chain_end" and name == "LangGraph":
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
