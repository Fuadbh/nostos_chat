document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const messagesArea = document.getElementById('messages');
    const searchToggle = document.getElementById('search-toggle');
    const modelSelector = document.getElementById('model-selector');

    // Base URL for the backend API
    // IMPORTANT: This must match the port the backend is running on (default 8000 for Uvicorn)
    const BACKEND_URL = 'http://127.0.0.1:8000/api/chat';
    const MODELS_URL = 'http://127.0.0.1:8000/api/models';

    // Conversation history to maintain context
    let conversationHistory = [];

    // Clear chat button handler
    const clearChatButton = document.getElementById('clear-chat');
    clearChatButton.addEventListener('click', () => {
        // Clear conversation history
        conversationHistory = [];
        // Clear messages area (keep only the initial greeting)
        messagesArea.innerHTML = '<div class="bot-message">> SYSTEM RESET COMPLETE<br>> NEURAL INTERFACE READY<br>> CONVERSATION HISTORY CLEARED</div>';
    });

    // Helper function to add a message to the chat
    // Returns the created element so it can be removed if needed
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        messagesArea.appendChild(messageDiv);
        // Scroll to the bottom of the chat area
        messagesArea.scrollTop = messagesArea.scrollHeight;
        return messageDiv;
    }

    // Load available models from the backend (which proxies Ollama)
    async function loadModels() {
        try {
            const resp = await fetch(MODELS_URL);
            if (!resp.ok) {
                throw new Error(`HTTP error! status: ${resp.status}`);
            }
            const data = await resp.json();
            const models = data.models || [];

            // Clear existing options
            modelSelector.innerHTML = '';

            if (models.length === 0) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No models found';
                modelSelector.appendChild(option);
                modelSelector.disabled = true;
                addMessage('> ERROR: NO MODELS DETECTED\n> RUN: ollama list\n> TO VERIFY INSTALLATION', 'bot');
                return;
            }

            // Populate selector with model names
            models.forEach((name, index) => {
                const option = document.createElement('option');
                option.value = name;
                option.textContent = name;
                modelSelector.appendChild(option);
                // First model is selected by default via DOM
            });
        } catch (err) {
            console.error('Failed to load models:', err);
            addMessage('> SYSTEM ERROR: CONNECTION FAILED\n> VERIFY BACKEND STATUS\n> CHECK: /api/models ENDPOINT', 'bot');
        }
    }

    // Kick off loading models
    loadModels();

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = userInput.value.trim();

        if (!prompt) return;

        // 1. Display user message
        addMessage(prompt, 'user');
        userInput.value = ''; // Clear input

        // 2. Get current settings
        const isSearchEnabled = searchToggle.checked;
        const selectedModel = document.getElementById('model-selector').value;

        // 3. Show loading indicator if search is enabled
        let loadingMessage = null;
        if (isSearchEnabled) {
            loadingMessage = addMessage('> NET_SEARCH ACTIVE\n> SCANNING DATABANKS...', 'bot');
        }

        // 4. Send message to backend
        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model: selectedModel,
                    search_enabled: isSearchEnabled,
                    conversation_history: conversationHistory
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // 5. Remove loading message if it exists
            if (loadingMessage) {
                loadingMessage.remove();
            }

            // 5b. Visual identification of search source (if any)
            if (data.search_source) {
                const sourceLabel = data.search_source.toLowerCase() === 'google'
                    ? '> NET_SEARCH SOURCE: GOOGLE'
                    : data.search_source.toLowerCase() === 'duckduckgo'
                        ? '> NET_SEARCH SOURCE: DUCKDUCKGO'
                        : `> NET_SEARCH SOURCE: ${data.search_source.toUpperCase()}`;
                addMessage(sourceLabel, 'bot');
            }

            // 6. Display bot response
            addMessage(data.response, 'bot');

            // 7. Update conversation history
            conversationHistory.push(
                { role: 'user', content: prompt },
                { role: 'assistant', content: data.response }
            );

        } catch (error) {
            console.error('Error sending message:', error);
            addMessage(`> CONNECTION ERROR\n> BACKEND OFFLINE\n> CHECK: ${BACKEND_URL}`, 'bot');
        }
    });
});