from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    topic: str                                        # original user query
    subtasks: list[str]                               # supervisor breaks topic into these
    current_subtask_index: int                        # which subtask we're working on
    search_results: Annotated[list[str], operator.add] # searcher appends findings here
    final_report: str                                 # analyst writes this at the end
    session_id: str                                   # for Postgres memory storage
