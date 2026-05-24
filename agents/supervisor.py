from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import ResearchState
from config import OPENAI_API_KEY, LLM_MODEL

llm = ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY)

async def supervisor_node(state: ResearchState) -> dict:
    topic = state["topic"]

    response = await llm.ainvoke([
        SystemMessage(content=(
            "You are a research planner. Break the given topic into 3-5 focused subtasks. "
            "Return ONLY a numbered list, one subtask per line. No extra text."
        )),
        HumanMessage(content=f"Topic: {topic}")
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
