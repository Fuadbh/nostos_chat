from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Any, Dict
import asyncio

import httpx
from ddgs import DDGS


app = FastAPI()

# 1. Setup CORS middleware
# This allows the frontend (which is served from a local file or different port)
# to make requests to the backend API.
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*" # Allows all origins for development (CHANGE THIS LATER!)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Simple test endpoint
@app.get("/")
def read_root():
    return {"message": "Nostos Chat Backend is running!"}

# 2.5. Check search configuration
@app.get("/api/search-config")
def check_search_config():
    """Check which search engine is configured"""
    google_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_cx = os.getenv("GOOGLE_SEARCH_CX")
    
    config = {
        "google_configured": bool(google_key and google_cx),
        "google_key_set": bool(google_key),
        "google_cx_set": bool(google_cx),
        "default_search": "google" if (google_key and google_cx) else "duckduckgo"
    }
    return config

# --- Ollama configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"


# 3. Endpoint to list available Ollama models
@app.get("/api/models")
async def list_models():
    """
    Returns a list of available Ollama models.
    Shape:
    {
        "models": ["model-name-1", "model-name-2", ...]
    }
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(OLLAMA_TAGS_ENDPOINT)

        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama tags error (status {resp.status_code}): {resp.text}",
            )

        data = resp.json() or {}
        # Ollama /api/tags returns {"models": [{ "name": "model-name", ...}, ...]}
        models_raw = data.get("models") or []
        model_names = [m.get("name") for m in models_raw if m.get("name")]

        return {"models": model_names}

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach Ollama at {OLLAMA_BASE_URL}: {str(e)}",
        )


async def perform_web_search(query: str, max_results: int = 5):
    """
    Perform a web search. Prefers Google Custom Search if GOOGLE_SEARCH_API_KEY and
    GOOGLE_SEARCH_CX are set; otherwise falls back to DuckDuckGo.

    Returns a tuple of (formatted_results, source), where source is one of
    "google", "duckduckgo", or None if no results.
    """
    google_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_cx = os.getenv("GOOGLE_SEARCH_CX")

    # Try Google Custom Search first if configured
    if google_key and google_cx:
        try:
            params = {
                "key": google_key,
                "cx": google_cx,
                "q": query,
                "num": max_results,
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://www.googleapis.com/customsearch/v1", params=params)

            if resp.status_code == 200:
                data = resp.json() or {}
                items = data.get("items") or []
                if not items:
                    print("Google search returned no items, falling back to DuckDuckGo")
                    # Fall through to DuckDuckGo
                else:
                    formatted_results = "\n\n=== Web Search Results (Google) ===\n"
                    for i, item in enumerate(items, 1):
                        title = item.get("title", "No title")
                        snippet = item.get("snippet", "No description")
                        link = item.get("link", "")
                        formatted_results += f"\n[{i}] {title}\n{snippet}\nSource: {link}\n"
                    formatted_results += "\n=== End of Search Results ===\n\n"
                    return formatted_results, "google"
            else:
                error_data = resp.text
                try:
                    error_json = resp.json()
                    error_data = error_json.get("error", {}).get("message", error_data)
                except:
                    pass
                print(f"Google search error: status {resp.status_code} - {error_data}")
                print("Falling back to DuckDuckGo")
        except Exception as e:
            print(f"Google search exception: {e}")
            print("Falling back to DuckDuckGo")
    else:
        if not google_key:
            print("GOOGLE_SEARCH_API_KEY not set, using DuckDuckGo")
        if not google_cx:
            print("GOOGLE_SEARCH_CX not set, using DuckDuckGo")

    # Fallback: DuckDuckGo (no key needed)
    try:
        loop = asyncio.get_event_loop()
        with DDGS() as ddgs:
            results = await loop.run_in_executor(
                None,
                lambda: list(ddgs.text(query, max_results=max_results))
            )

        if not results:
            return "", None

        formatted_results = "\n\n=== Web Search Results (DuckDuckGo) ===\n"
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            body = result.get("body", "No description")
            url = result.get("href", "")
            formatted_results += f"\n[{i}] {title}\n{body}\nSource: {url}\n"
        formatted_results += "\n=== End of Search Results ===\n\n"

        return formatted_results, "duckduckgo"
    except Exception as e:
        # If search fails, return empty string (don't break the chat)
        print(f"DuckDuckGo search error: {e}")
        return "", None


# 4. Chat endpoint that forwards requests to a local Ollama server
@app.post("/api/chat")
async def chat(message: Dict[str, Any]):
    """
    Expected JSON body from the frontend:
    {
        "prompt": "User message",
        "model": "some-model-name",  # Optional - if not provided, uses first available model
        "search_enabled": true  # If true, performs web search and includes results in context
        "conversation_history": [  # Optional - previous messages for context
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """
    prompt = message.get("prompt")
    model = message.get("model")
    search_enabled = message.get("search_enabled", False)
    conversation_history = message.get("conversation_history", [])

    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body")

    # If no model specified, fetch the first available model dynamically
    if not model:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(OLLAMA_TAGS_ENDPOINT)
            if resp.status_code == 200:
                data = resp.json() or {}
                models_raw = data.get("models") or []
                if models_raw:
                    model = models_raw[0].get("name")
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="No models available in Ollama. Please install a model first."
                    )
            else:
                raise HTTPException(
                    status_code=502,
                    detail=f"Could not fetch models from Ollama (status {resp.status_code})"
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=502,
                detail=f"Could not reach Ollama at {OLLAMA_BASE_URL} to fetch default model"
            )

    # Perform web search if enabled
    search_results = ""
    search_source = None
    if search_enabled:
        search_results, search_source = await perform_web_search(prompt)
    
    # Build the final prompt with search results if available
    if search_results:
        # Enhanced prompt that instructs LLM to update outdated information
        final_prompt = f"""{search_results}

IMPORTANT INSTRUCTIONS:
- The web search results above contain current, up-to-date information from the internet.
- Compare these search results with any information you may have from your training data.
- If the search results show information that differs from or updates what you know, USE THE SEARCH RESULTS as they are more current.
- Explicitly correct any outdated information you may have mentioned earlier in this conversation.
- If you previously provided information that is now outdated based on the search results, acknowledge this and provide the updated information.
- Prioritize accuracy and currency: the web search results represent the most recent information available.

Now, based on the web search results above and the conversation history, please answer the following question:

{prompt}"""
    else:
        final_prompt = prompt

    # Build messages array with conversation history
    messages = []
    
    # Add conversation history (limit to last 10 exchanges to avoid token limits)
    for msg in conversation_history[-20:]:  # Last 20 messages (10 exchanges)
        if msg.get("role") in ["user", "assistant"]:
            messages.append({
                "role": msg.get("role"),
                "content": msg.get("content", "")
            })
    
    # Add the current user message
    messages.append({
        "role": "user",
        "content": final_prompt,
    })

    # Prepare payload for Ollama's /api/chat endpoint
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(OLLAMA_CHAT_ENDPOINT, json=payload)

        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama error (status {resp.status_code}): {resp.text}",
            )

        data = resp.json()

        # Ollama /api/chat returns a JSON object, with the final response
        # typically available as data["message"]["content"].
        content = (
            data.get("message", {}).get("content")
            or data.get("response")
            or ""
        )

        if not content:
            content = "[No content returned from Ollama]"

        return {"response": content, "search_source": search_source}

    except httpx.RequestError as e:
        # Usually means Ollama is not running or unreachable
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach Ollama at {OLLAMA_BASE_URL}: {str(e)}",
        )
