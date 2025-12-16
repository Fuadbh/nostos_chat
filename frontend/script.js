document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const messagesArea = document.getElementById('messages');
    const searchToggle = document.getElementById('search-toggle');

    // Base URL for the backend API
    // IMPORTANT: This must match the port the backend is running on (default 8000 for Uvicorn)
    const BACKEND_URL = 'http://127.0.0.1:8000/api/chat';

    // Helper function to add a message to the chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        messagesArea.appendChild(messageDiv);
        // Scroll to the bottom of the chat area
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

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

        // 3. Send message to backend
        try {
            const response = await fetch(BACKEND_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model: selectedModel,
                    search_enabled: isSearchEnabled
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // 4. Display bot response
            addMessage(data.response, 'bot');

        } catch (error) {
            console.error('Error sending message:', error);
            addMessage(`[ERROR] Could not connect to the local model server. Is the backend running on ${BACKEND_URL}?`, 'bot');
        }
    });
});