# Nostos Chat: Lightweight Local LLM Interface

**Nostos Chat** is a resource-efficient, fast, and simple web interface designed to interact with local Large Language Models (LLMs) via an API endpoint. It prioritizes text-based chat, offering essential features while maintaining a minimal footprint.

## Features

* **Lightweight & Fast:** Built with a minimal HTML/CSS/JS frontend and a high-performance Python FastAPI backend.
* **Local Model API:** Designed to connect easily with local LLM APIs (e.g., Ollama: https://ollama.com/).
* **Model Switching:** Seamlessly switch between different LLMs via the frontend selector.
* **Document Analysis (RAG):** Placeholder for uploading and analyzing documents to provide context-aware responses.
* **Web Search Toggle:** Placeholder for giving the LLM access to real-time web search results when enabled.

---

## Getting Started

Follow these steps to set up the project on your local machine.

### Prerequisites

You need the following software installed:

1.  **Python** (3.8+)
2.  **Git** (for version control)
3.  **(Optional but Recommended) Ollama:** The simplest way to run local LLMs.

### Step 1: Set up the Backend (FastAPI)

#### A. Navigate and Activate Virtual Environment

1.  Navigate to the backend folder:
    cd backend

2.  Create and activate a Python virtual environment (.venv) to isolate dependencies:
    # Create the environment
    python -m venv .venv 
    
    # Activate (Linux/macOS)
    source .venv/bin/activate
    
    # Activate (Windows PowerShell)
    # .venv\Scripts\Activate.ps1

#### B. Install Dependencies

Install the required Python packages:

    pip install -r requirements.txt

#### C. Run the Backend Server

Start the API server.
    uvicorn app:app --reload --port 8000
    
The server will be accessible at http://127.0.0.1:8000.

### Step 3: Run the Frontend (UI)

1.  Navigate to the `frontend` folder.
    cd ../frontend

2.  Simply open the `index.html` file in your web browser (e.g., double-click it in your file explorer).

---

## Project Structure

The project is structured into two main, easily manageable components:

nostos_chat/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html        # HTML (UI Structure)
│   ├── style.css         # CSS (Styling/Appearance)
│   └── script.js         # JavaScript (Logic/Interactivity)
├── .gitignore
├── README.md
└── LICENSE

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.