const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const loginOverlay = document.getElementById('login-overlay');
const authStatusText = document.getElementById('auth-status-text');
const authToggleBtn = document.getElementById('auth-toggle-btn');

let authToken = localStorage.getItem('hr_auth_token');
let authName = localStorage.getItem('hr_auth_name') || 'Guest';

function updateUIAuth() {
    if (authToken) {
        authStatusText.innerText = `Role: ${authName}`;
        authToggleBtn.innerText = 'Logout';
        loginOverlay.style.display = 'none';
        loginOverlay.classList.remove('active');
    } else {
        authStatusText.innerText = 'Role: Guest';
        authToggleBtn.innerText = 'Login';
    }
}
updateUIAuth();

function toggleAuth() {
    if (authToken) {
        // Logout execution
        authToken = null;
        authName = 'Guest';
        localStorage.removeItem('hr_auth_token');
        localStorage.removeItem('hr_auth_name');
        updateUIAuth();
        appendMessage("You have successfully logged out. You are now operating as a Guest.", 'assistant');
    } else {
        loginOverlay.style.display = 'flex';
        loginOverlay.classList.add('active');
    }
}

function closeLoginModal() {
    loginOverlay.style.display = 'none';
    loginOverlay.classList.remove('active');
}

async function loginUser(username, password) {
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            authName = data.name;
            localStorage.setItem('hr_auth_token', authToken);
            localStorage.setItem('hr_auth_name', authName);
            updateUIAuth();
            appendMessage(`Successfully authenticated as ${data.name}. How can I assist you?`, 'assistant');
        } else {
            document.getElementById('login-error').innerText = data.detail || "Login failed.";
        }
    } catch (e) {
        document.getElementById('login-error').innerText = "Network error.";
    }
}

// Generate unique session ID for this tab instance
let sessionId = localStorage.getItem('chat_session_id');
if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 9);
    localStorage.setItem('chat_session_id', sessionId);
}

function appendMessage(text, role, isEscalation = false) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', role + '-message');
    
    if (isEscalation) {
        msgDiv.classList.add('escalated-message');
    }
    
    // Format response safely
    const formattedText = text.replace(/\n/g, '<br>');
    msgDiv.innerHTML = `<p>${formattedText}</p>`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('loading-dots');
    loadingDiv.id = 'loading-indicator';
    loadingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideLoading() {
    const loader = document.getElementById('loading-indicator');
    if (loader) loader.remove();
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    userInput.value = '';
    
    showLoading();

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch('/chat', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ query: text, session_id: sessionId })
        });
        
        const data = await response.json();
        hideLoading();
        
        if (response.ok) {
            appendMessage(data.answer, 'assistant', data.is_escalation);
            sessionId = data.session_id; // Keep the same session active
        } else {
            appendMessage(data.detail || "I am currently unable to connect to the HR servers. Please try again shortly.", 'assistant');
        }
    } catch (error) {
        hideLoading();
        appendMessage("Network error. Is the server running?", 'assistant');
    }
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
