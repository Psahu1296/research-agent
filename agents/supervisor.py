from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import ResearchState
from config import OPENAI_BASE_URL, OPENAI_API_KEY, LLM_MODEL
from memory.long_term import get_recent_sessions

llm = ChatOpenAI(model=LLM_MODEL, base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)


async def supervisor_node(state: ResearchState) -> dict:
    topic = state["topic"]

    past_sessions = await get_recent_sessions(limit=2)
    memory_context = ""
    if past_sessions:
        memory_context = "\n\nPrevious research sessions:\n" + "\n".join(
            f"- [{s['topic']}]: {s['report'][:600]}" for s in past_sessions
        )

    response = await llm.ainvoke([
        SystemMessage(content=(
            "You are a research planner. Break the given topic into 3-5 focused subtasks. "
            "If previous research sessions are provided, build upon that knowledge — "
            "avoid repeating already covered ground and focus on gaps or follow-up angles. "
            "Return ONLY a numbered list, one subtask per line. No extra text."
        )),
        HumanMessage(content=f"Topic: {topic}{memory_context}")
    ])

    lines = response.content.strip().split("\n")
    subtasks = [
        line.lstrip("0123456789.-) ").strip()
        for line in lines if line.strip()
    ]

    if not subtasks:
        print("[supervisor] fallback: could not parse subtasks")
        subtasks = [topic]

    print(f"[supervisor] {len(subtasks)} subtasks for: {topic}")
    return {"subtasks": subtasks, "current_subtask_index": 0}
