import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "hermes-fast")


_raw_db_url = os.getenv("DATABASE_URL", "")
DATABASE_URL = _raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

