// --- src/app.js ---
import './styles/main.css';
let Conversation = null;
let conversation = null;

/**
 * Debug Panel Usage:
 * To enable the debug panel:
 * 1. In index.html: Uncomment the debug panel div (search for "Debug Panel")
 * 2. In styles.css: Uncomment the debug panel styles (search for "Debug Panel Styles")
 * 3. Below: Change DEBUG_ENABLED to true
 */
const DEBUG_ENABLED = false;

// Debug logging
function debugLog(message, data = null) {
    if (!DEBUG_ENABLED) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const logElement = document.getElementById('debugLog');
    const logMessage = `[${timestamp}] ${message}${data ? '\n' + JSON.stringify(data, null, 2) : ''}`;
    
    console.log(logMessage); // Also log to console
    
    if (logElement) {
        logElement.innerHTML = logMessage + '\n\n' + logElement.innerHTML;
        if (logElement.innerHTML.length > 5000) { // Prevent too much content
            logElement.innerHTML = logElement.innerHTML.substring(0, 5000) + '...';
        }
    }
}

// Dynamically import ElevenLabs client
async function loadElevenLabsClient() {
    if (!Conversation) {
        const module = await import('@elevenlabs/client');
        Conversation = module.Conversation;
    }
    return Conversation;
}
let currentInvitationCode = null;
let currentInvitationData = null;

// Page Management
function showPage(pageId) {
    document.getElementById('homePage').style.display = pageId === 'homePage' ? 'block' : 'none';
    document.getElementById('voiceAgentPage').style.display = pageId === 'voiceAgentPage' ? 'block' : 'none';
}

// Invitation Code Management
async function validateInvitationCode(code) {
    try {
        const response = await fetch('/api/validate-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Invalid invitation code');
        }

        const data = await response.json();
        currentInvitationData = data;
        return data;
    } catch (error) {
        console.error('Error validating code:', error);
        throw error;
    }
}

async function incrementCodeUsage(code) {
    try {
        const response = await fetch('/api/increment-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to increment code usage');
        }

        return true;
    } catch (error) {
        console.error('Error incrementing code usage:', error);
        throw error;
    }
}

async function handleCodeSubmission() {
    debugLog('Starting code submission');
    
    const codeInput = document.getElementById('invitationCode');
    const errorElement = document.getElementById('codeError');
    const submitButton = document.getElementById('submitCode');

    debugLog('Elements found', {
        codeInput: !!codeInput,
        errorElement: !!errorElement,
        submitButton: !!submitButton
    });

    const code = codeInput.value.trim();
    if (!code) {
        debugLog('Empty code submitted');
        errorElement.textContent = 'Please enter an invitation code';
        return;
    }

    try {
        debugLog('Disabling submit button');
        submitButton.disabled = true;
        
        debugLog('Validating code', { code });
        await validateInvitationCode(code);
        
        debugLog('Code validated successfully');
        currentInvitationCode = code;
        showPage('voiceAgentPage');
    } catch (error) {
        debugLog('Error during code submission', {
            error: error.message,
            stack: error.stack
        });
        errorElement.textContent = error.message;
        codeInput.value = '';
    } finally {
        debugLog('Re-enabling submit button');
        submitButton.disabled = false;
    }
}

// Voice Chat Functions
async function requestMicrophonePermission() {
    try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        return true;
    } catch (error) {
        console.error('Microphone permission denied:', error);
        return false;
    }
}

async function getSignedUrl() {
    try {
        console.log('Fetching signed URL...');
        const response = await fetch('/api/signed-url');
        
        console.log('Signed URL Response:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries())
        });
        
        const data = await response.json();
        console.log('Signed URL Data:', data);
        
        if (!response.ok) {
            throw new Error(`Failed to get signed URL: ${response.status} ${response.statusText}`);
        }
        
        return data.signedUrl;
    } catch (error) {
        console.error('Error getting signed URL:', error);
        throw error;
    }
}

async function getAgentId() {
    const response = await fetch('/api/getAgentId');
    const { agentId } = await response.json();
    return agentId;
}

function updateStatus(isConnected) {
    const statusElement = document.getElementById('connectionStatus');
    statusElement.textContent = isConnected ? 'Connected' : 'Disconnected';
    statusElement.classList.toggle('connected', isConnected);
}

function updateSpeakingStatus(mode) {
    const statusElement = document.getElementById('speakingStatus');
    const isSpeaking = mode.mode === 'speaking';
    statusElement.textContent = isSpeaking ? 'Agent Speaking' : 'Agent Silent';
    statusElement.classList.toggle('speaking', isSpeaking);
    console.log('Speaking status updated:', { mode, isSpeaking });
}

async function startConversation() {
    if (!currentInvitationCode) {
        alert('Invalid session. Please enter your invitation code again.');
        showPage('homePage');
        return;
    }

    const startButton = document.getElementById('startButton');
    const endButton = document.getElementById('endButton');
    
    try {
        // Validate code again and increment usage
        await validateInvitationCode(currentInvitationCode);
        await incrementCodeUsage(currentInvitationCode);

        const hasPermission = await requestMicrophonePermission();
        if (!hasPermission) {
            alert('Microphone permission is required for the conversation.');
            return;
        }

        const signedUrl = await getSignedUrl();
        const ConversationClass = await loadElevenLabsClient();
        
        // Use first name from invitation code data, fallback to "Student"
        const customerName = (currentInvitationData?.first_name && currentInvitationData.first_name.trim()) 
            ? currentInvitationData.first_name.trim() 
            : "Student";
        
        console.log('🔥🔥🔥 CUSTOMER NAME DEBUG:', customerName, '🔥🔥🔥');
        
        conversation = await ConversationClass.startSession({
            signedUrl: signedUrl,
            dynamicVariables: {
                customer_name: customerName
            },
            onConnect: () => {
                console.log('WebSocket Connected');
                updateStatus(true);
                startButton.disabled = true;
                endButton.disabled = false;
            },
            onDisconnect: () => {
                console.log('Disconnected');
                updateStatus(false);
                startButton.disabled = false;
                endButton.disabled = true;
                updateSpeakingStatus({ mode: 'listening' });
            },
            onError: (error) => {
                console.error('Conversation error:', error);
                alert('An error occurred during the conversation.');
            },
            onModeChange: (mode) => {
                console.log('Mode Changed:', mode);
                updateSpeakingStatus(mode);
            },
            onMessage: (message) => {
                console.log('Agent Response:', message);
            }
        });
    } catch (error) {
        console.error('Failed to start conversation:', error);
        
        if (error.message.includes('Invalid invitation code') || 
            error.message.includes('expired') || 
            error.message.includes('Maximum number')) {
            alert(error.message);
            showPage('homePage');
            currentInvitationCode = null;
            currentInvitationData = null;
        } else {
            alert('Failed to start conversation. Please try again.');
        }
    }
}

async function endConversation() {
    const endButton = document.getElementById('endButton');
    const startButton = document.getElementById('startButton');
    
    if (conversation) {
        try {
            endButton.disabled = true;
            await conversation.endSession();
            updateStatus(false);
            updateSpeakingStatus({ mode: 'listening' });
            startButton.disabled = false;
            conversation = null;
        } catch (error) {
            console.error('Error ending conversation:', error);
        } finally {
            endButton.disabled = false;
        }
    }
}

// Event Listeners
function setupEventListeners() {
    debugLog('Setting up event listeners...');
    
    const submitButton = document.getElementById('submitCode');
    const codeInput = document.getElementById('invitationCode');
    
    if (!submitButton || !codeInput) {
        debugLog('Required elements not found', {
            submitButton: !!submitButton,
            codeInput: !!codeInput
        });
        return;
    }

    // Add both click and touchend events for better mobile support
    const submitEvents = ['click', 'touchend'];
    submitEvents.forEach(eventType => {
        submitButton.addEventListener(eventType, (e) => {
            debugLog(`Submit button ${eventType} event triggered`, {
                type: e.type,
                target: e.target.id,
                timestamp: new Date().getTime()
            });
            e.preventDefault(); // Prevent any default behavior
            handleCodeSubmission();
        });
    });

    codeInput.addEventListener('keypress', (e) => {
        debugLog('Keypress event on input', {
            key: e.key,
            target: e.target.id
        });
        if (e.key === 'Enter') {
            e.preventDefault();
            handleCodeSubmission();
        }
    });

    // Log initial button state
    debugLog('Submit button initial state', {
        disabled: submitButton.disabled,
        display: window.getComputedStyle(submitButton).display,
        visibility: window.getComputedStyle(submitButton).visibility,
        pointer: window.getComputedStyle(submitButton).pointerEvents,
        userAgent: navigator.userAgent
    });
}

// Call setup when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupEventListeners);
} else {
    setupEventListeners();
}
document.getElementById('startButton').addEventListener('click', startConversation);
document.getElementById('endButton').addEventListener('click', endConversation);

window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});
