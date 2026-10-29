from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):

    # Application
    app_name: str
    app_version: str
    debug: bool

    # Database
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    DATABASE_URL: str = ""

    # Gemini
    GEMINI_API_KEY: str = ""
    #Agentic LLM models
    CRM_MODEL: str = "gemini-3.1-flash-lite"

    SUMMARIZER_MODEL: str = "gemini-3.5-flash-lite"
    
    COMMERCE_MODEL : str = "gemini-3.5-flash-lite"
    
    SUPERVISOR_MODEL: str = "gemini-3.1-flash-lite"

    RESPONSE_GENERATOR_MODEL: str = "gemini-3.1-flash-lite"

    RESEARCH_MODEL: str = "gemini-3.5-flash-lite"

    PRODUCT_MODEL: str = "gemini-2.5-flash"

    FAQ_MODEL : str = "gemini-3.1-flash-lite"
    # Tavily
    TAVILY_API_KEY : str = ""
    # grok api key

    GROQ_API_KEY : str = ""

    # Google
    google_client_id: str = ""
    google_client_secret: str = ""

    # Meta
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_verify_token: str = ""

    # Security
    secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()