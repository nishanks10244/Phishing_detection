/**
 * PhishGuard - Popup Script
 * Handles popup interactions
 */

const API_BASE = 'http://localhost:5000/api/v1';

function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(tab + '-tab').classList.add('active');
    event.target.classList.add('active');
}

async function scanCurrentPage() {
    const tab = await getCurrentTab();
    if (!tab || !tab.url) return;

    showScanning();
    const result = await scanURL(tab.url);
    displayResult(result, tab.url);
}

async function scanManual() {
    const input = document.getElementById('manual-input').value.trim();
    if (!input) return;

    showScanning();
    const result = await scanURL(input);
    displayResult(result, input);
}

async function getCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab;
}

async function scanURL(url) {
    try {
        const response = await fetch(API_BASE + '/scan/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (response.ok) {
            return await response.json();
        }
        return { error: 'Unable to scan' };
    } catch (error) {
        return { error: 'Connection failed: ' + error.message };
    }
}

function showScanning() {
    const result = document.getElementById('result');
    result.innerHTML = `<div style="text-align: center; padding: 1rem;">
        <div class="spinner"></div>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">Scanning...</p>
    </div>`;
    result.classList.add('show');
}

function displayResult(data, url) {
    const result = document.getElementById('result');

    if (data.error) {
        result.innerHTML = `<div class="result-title" style="color: #f59e0b;">⚠️ Error</div><div>${data.error}</div>`;
        result.className = 'result show';
        return;
    }

    const isPhishing = data.is_phishing;
    const confidence = (data.confidence * 100).toFixed(1);
    const riskLevel = data.risk_level;

    let html = `
        <div class="result-title">
            ${isPhishing ? '⚠️ PHISHING' : '✅ SAFE'}
        </div>
        <div class="confidence">
            <div class="confidence-label">
                <span>Risk Level: ${riskLevel.toUpperCase()}</span>
                <span>${confidence}%</span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${confidence}%"></div>
            </div>
        </div>
    `;

    if (data.details) {
        if (data.details.domain) {
            html += `<div style="margin-top: 0.75rem; font-size: 0.8rem;">
                <strong>Domain:</strong> ${data.details.domain}<br>
                <strong>HTTPS:</strong> ${data.details.uses_https ? 'Yes' : 'No'}<br>
                <strong>IP Address:</strong> ${data.details.has_ip ? 'Yes' : 'No'}
            </div>`;
        }
    }

    result.innerHTML = html;
    result.className = 'result show ' + (isPhishing ? 'danger' : 'safe');
}
