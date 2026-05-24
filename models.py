from pydantic import BaseModel

class ResearchRequest(BaseModel):
    topic: str
    session_id: str = "default"

class ResearchResponse(BaseModel):
    topic: str
    subtasks: list[str]
    report: str
