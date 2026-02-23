/**
 * PhishGuard - Background Service Worker
 * Handles extension-level logic and notifications
 */

const API_BASE = 'http://localhost:5000/api/v1';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'showNotification') {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: request.title,
            message: request.message,
            priority: 2
        });
    }

    if (request.action === 'scanURL') {
        scanURL(request.url).then(result => {
            sendResponse(result);
        });
        return true;
    }

    if (request.action === 'scanEmail') {
        scanEmail(request.email).then(result => {
            sendResponse(result);
        });
        return true;
    }
});

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
        return { error: 'API Error' };
    } catch (error) {
        return { error: error.message };
    }
}

async function scanEmail(email) {
    try {
        const response = await fetch(API_BASE + '/scan/email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email_content: email })
        });

        if (response.ok) {
            return await response.json();
        }
        return { error: 'API Error' };
    } catch (error) {
        return { error: error.message };
    }
}

// Check tabs on update
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // Content script will handle the scanning
    }
});
