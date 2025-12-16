# Nostos Chat: Lightweight Local LLM Interface

**Nostos Chat** is a resource-efficient, fast, and simple web interface designed to interact with local Large Language Models (LLMs) via an API endpoint. It prioritizes text-based chat, offering essential features while maintaining a minimal footprint.

## Features

* **Lightweight & Fast:** Built with a minimal HTML/CSS/JS frontend and a high-performance Python FastAPI backend.
* **Local Model API:** Connects seamlessly with Ollama (https://ollama.com/) for running local LLMs.
* **Automatic Model Detection:** Automatically detects and lists all available models from your Ollama installation - no configuration needed!
* **Dynamic Model Switching:** Seamlessly switch between any available LLMs via the frontend selector.
* **Generalized Design:** Works with any Ollama models you have installed - just add models with `ollama pull` and they'll appear automatically.
* **Cyberpunk UI:** Full-page, neon-lit, modern cyberpunk-inspired interface with glowing effects, responsive layout, and animated touches.
* **Clear Conversation:** One-click button to reset chat and wipe context instantly.
* **Web Search Integration:** Toggle web search on/off to give the LLM access to real-time web search results from Google or DuckDuckGo. A clear system line in the chat always shows which provider is used for each query.
* **Document Analysis (RAG):** Placeholder for uploading and analyzing documents to provide context-aware responses.

---

## UI / UX Highlights

- **Fullscreen Responsive:** The chat fills the entire window, adapts to all devices, and has a beautiful neon-glow grid.
- **Cyberpunk Theme:** Terminal-inspired, uses Orbitron/Rajdhani fonts, animated scanlines, glowing colors, and dazzling button/toggle effects.
- **Conversation Controls:** Instantly reset your session/history with the RESET button. All chat is contextual, persistent for the page session.
- **Visual Search Source Indicator:** Every time you use "NET_SEARCH" (web search), a system line in the chat identifies (GOOGLE or DUCKDUCKGO).
- **Accessibility:** High-contrast bot message bubbles for readability.

## Getting Started

Follow these steps to set up the project on your local machine.

### Prerequisites

You need the following software installed:

1.  **Python** (3.8+)
2.  **Git** (for version control)
3.  **Ollama**: Required for running local LLMs. Install from https://ollama.com/
4.  **At least one Ollama model:** Install models using `ollama pull <model-name>`. Examples:
    - `ollama pull llama3`
    - `ollama pull gemma2`
    - `ollama pull qwen2.5`
    - Or any other model from the Ollama library
5.  **(Optional but Recommended)** For Google-powered web search:
    - A Google Cloud Custom Search API key
    - A Custom Search Engine (CSE) ID
    - See https://programmablesearchengine.google.com/about/ and Google Custom Search API docs

### Step 1: Ensure Ollama is Running

Make sure Ollama is installed and running:

```bash
# Start Ollama (if not already running)
ollama serve

# Verify you have at least one model installed
ollama list
```

If you don't have any models yet, install one:
```bash
ollama pull llama3  # or any other model
```

### Step 2: Set up the Backend (FastAPI)

#### A. Navigate and Activate Virtual Environment

1.  Navigate to the backend folder:
    ```bash
    cd backend
    # Create the environment
    python -m venv .venv
    # Activate (Linux/macOS)
    source .venv/bin/activate
    # Activate (Windows PowerShell)
    # .venv\Scripts\Activate.ps1
    ```

#### B. Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

#### C. Run the Backend Server

(Optional, for Google-powered web search): Set your Google API key and CSE ID:
```bash
export GOOGLE_SEARCH_API_KEY="your-google-api-key"
export GOOGLE_SEARCH_CX="your-google-cse-id"
```

Start the API server:
```bash
uvicorn app:app --reload --port 8000
```

The server will be accessible at http://127.0.0.1:8000.

**Note:** The backend automatically connects to Ollama at `http://127.0.0.1:11434` by default. To use a different Ollama instance, set the `OLLAMA_BASE_URL` environment variable:
```bash
export OLLAMA_BASE_URL="http://your-ollama-host:11434"
uvicorn app:app --reload --port 8000
```

### Step 3: Run the Frontend (UI)

1.  Navigate to the `frontend` folder:

    ```bash
    cd ../frontend
    ```

2.  Open the `index.html` file in your web browser (e.g., double-click it in your file explorer).

3.  The model selector will automatically populate with all available models from your Ollama installation. Select any model and start chatting!

---

## How It Works

The application automatically detects all models available in your Ollama installation:

1. **Backend (`/api/models`)**: Queries Ollama's `/api/tags` endpoint to fetch the list of available models
2. **Frontend**: On page load, fetches the model list and populates the dropdown selector
3. **Chat (`/api/chat`)**: Forwards chat requests to Ollama's `/api/chat` endpoint with the selected model
4. **Web Search (when enabled)**: Performs Google Custom Search (if API configured) or DuckDuckGo web searches and includes results in the prompt context, allowing the LLM to provide answers based on current web information

No hardcoded model names - everything is dynamic and works with any Ollama models you have installed!

## Using Web Search

The web search feature allows your local LLM to access real-time information from the internet:

1. **Toggle ON**: Click the "Web Search" toggle in the header to enable web search
2. **Ask Questions**: When web search is enabled, your questions will trigger a search
3. **Get Informed Answers**: The LLM will receive search results and use them to provide more accurate, up-to-date responses
4. **Results source indicator**: When search is performed, a system line in the chat will clearly show if results are from GOOGLE or DUCKDUCKGO.

**Search preferences:**
- If Google Custom Search API key and CX are set, all web search is via Google (subject to your Google quota)
- Otherwise, DuckDuckGo is used as a fallback (no quota/usage displayed)

**Example use cases:**
- Current events and news
- Recent developments in technology
- Up-to-date information about topics
- Real-time data queries

**Note:** Web search adds a small delay. The chat UI will always inform you of the active search engine in use for each query.

## Adding New Models

Simply install new models in Ollama and they'll automatically appear in the interface:

```bash
ollama pull <model-name>
```

Then refresh the frontend page - the new model will be available in the dropdown selector.

## Project Structure

The project is structured into two main, easily manageable components:

```
nostos_chat/
├── backend/
│   ├── app.py            # FastAPI backend with Ollama integration
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # HTML (UI Structure)
│   ├── style.css         # CSS (Styling/Appearance)
│   └── script.js         # JavaScript (Logic/Interactivity)
├── .gitignore
├── README.md
└── LICENSE
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.