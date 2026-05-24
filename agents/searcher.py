from ddgs import DDGS
from state import ResearchState

def _search(query: str, max_results: int = 4) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"[no results] {query}"
        return "### " + query + "\n" + "\n".join(
            f"- {r['title']}: {r['body']}" for r in results
        )
    except Exception as e:
        print(f"[searcher] search failed: {e}")
        return f"[search error] Could not fetch results for: {query}"

async def searcher_node(state: ResearchState) -> dict:
    idx = state["current_subtask_index"]
    subtask = state["subtasks"][idx]

    print(f"[searcher] subtask {idx + 1}: {subtask}")
    result = _search(subtask)

    return {
        "search_results": [result],
        "current_subtask_index": idx + 1
    }
