# ============================================================
# AI Medical Consultant - Configuration
# ============================================================
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # --- LLM Configuration ---
    LLM_API_KEY: str = "sk-e63595f598c34bf3a8affebbbc0be260"
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # --- Embedding ---
    EMBEDDING_API_KEY: str = "sk-ws-H.RYDXILX.lcAZ.MEQCIEd7B6oQPCRdNaYb7chKKh2oxg2hnApeN3l5EUPWE-A8AiBNzVhzmYYNb7nO4gfCZdWV_yty00q3uvjH3RiKq8ALTQ"
    EMBEDDING_MODEL: str = "text-embedding-v1"

    # --- Database ---
    # 默认使用 SQLite（本地开发），生产环境使用 PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/medical.db"
    DATABASE_URL_SYNC: str = "sqlite:///./data/medical.db"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- FAISS ---
    FAISS_INDEX_PATH: str = "./data/faiss_index"
    VECTOR_DIMENSION: int = 1536

    # --- JWT ---
    SECRET_KEY: str = "medical-consultant-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: str = '["*"]'

    # --- Knowledge Base ---
    MEDICAL_KB_PATH: str = "./data/medical_kb"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_cors_origins(self) -> List[str]:
        import json
        try:
            return json.loads(self.CORS_ORIGINS)
        except Exception:
            return ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
