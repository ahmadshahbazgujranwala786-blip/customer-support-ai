"""HTTP API adapter for the CustomerSupport multi-agent backend.

Run from this project directory with:
    python -m uvicorn web_api:app --reload --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("customer_support.web_api")

app = FastAPI(
    title="Customer Support API",
    version="1.0.0",
    description="Website API adapter for the existing multi-agent customer-support service.",
)

origins = [
    value.strip()
    for value in os.getenv(
        "FRONTEND_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if value.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    user_id: str = Field(min_length=1, max_length=100)
    channel: str = Field(default="web", min_length=1, max_length=50)
    sender_name: str = Field(default="Website Visitor", max_length=100)


@app.get("/")
def root() -> FileResponse:
    # The root URL is the public customer-facing website; API health is /health.
    return FileResponse(str(Path(__file__).resolve().parent / "frontend" / "index.html"))


@app.get("/health")
def health() -> dict[str, str]:
    # This confirms that the HTTP API is running. It does not guarantee that
    # database credentials, the knowledge collection, or model keys are valid.
    return {"service": "customer-support-api", "status": "ok"}


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message must not be empty.")

    db = None
    try:
        # Validate the app-specific environment before importing model agents.
        # That makes missing local configuration visible to the website instead
        # of returning only a generic "backend could not process" message.
        from core.config import settings

        missing = []
        if not settings.GEMINI_API_KEY.strip():
            missing.append("GEMINI_API_KEY")
        if not settings.DATABASE_URL.strip() and settings.db_password.strip().upper() in {"", "CHANGE_ME"}:
            missing.append("db_password")

        if missing:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Customer Support configuration is incomplete. Set "
                    + ", ".join(missing)
                    + " in the project-root .env file, then retry the message. "
                    "Do not paste API keys into chat."
                ),
            )

        # Defer heavyweight backend imports until a chat request arrives so
        # /health can still help diagnose deployment/setup problems.
        from app.database.session import SessionLocal
        from app.tools.Conversation.ConversationService import ConversationService

        db = SessionLocal()
        service = ConversationService(db)
        reply = service.process_user_message(
            user_id=request.user_id,
            channel=request.channel,
            sender_name=request.sender_name,
            message=message,
        )
        if reply is None or not str(reply).strip():
            raise HTTPException(
                status_code=502,
                detail="The support workflow completed without producing a reply.",
            )
        text = str(reply).strip()
        return {"reply": text, "final_response": text}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Customer-support request failed during backend initialization or processing.")
        raise HTTPException(
            status_code=503,
            detail=(
                "The support backend could not process this message. Check the API terminal, "
                "Python dependencies, .env configuration, PostgreSQL connection, knowledge-base "
                "collection, and AI provider keys."
            ),
        ) from None
    finally:
        if db is not None:
            db.close()


# Serve the chat UI and API from the same origin so the ngrok URL exposes the
# complete website, not just the JSON API. Keep this mount after API routes.
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
