from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import ResearchState
from memory.long_term import get_recent_sessions
from config import OPENAI_BASE_URL, OPENAI_API_KEY, LLM_MODEL

llm = ChatOpenAI(model=LLM_MODEL, base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)


async def analyst_node(state: ResearchState) -> dict:
    topic = state["topic"]
    findings = "\n\n".join(state["search_results"])
    past_sessions = await get_recent_sessions(limit=2)

    memory_context = ""
    if past_sessions:
        memory_context = "\n\nPast research context (from memory):\n" + "\n".join(
            f"- [{s['topic']}]: {s['report']}" for s in past_sessions
        )

    response = await llm.ainvoke([
        SystemMessage(content=(
            "You are a research analyst. Synthesize the findings into a structured markdown report. "
            "Include: Summary, Key Findings, and Conclusion sections. Be concise and factual."
        )),
        HumanMessage(content=(
            f"Topic: {topic}\n\n"
            f"Research findings:\n{findings}"
            f"{memory_context}"
        ))
    ])

    print(f"[analyst] report generated for: {topic}")
    return {"final_report": response.content}
