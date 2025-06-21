const API_BASE_URL = 'http://localhost:5000';

async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error('server health check failed');
        return true;
    } catch (error) {
        console.error('server health check failed D:', error);
        return false;
    }
}

chrome.runtime.onInstalled.addListener(() => {
    console.log('pswd Strength Checker installed');
});

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "checkpswdStrength",
        title: "Check Password", // Changed label to be more user-friendly
        contexts: ["selection", "editable"]
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "checkpswdStrength") {
        const isHealthy = await checkServerHealth();
        if (!isHealthy) {
            chrome.tabs.sendMessage(tab.id, {
                type: 'error',
                message: 'Password service is not available. Please make sure the server is running.'
            });
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/check_pswd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pswd: info.selectionText || info.pswd })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            // Store result in chrome.storage.local for popup to read
            chrome.storage.local.set({ pswdCheckResult: data }, () => {
                // Optionally, set a badge to indicate result is ready
                chrome.action.setBadgeText({ text: '!' });
                chrome.action.setBadgeBackgroundColor({ color: '#FF5722' });
            });
            // Note: Cannot programmatically open the popup, user must click the extension icon
        } catch (error) {
            console.error('Error:', error);
            chrome.tabs.sendMessage(tab.id, {
                type: 'error',
                message: 'Failed to check password. Please try again.'
            });
        }
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'checkHealth') {
        checkServerHealth().then(isHealthy => {
            sendResponse({ isHealthy });
        });
        return true; 
    }
});

function suggestMutations(pswd) {
    const mutations = [];
    const subs = {'a': '@', 'i': '1', 'e': '3', 's': '$'};
    for (const [char, sub] of Object.entries(subs)) {
        if (pswd.toLowerCase().includes(char)) {
            const mutated = pswd.replace(char, sub);
            const entropy_change = calculateEntropy(mutated) - calculateEntropy(pswd);
            mutations.push({
                'original': pswd,
                'mutated': mutated,
                'entropy_change': entropy_change
            });
        }
    }
    return mutations;
}

function assessContextualRisk(pswd, context) {
    const riskLevels = {
        'banking': {minLength: 16, requiredChars: ['upper', 'lower', 'number', 'special']},
        'social_media': {minLength: 12, requiredChars: ['upper', 'lower', 'number']},
        'email': {minLength: 14, requiredChars: ['upper', 'lower', 'number', 'special']}
    };
    return checkAgainstRequirements(pswd, riskLevels[context]);
}

function checkSocialEngineeringRisk(pswd, userInfo = null) {
    const risks = [];
    const datePatterns = pswd.match(/\d{4}|\d{2}\/\d{2}/g);
    const namePatterns = checkAgainstCommonNames(pswd);
    return {
        'contains_dates': Boolean(datePatterns),
        'contains_names': Boolean(namePatterns),
        'risk_level': calculateRiskLevel(risks)
    };
}

function checkPolicyCompliance(pswd) {
    const policies = {
        'nist': checkNistCompliance(pswd),
        'pci_dss': checkPciCompliance(pswd),
        'corporate': checkCorporatePolicy(pswd)
    };
    return policies;
}

// calculate risk level based on multiple factors
function calculateRiskLevel(risks) {
    const riskScore = risks.reduce((sum, risk) => sum + risk.score, 0);
    return riskScore;
}
