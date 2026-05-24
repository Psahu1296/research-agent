import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

_raw_db_url = os.getenv("DATABASE_URL", "")
DATABASE_URL = _raw_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

