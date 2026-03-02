const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');

const API_URL = '/chat';

function addMessage(role, content, sources = []) {
    const row = document.createElement('div');
    row.className = `msg-row ${role}`;

    if (role === 'assistant' && sources.length > 0) {
        // Render as a card if there are sources
        const card = document.createElement('div');
        card.className = 'assistant-card';

        let sourcesHtml = '<ul>';
        sources.forEach(source => {
            const fileName = source.split('/').pop().replace(/-/g, ' ');
            sourcesHtml += `<li><a href="${source}" target="_blank">${fileName}</a></li>`;
        });
        sourcesHtml += '</ul>';

        card.innerHTML = `
            <p>${content}</p>
            ${sourcesHtml}
        `;
        row.appendChild(card);
    } else {
        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';
        bubble.textContent = content;
        row.appendChild(bubble);
    }

    chatContainer.appendChild(row);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function handleSendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    addMessage('user', message);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        if (response.ok) {
            const data = await response.json();
            addMessage('assistant', data.answer, data.sources);
        } else {
            addMessage('assistant', `Error: ${response.status} - ${response.statusText}`);
        }
    } catch (error) {
        addMessage('assistant', `Connection Error: ${error.message}`);
    }
}

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});
