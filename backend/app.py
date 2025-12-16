from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# 3. Placeholder endpoint for chat
@app.post("/api/chat")
async def chat(message: dict):
    user_message = message.get("prompt", "No prompt received")
    # For now, just echo back the user message
    # In the future, this is where you call Ollama/llama.cpp
    return {"response": f"Your message was: '{user_message}' (Model processing placeholder)"}