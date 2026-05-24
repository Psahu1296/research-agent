from langgraph.graph import StateGraph, START, END
from state import ResearchState
from agents.supervisor import supervisor_node
from agents.searcher import searcher_node
from agents.analyst import analyst_node
from memory.long_term import save_session

async def save_memory_node(state: ResearchState) -> dict:
    await save_session(topic=state["topic"], report=state["final_report"])
    print(f"[memory] session saved for: {state['topic']}")
    return {}

def should_keep_searching(state: ResearchState) -> str:
    idx = state["current_subtask_index"]
    total = len(state["subtasks"])
    if idx < total:
        return "search"
    return "analyze"

def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("searcher", searcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("save_memory", save_memory_node)

    graph.add_edge(START, "supervisor")
    graph.add_edge("supervisor", "searcher")
    graph.add_conditional_edges(
        "searcher",
        should_keep_searching,
        {"search": "searcher", "analyze": "analyst"}
    )
    graph.add_edge("analyst", "save_memory")
    graph.add_edge("save_memory", END)

    return graph.compile()

research_graph = build_graph()
