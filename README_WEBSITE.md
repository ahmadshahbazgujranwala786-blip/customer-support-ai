# Customer Support Website

This folder adds a browser-based chat interface to the existing Python multi-agent customer-support project.

## What's included

- `frontend/index.html` — responsive website structure and chat workspace.
- `frontend/styles.css` — responsive dark/light visual design.
- `frontend/app.js` — chat UI, local conversation history, connection check, and API calls.
- `web_api.py` — FastAPI HTTP adapter around the existing `ConversationService`.
- `requirements.txt` — Python packages used by the HTTP adapter and existing agents.
- `.env.example` — template for local configuration.
- `run_customer_support.bat` — launcher for the API and website.

## First-time setup

1. Install Python 3.11 or a compatible version and PostgreSQL. Confirm the existing `customer_support` database and required tables/knowledge-base data are available.
2. Open PowerShell in this project directory and create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and enter the correct PostgreSQL credentials and the Google Gemini API key. Add Tavily/Groq keys for the features that use those providers. Do not place API keys in the frontend.
4. Check the existing ChromaDB data is available at the project-root `chroma_db` path and that the `knowledge_base_embeddings` collection exists.
5. Initialize the project tables if needed:

   ```powershell
   python -m app.database.init_db
   ```

   This command creates mapped tables; it does not populate business knowledge or migrate a knowledge base.

## Run the website

After completing the setup, run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_api:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, from the project root:

```powershell
.\.venv\Scripts\python.exe -m http.server 5173 --bind 127.0.0.1 --directory frontend
```

Open **http://127.0.0.1:5173/**. The website calls `http://127.0.0.1:8000/api/chat`. The API health check is `http://127.0.0.1:8000/health`.

The `run_customer_support.bat` launcher can start both processes after a working `.env` file is in place.

## Chat API contract

`POST /api/chat`

Request JSON:

```json
{
  "message": "Where is my order?",
  "user_id": "stable-browser-visitor-id",
  "channel": "web",
  "sender_name": "Website Visitor"
}
```

Successful response JSON:

```json
{
  "reply": "The support assistant's answer."
}
```

The API delegates each chat request to the existing `ConversationService`. A healthy `/health` response confirms the HTTP process is running, not that the database, vector collection, AI provider credentials or every agent are configured correctly.

## Notes

- Conversation history is saved in the current browser's local storage. It is local to that browser profile and is not synchronized across devices.
- The interface does not invent assistant answers when the API fails; it shows a service error instead.
- This is a local development setup. Before public deployment, configure HTTPS, a production database and persistent vector storage, restrict CORS to the real website origin, review authentication/rate limiting and privacy requirements, and remove sensitive debug logging.
