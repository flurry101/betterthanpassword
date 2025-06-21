// API configuration
const API_BASE_URL = 'http://localhost:5000';

// Constants
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Utility Functions
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (!errorDiv) {
        const div = document.createElement('div');
        div.id = 'error-message';
        div.style.color = 'red';
        div.style.padding = '10px';
        div.style.marginTop = '10px';
        div.style.backgroundColor = '#ffe6e6';
        div.style.borderRadius = '5px';
        document.body.insertBefore(div, document.body.firstChild);
    }
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error('Server health check failed:', response.status);
            return false;
        }
        
        const data = await response.json();
        const isHealthy = data && data.status === 'healthy';
        console.log('Server health check:', isHealthy ? 'healthy' : 'unhealthy');
        return isHealthy;
    } catch (error) {
        console.error('Server health check failed:', error);
        return false;
    }
}

async function fetchWithRetry(url, options, retries = MAX_RETRIES) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...options.headers,
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Attempt ${i + 1} failed:`, error);
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (i + 1)));
        }
    }
}

// Main Application Logic
class PasswordApp {
    constructor() {
        this.debounceTimer = null;
        this.lastResponse = null;
        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        // Password checking elements
        this.passwordInput = document.getElementById('passwordInput');
        this.strengthScore = document.getElementById('strengthScore');
        this.entropyScore = document.getElementById('entropyScore');
        this.charSets = document.getElementById('charSets');
        this.breachAlert = document.getElementById('breachAlert');
        this.breachDetails = document.getElementById('breachDetails');
        this.roastBox = document.getElementById('roastBox');
        this.toggleRoast = document.getElementById('toggleRoast');
        this.badgesContainer = document.getElementById('badgesContainer');
        this.weaknessList = document.getElementById('weaknessList');
        this.emojiScore = document.getElementById('emojiScore');
        this.userFriendlyScore = document.getElementById('userFriendlyScore');
        
        // Password generation elements
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        this.generateButtons = document.querySelectorAll('.generate-button');
        this.lengthSlider = document.getElementById('lengthSlider');
        this.lengthValue = document.getElementById('lengthValue');
        this.generatedPassword = document.getElementById('generatedPassword');
        this.passwordText = document.getElementById('passwordText');
        this.copyButton = document.getElementById('copyButton');
        this.qrCode = document.getElementById('qrCode');
    }

    setupEventListeners() {
        // Initialize length slider
        if (this.lengthSlider && this.lengthValue) {
            this.lengthValue.textContent = this.lengthSlider.value;
            this.lengthSlider.addEventListener('input', () => {
                this.lengthValue.textContent = this.lengthSlider.value;
            });
        }

        // Tab switching
        this.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.tabButtons.forEach(btn => btn.classList.remove('active'));
                this.tabContents.forEach(content => content.classList.remove('active'));
                
                button.classList.add('active');
                document.getElementById(`${button.dataset.tab}-tab`).classList.add('active');
            });
        });

        // Generate password buttons
        this.generateButtons.forEach(button => {
            button.addEventListener('click', () => {
                const type = button.dataset.type;
                const length = this.lengthSlider ? parseInt(this.lengthSlider.value) : 16;
                this.generatePassword(type, length);
            });
        });

        // Custom password generation
        const customBtn = document.getElementById('generateCustomBtn');
        if (customBtn) {
            customBtn.addEventListener('click', () => {
                const customWord = document.getElementById('customWordInput')?.value || '';
                const useLowercase = document.getElementById('customLowercase')?.checked;
                const useUppercase = document.getElementById('customUppercase')?.checked;
                const useNumbers = document.getElementById('customNumbers')?.checked;
                const useSymbols = document.getElementById('customSymbols')?.checked;
                const length = this.lengthSlider ? parseInt(this.lengthSlider.value) : 16;
                this.generateCustomPassword({ customWord, useLowercase, useUppercase, useNumbers, useSymbols, length });
            });
        }

        // Copy button
        if (this.copyButton && this.passwordText) {
            this.copyButton.addEventListener('click', () => {
                const textToCopy = this.passwordText.textContent;
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalText = this.copyButton.textContent;
                    this.copyButton.textContent = '✅';
                    setTimeout(() => {
                        this.copyButton.textContent = originalText;
                    }, 1000);
                });
            });
        }

        // Password input with debouncing
        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', (event) => {
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.checkPassword(event.target.value);
                }, 300);
            });
        }

        // Toggle roast mode
        if (this.toggleRoast && this.roastBox) {
            this.toggleRoast.addEventListener('click', () => {
                this.roastBox.classList.toggle('visible');
                this.toggleRoast.textContent = this.roastBox.classList.contains('visible') ? 
                    'Hide Roast Mode 🔥' : 'Show Roast Mode 🔥';
                if (this.lastResponse && this.lastResponse.roast) {
                    this.roastBox.textContent = this.lastResponse.roast;
                }
            });
        }

        // Listen for context menu messages
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.type === 'checkPassword' && message.password && this.passwordInput) {
                this.passwordInput.value = message.password;
                this.checkPassword(message.password);
            }
        });
    }

    updateUI(data) {
        if (!data) {
            console.error('No data provided to updateUI');
            return;
        }

        try {
            if (this.emojiScore) this.emojiScore.textContent = data.emoji_rating || '🔓';
            if (this.userFriendlyScore) this.userFriendlyScore.textContent = data.user_friendly_score || 'Enter a Password';
            if (this.strengthScore) this.strengthScore.textContent = `${Math.round(data.score || 0)}/100`;
            
            if (this.entropyScore && data.entropy) {
                this.entropyScore.textContent = `${Math.round(data.entropy)} bits`;
            }
            
            if (this.charSets) {
                const charTypes = [];
                if (data.password?.match(/[A-Z]/)) charTypes.push('ABC');
                if (data.password?.match(/[a-z]/)) charTypes.push('abc');
                if (data.password?.match(/[0-9]/)) charTypes.push('123');
                if (data.password?.match(/[^A-Za-z0-9]/)) charTypes.push('#@!');
                this.charSets.textContent = charTypes.join(' + ') || '-';
            }
            
            if (this.breachAlert && this.breachDetails) {
                if (data.hibp_breaches > 0) {
                    this.breachAlert.classList.add('visible');
                    this.breachDetails.textContent = `Found in ${data.hibp_breaches.toLocaleString()} data breaches! Change this password immediately.`;
                } else {
                    this.breachAlert.classList.remove('visible');
                }
            }
            
            if (this.weaknessList) {
                this.weaknessList.innerHTML = '';
                if (data.weaknesses && data.weaknesses.length > 0) {
                    data.weaknesses.forEach(weakness => {
                        const div = document.createElement('div');
                        div.className = 'weakness-item';
                        div.innerHTML = `<span class="weakness-icon">⚠️</span>${weakness}`;
                        this.weaknessList.appendChild(div);
                    });
                }
            }

            if (this.badgesContainer) {
                this.badgesContainer.innerHTML = '';
                if (data.badges && data.badges.length > 0) {
                    const badgeWrapper = document.createElement('div');
                    badgeWrapper.className = 'badges-wrapper';
                    
                    data.badges.forEach((badge, index) => {
                        const badgeElement = document.createElement('div');
                        badgeElement.className = `badge ${badge.rarity}`;
                        
                        // Create tooltip for badge info
                        const tooltip = document.createElement('div');
                        tooltip.className = 'badge-tooltip';
                        tooltip.innerHTML = `
                            <span class="badge-name">${badge.name}</span>
                            <span class="badge-description">${badge.description}</span>
                            <span class="badge-rarity">${badge.rarity}</span>
                        `;
                        
                        badgeElement.innerHTML = `
                            <div class="badge-content">
                                <div class="badge-icon-wrapper">
                                    <span class="badge-icon">${badge.icon}</span>
                                    <div class="badge-shine"></div>
                                </div>
                            </div>
                        `;
                        
                        badgeElement.appendChild(tooltip);
                        badgeWrapper.appendChild(badgeElement);
                        
                        // Stagger animations
                        setTimeout(() => {
                            badgeElement.classList.add('earned');
                            // Add sparkle effect
                            const sparkle = document.createElement('div');
                            sparkle.className = 'sparkle-effect';
                            badgeElement.appendChild(sparkle);
                            setTimeout(() => sparkle.remove(), 1000);
                        }, index * 150);
                    });
                    
                    this.badgesContainer.appendChild(badgeWrapper);
                } else {
                    // Show empty state
                    const emptyState = document.createElement('div');
                    emptyState.className = 'badges-empty-state';
                    emptyState.innerHTML = `
                        <span class="empty-icon">🏆</span>
                        <span class="empty-text">Make your password stronger to earn badges!</span>
                    `;
                    this.badgesContainer.appendChild(emptyState);
                }
            }

            if (this.roastBox && data.roast) {
                this.roastBox.textContent = data.roast;
            }

            this.lastResponse = data;
        } catch (error) {
            console.error('Error updating UI:', error);
            showError('Failed to update UI. Please try again.');
        }
    }

    async checkPassword(password) {
        if (!password) {
            this.updateUI({
                score: 0,
                entropy: 0,
                user_friendly_score: 'Enter a Password',
                emoji_rating: '🔍',
                weaknesses: ['Type a password to begin...'],
                badges: []
            });
            return;
        }

        try {
            const data = await fetchWithRetry(`${API_BASE_URL}/check_pswd`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
                body: JSON.stringify({ pswd: password })
            });
            
            data.password = password; // Add password for character set analysis
            this.updateUI(data);
        } catch (error) {
            console.error('Error checking password:', error);
            this.updateUI({
                score: 0,
                user_friendly_score: 'Connection Error',
                emoji_rating: '❌',
                weaknesses: ['Could not connect to the server. Please try again.'],
                badges: []
            });
        }
    }

    async generatePassword(type, length = 16) {
        try {
            hideError();
            const data = await fetchWithRetry(`${API_BASE_URL}/generate_pswd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type, length })
            });
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            const generatedPass = data.pswd || data.passkey || '';
            
            if (this.passwordInput) {
                this.passwordInput.value = generatedPass;
                await this.checkPassword(generatedPass);
            }
            
            if (this.generatedPassword && this.passwordText) {
                this.generatedPassword.classList.add('visible');
                this.passwordText.textContent = generatedPass;
            }
            
            if (data.qr_code && this.qrCode) {
                this.qrCode.classList.add('visible');
                this.qrCode.innerHTML = `<img src="data:image/png;base64,${data.qr_code}" alt="QR Code">`;
            }
        } catch (error) {
            console.error('Error generating password:', error);
            showError('Unable to generate password. Please make sure the server is running.');
        }
    }

    async generateCustomPassword(options) {
        try {
            hideError();
            const data = await fetchWithRetry(`${API_BASE_URL}/generate_pswd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'custom',
                    custom_word: options.customWord,
                    use_lowercase: options.useLowercase,
                    use_uppercase: options.useUppercase,
                    use_numbers: options.useNumbers,
                    use_symbols: options.useSymbols,
                    length: options.length
                })
            });
            if (data.error) {
                throw new Error(data.error);
            }
            const generatedPass = data.pswd || '';
            if (this.passwordInput) {
                this.passwordInput.value = generatedPass;
                await this.checkPassword(generatedPass);
            }
            if (this.generatedPassword && this.passwordText) {
                this.generatedPassword.classList.add('visible');
                this.passwordText.textContent = generatedPass;
            }
        } catch (error) {
            console.error('Error generating custom password:', error);
            showError('Unable to generate custom password. Please make sure the server is running.');
        }
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    // Check if there is a result from context menu action
    chrome.storage.local.get(['pswdCheckResult'], (result) => {
        if (result && result.pswdCheckResult) {
            const app = new PasswordApp();
            app.updateUI(result.pswdCheckResult);
            // Optionally clear the badge and storage after displaying
            chrome.action.setBadgeText({ text: '' });
            chrome.storage.local.remove('pswdCheckResult');
        } else {
            const app = new PasswordApp();
            app.checkPassword(''); // Initialize UI with empty state
        }
    });
    const isServerHealthy = await checkServerHealth();
    if (!isServerHealthy) {
        showError('Unable to connect to the password service. Please make sure the server is running.');
    }
});
