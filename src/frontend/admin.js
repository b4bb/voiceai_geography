import './styles/main.css';
import './styles/admin.css';

// State management
let accessToken = null;
let currentSort = { field: 'created_at', ascending: false };
let codes = [];

// DOM Elements
const loginForm = document.getElementById('loginForm');
const codesPanel = document.getElementById('codesPanel');
const loginButton = document.getElementById('loginButton');
const loginError = document.getElementById('loginError');
const showValidOnly = document.getElementById('showValidOnly');
const codesTable = document.getElementById('codesTable');

// Event Listeners
console.log('Setting up event listeners...');

// Login button
console.log('Login button:', loginButton);
loginButton.addEventListener('click', handleLogin);

// Show valid only checkbox
console.log('Show valid only checkbox:', showValidOnly);
showValidOnly.addEventListener('change', filterAndDisplayCodes);

// Refresh button
const refreshButton = document.getElementById('refreshButton');
console.log('Refresh button:', refreshButton);
if (refreshButton) {
    refreshButton.addEventListener('click', () => {
        console.log('Refresh button clicked');
        loadCodes(true);
    });
} else {
    console.error('Refresh button not found!');
}

// Sort headers
const sortHeaders = document.querySelectorAll('th[data-sort]');
console.log('Sort headers:', sortHeaders);
sortHeaders.forEach(th => {
    th.addEventListener('click', () => handleSort(th.dataset.sort));
});

// Login Handler
async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        loginButton.disabled = true;
        const response = await fetch('/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        if (!response.ok) {
            throw new Error('Invalid credentials');
        }

        const data = await response.json();
        accessToken = data.access_token;
        
        // Hide login, show codes panel
        loginForm.style.display = 'none';
        codesPanel.style.display = 'block';
        
        // Load codes
        await loadCodes();
    } catch (error) {
        loginError.textContent = error.message;
    } finally {
        loginButton.disabled = false;
    }
}

// Load Codes
async function loadCodes(isRefresh = false) {
    console.log('Loading codes, isRefresh:', isRefresh);
    
    const refreshButton = document.getElementById('refreshButton');
    console.log('Refresh button in loadCodes:', refreshButton);
    
    if (isRefresh) {
        console.log('Disabling refresh button and adding refreshing class');
        refreshButton.disabled = true;
        refreshButton.classList.add('refreshing');
    }

    try {
        const response = await fetch('/api/codes', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load invitation codes');
        }

        codes = await response.json();
        filterAndDisplayCodes();
    } catch (error) {
        console.error('Error loading codes:', error);
    } finally {
        if (isRefresh) {
            refreshButton.disabled = false;
            refreshButton.classList.remove('refreshing');
        }
    }
}

// Sort Handler
function handleSort(field) {
    if (currentSort.field === field) {
        currentSort.ascending = !currentSort.ascending;
    } else {
        currentSort.field = field;
        currentSort.ascending = true;
    }

    // Update sort indicators
    document.querySelectorAll('th[data-sort]').forEach(th => {
        const arrow = currentSort.field === th.dataset.sort
            ? (currentSort.ascending ? ' ↑' : ' ↓')
            : ' ↕';
        th.textContent = th.textContent.replace(/[↑↓↕]$/, '') + arrow;
    });

    filterAndDisplayCodes();
}

// Filter and Display Codes
function filterAndDisplayCodes() {
    let filteredCodes = [...codes];

    // Apply valid-only filter if checked
    if (showValidOnly.checked) {
        filteredCodes = filteredCodes.filter(code => code.is_valid);
    }

    // Apply sorting
    filteredCodes.sort((a, b) => {
        let aVal = a[currentSort.field];
        let bVal = b[currentSort.field];

        // Handle dates
        if (currentSort.field.includes('_at')) {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        }

        // Handle numeric values
        if (typeof aVal === 'number') {
            return currentSort.ascending ? aVal - bVal : bVal - aVal;
        }

        // Handle boolean values
        if (typeof aVal === 'boolean') {
            return currentSort.ascending ? aVal - bVal : bVal - aVal;
        }

        // Handle strings
        const comparison = String(aVal).localeCompare(String(bVal));
        return currentSort.ascending ? comparison : -comparison;
    });

    // Update table
    const tbody = codesTable.querySelector('tbody');
    tbody.innerHTML = filteredCodes.map(code => `
        <tr>
            <td>${code.code}</td>
            <td>${new Date(code.created_at).toLocaleString()}</td>
            <td>${new Date(code.expires_at).toLocaleString()}</td>
            <td>${code.max_calls}</td>
            <td>${code.call_count}</td>
            <td class="${getStatusClass(code)}">${getStatusText(code)}</td>
        </tr>
    `).join('');
}

// Helper Functions
function getStatusClass(code) {
    if (!code.is_valid) {
        return new Date() >= new Date(code.expires_at) ? 'status-expired' : 'status-depleted';
    }
    return 'status-valid';
}

function getStatusText(code) {
    if (!code.is_valid) {
        return new Date() >= new Date(code.expires_at) ? 'Expired' : 'Depleted';
    }
    return 'Valid';
}

// Initialize sorting indicators
document.querySelectorAll('th[data-sort]').forEach(th => {
    th.textContent = th.textContent.replace(/[↑↓↕]$/, '') + ' ↕';
});
