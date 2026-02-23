/**
 * PhishGuard - Content Script
 * Runs on every webpage to inject warning banners
 */

const API_BASE = 'http://localhost:5000/api/v1';
const CACHE_DURATION = 3600000; // 1 hour

let phishingCache = {};

// Check if page/links are phishing
async function checkPageContent() {
    const url = window.location.href;
    await checkURL(url);
}

async function checkURL(url) {
    try {
        // Check cache first
        const cached = phishingCache[url];
        if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
            if (cached.isPhishing) {
                showWarningBanner(url, cached.confidence);
            }
            return;
        }

        // Scan with API
        const response = await fetch(API_BASE + '/scan/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (response.ok) {
            const result = await response.json();
            phishingCache[url] = {
                isPhishing: result.is_phishing,
                confidence: result.confidence,
                timestamp: Date.now()
            };

            if (result.is_phishing) {
                showWarningBanner(url, result.confidence);
                sendNotification(url, result);
            }
        }
    } catch (error) {
        console.log('PhishGuard: Could not scan URL');
    }
}

function showWarningBanner(url, confidence) {
    // Check if banner already exists
    if (document.getElementById('phishguard-banner')) {
        return;
    }

    const banner = document.createElement('div');
    banner.id = 'phishguard-banner';
    banner.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem 2rem;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;

    const confidencePercent = (confidence * 100).toFixed(0);
    banner.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <strong style="font-size: 1.1rem;">⚠️ Warning: Phishing Site Detected</strong>
                <p style="margin: 0.25rem 0 0; font-size: 0.9rem; opacity: 0.9;">
                    This page appears to be a phishing attempt. Avoid entering personal information. (${confidencePercent}% confidence)
                </p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                Dismiss
            </button>
        </div>
    `;

    document.body.insertBefore(banner, document.body.firstChild);

    // Add top margin to body to accommodate banner
    document.body.style.marginTop = '60px';
}

function sendNotification(url, result) {
    chrome.runtime.sendMessage({
        action: 'showNotification',
        title: '⚠️ Phishing Detected',
        message: `${url} appears to be a phishing site (${(result.confidence * 100).toFixed(0)}% confidence)`,
        type: 'danger'
    }).catch(() => {
        // Notification API might not be available
    });
}

// Scan all links on page
function scanPageLinks() {
    const links = document.querySelectorAll('a[href]');
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
            // Mark suspicious links
            checkLinkSuspicious(href, link);
        }
    });
}

function checkLinkSuspicious(url, link) {
    // Quick heuristic check
    const suspiciousPatterns = [
        '/verify', '/confirm', '/login', '/account',
        '/update', '/security', '/billing', '/payment'
    ];

    const urlLower = url.toLowerCase();
    let suspicious = false;

    // Check for IP address
    if (/http:\/\/\d+\.\d+\.\d+\.\d+/.test(url)) {
        suspicious = true;
    }

    // Check for suspicious patterns
    for (const pattern of suspiciousPatterns) {
        if (urlLower.includes(pattern)) {
            suspicious = true;
            break;
        }
    }

    if (suspicious) {
        link.style.textDecoration = 'underline dashed #ef4444';
        link.title = '⚠️ This link looks suspicious';
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        checkPageContent();
        scanPageLinks();
    });
} else {
    checkPageContent();
    scanPageLinks();
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'scanURL') {
        checkURL(request.url).then(() => {
            sendResponse({ success: true });
        });
    }
});
