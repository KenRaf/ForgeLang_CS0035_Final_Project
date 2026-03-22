const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
const synth = window.speechSynthesis;

function switchTab(evt, tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    evt.currentTarget.classList.add('active');
}

function toggleSymbolTable() {
    const container = document.getElementById('symbol-table-container');
    const btn = document.getElementById('toggle-sym-btn');
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.innerText = '[ HIDE SYMBOL TABLE ]';
    } else {
        container.style.display = 'none';
        btn.innerText = '[ REVEAL SYMBOL TABLE ]';
    }
}

function aiSpeak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; 
    utterance.pitch = 0.8;
    synth.speak(utterance);
}

function renderOutputs(data) {
    document.getElementById('status-log').innerText = data.message;
    
    document.getElementById('terminal-box').innerText = data.terminal_logs;
    const terminal = document.getElementById('terminal-box');
    terminal.scrollTop = terminal.scrollHeight;

    const errorBox = document.getElementById('error-box');
    if (data.status === 'error') {
        errorBox.style.display = 'block';
        document.querySelector('.err-title').innerText = "⚠️ " + data.error_details.type; 
        
        // --- NEW: Line Number Error Mapping ---
        document.getElementById('err-line').innerText = data.error_details.line || "1";
        
        document.getElementById('err-reason').innerText = data.error_details.reason;
        document.getElementById('err-rule').innerText = data.error_details.rule;
        document.getElementById('err-fix').innerText = data.error_details.fix;
        document.getElementById('err-suggestion').innerText = data.error_details.suggestion;
    } else {
        errorBox.style.display = 'none';
    }

    aiSpeak(data.message);

    const invBody = document.getElementById('inventory-body');
    invBody.innerHTML = '';
    const symBody = document.getElementById('symbol-body');
    symBody.innerHTML = '';

    const sortedInventory = Object.entries(data.inventory).sort((a, b) => a[1].order - b[1].order);

    for (const [key, details] of sortedInventory) {
        invBody.innerHTML += `<tr><td>${key}</td><td>${details.type}</td><td>${details.value}</td></tr>`;
        symBody.innerHTML += `<tr>
            <td>${key}</td><td style="color: #ffcc00;">${details.type}</td>
            <td style="color: #00ffff;">${details.level}</td><td style="color: #ff00ff;">${details.offset}</td>
            <td>${details.width}</td>
        </tr>`;
    }
}

function startListening() {
    document.getElementById('status-log').innerText = "[ LISTENING... SPEAK NOW ]";
    document.getElementById('error-box').style.display = 'none'; 
    recognition.start();
}

recognition.onresult = async function(event) {
    const voiceText = event.results[0][0].transcript;
    document.getElementById('status-log').innerText = "Processing compiler logic...";
    document.getElementById('recognized-text').innerText = voiceText;

    const response = await fetch('/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: voiceText, mode: 'voice' })
    });

    const data = await response.json();
    
    if (data.status === 'success') {
        const editor = document.getElementById('code-editor');
        editor.value += data.code + '\n'; 
        
        // --- NEW: Update line numbers when voice scribe writes a new line ---
        updateLineNumbers();
    }

    renderOutputs(data);
};

async function compileTextCode() {
    const textCode = document.getElementById('code-editor').value;
    if (!textCode.trim()) return;

    document.getElementById('status-log').innerText = "Compiling written script...";
    document.getElementById('error-box').style.display = 'none';

    const response = await fetch('/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: textCode, mode: 'text' })
    });

    const data = await response.json();
    renderOutputs(data);
}

// --- NEW: VS CODE EDITOR LOGIC ---
function updateLineNumbers() {
    const textarea = document.getElementById('code-editor');
    const lineNumbers = document.getElementById('line-numbers');
    if (!textarea || !lineNumbers) return; // Safety check
    
    const lines = textarea.value.split('\n').length;
    lineNumbers.innerHTML = Array(lines).fill(0).map((_, i) => `<span>${i + 1}</span>`).join('');
}

function syncScroll() {
    const textarea = document.getElementById('code-editor');
    const lineNumbers = document.getElementById('line-numbers');
    if (!textarea || !lineNumbers) return; // Safety check
    
    lineNumbers.scrollTop = textarea.scrollTop;
}

// --- NEW: LANDSCAPE / PORTRAIT TOGGLE ---
function toggleLayout() {
    const container = document.getElementById('main-container');
    const workspace = document.getElementById('workspace');
    const btn = document.getElementById('layout-btn');

    if (workspace.classList.contains('workspace-portrait')) {
        // Switch to Landscape Mode
        workspace.classList.remove('workspace-portrait');
        workspace.classList.add('workspace-landscape');
        container.classList.add('wide-mode');
        btn.innerHTML = '[ PORTRAIT MODE ]';
    } else {
        // Switch to Portrait Mode
        workspace.classList.remove('workspace-landscape');
        workspace.classList.add('workspace-portrait');
        container.classList.remove('wide-mode');
        btn.innerHTML = '[ LANDSCAPE MODE ]';
    }
}

// Ensure lines load immediately when the page opens
document.addEventListener('DOMContentLoaded', updateLineNumbers);