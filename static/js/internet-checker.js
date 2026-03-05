/**
 * Internet Connection Checker for ValidoAI
 * Monitors network connectivity and provides real-time feedback
 */

class ValidoAIInternetChecker {
    constructor() {
        this.isOnline = navigator.onLine;
        this.connectionType = this.getConnectionType();
        this.connectionSpeed = 'unknown';
        this.lastOnlineTime = null;
        this.lastOfflineTime = null;
        this.checkInterval = null;
        this.toastShown = false;
        this.modalShown = false;

        this.init();
    }

    init() {
        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Check connection periodically
        this.startPeriodicCheck();

        // Initial connection check
        this.checkConnection();

        // Listen for visibility changes to check connection when tab becomes active
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkConnection();
            }
        });

        // Monitor connection quality if supported
        if ('connection' in navigator) {
            navigator.connection.addEventListener('change', () => {
                this.updateConnectionInfo();
            });
            this.updateConnectionInfo();
        }
    }

    handleOnline() {
        this.isOnline = true;
        this.lastOnlineTime = new Date();

        // Show success toast
        if (window.showToast) {
            showToast('success', '🌐 Internet connection restored', {
                position: 'top-right',
                duration: 3000
            });
        }

        // Hide offline modal if shown
        this.hideOfflineModal();

        // Trigger custom event
        this.triggerEvent('connectionOnline', {
            timestamp: this.lastOnlineTime,
            connectionType: this.connectionType
        });

        console.log('Internet connection restored at:', this.lastOnlineTime);
    }

    handleOffline() {
        this.isOnline = false;
        this.lastOfflineTime = new Date();

        // Show error toast
        if (window.showToast) {
            showToast('error', '🔴 No internet connection', {
                position: 'top-right',
                duration: 0 // Persistent until connection restored
            });
        }

        // Show offline modal
        this.showOfflineModal();

        // Trigger custom event
        this.triggerEvent('connectionOffline', {
            timestamp: this.lastOfflineTime
        });

        console.log('Internet connection lost at:', this.lastOfflineTime);
    }

    async checkConnection() {
        try {
            // Try to fetch a small resource to verify connection
            const response = await fetch('/static/img/favicon.ico', {
                method: 'HEAD',
                cache: 'no-cache',
                timeout: 5000
            });

            const wasOffline = !this.isOnline;
            this.isOnline = response.ok;

            if (wasOffline && this.isOnline) {
                this.handleOnline();
            } else if (!wasOffline && !this.isOnline) {
                this.handleOffline();
            }

            return this.isOnline;
        } catch (error) {
            if (this.isOnline) {
                this.handleOffline();
            }
            return false;
        }
    }

    getConnectionType() {
        if ('connection' in navigator && navigator.connection) {
            return navigator.connection.effectiveType || 'unknown';
        }
        return 'unknown';
    }

    updateConnectionInfo() {
        if ('connection' in navigator && navigator.connection) {
            const connection = navigator.connection;

            this.connectionType = connection.effectiveType || 'unknown';
            this.connectionSpeed = this.getSpeedLabel(connection.downlink);

            // Trigger connection info update event
            this.triggerEvent('connectionInfoUpdate', {
                type: this.connectionType,
                speed: this.connectionSpeed,
                downlink: connection.downlink,
                rtt: connection.rtt
            });

            console.log('Connection updated:', {
                type: this.connectionType,
                speed: this.connectionSpeed,
                downlink: connection.downlink + ' Mbps',
                rtt: connection.rtt + ' ms'
            });
        }
    }

    getSpeedLabel(downlink) {
        if (!downlink) return 'unknown';

        if (downlink >= 10) return 'fast';
        if (downlink >= 5) return 'good';
        if (downlink >= 2) return 'slow';
        return 'very-slow';
    }

    showOfflineModal() {
        if (this.modalShown) return;

        if (window.showGlobalModal) {
            showGlobalModal({
                title: '🔴 Connection Lost',
                content: `
                    <div class="text-center">
                        <div class="w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i class="fas fa-wifi-slash text-red-600 text-2xl"></i>
                        </div>
                        <h3 class="text-lg font-semibold mb-2">No Internet Connection</h3>
                        <p class="text-neutral-600 dark:text-neutral-400 mb-4">
                            You're currently offline. Some features may not work properly.
                        </p>
                        <div class="bg-neutral-50 dark:bg-neutral-800 p-3 rounded-lg text-sm">
                            <p class="mb-2"><strong>Last online:</strong> ${this.lastOnlineTime ? this.lastOnlineTime.toLocaleString() : 'Never'}</p>
                            <p class="mb-0"><strong>We'll automatically reconnect when connection is restored.</strong></p>
                        </div>
                    </div>
                `,
                actions: false,
                size: 'max-w-sm'
            });
        }

        this.modalShown = true;
    }

    hideOfflineModal() {
        // Close the modal if it's open (this would need to be implemented based on your modal system)
        if (this.modalShown) {
            // Assuming you have a way to close modals programmatically
            if (window.closeGlobalModal) {
                closeGlobalModal();
            }
            this.modalShown = false;
        }
    }

    startPeriodicCheck() {
        // Check connection every 30 seconds
        this.checkInterval = setInterval(() => {
            this.checkConnection();
        }, 30000);
    }

    stopPeriodicCheck() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    triggerEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, { detail });
        window.dispatchEvent(event);
    }

    // Public API methods
    getStatus() {
        return {
            isOnline: this.isOnline,
            connectionType: this.connectionType,
            connectionSpeed: this.connectionSpeed,
            lastOnlineTime: this.lastOnlineTime,
            lastOfflineTime: this.lastOfflineTime
        };
    }

    isConnectionFast() {
        return this.connectionSpeed === 'fast';
    }

    isConnectionGood() {
        return ['fast', 'good'].includes(this.connectionSpeed);
    }

    isConnectionSlow() {
        return ['slow', 'very-slow'].includes(this.connectionSpeed);
    }

    // Network quality indicator
    getNetworkQuality() {
        if (!this.isOnline) return 'offline';
        if (this.connectionSpeed === 'fast') return 'excellent';
        if (this.connectionSpeed === 'good') return 'good';
        if (this.connectionSpeed === 'slow') return 'poor';
        return 'very-poor';
    }

    // Show network status in UI
    showNetworkStatus() {
        const status = this.getStatus();
        const quality = this.getNetworkQuality();

        const qualityColors = {
            excellent: 'text-green-600',
            good: 'text-blue-600',
            poor: 'text-yellow-600',
            'very-poor': 'text-orange-600',
            offline: 'text-red-600'
        };

        const qualityIcons = {
            excellent: 'fas fa-wifi',
            good: 'fas fa-wifi',
            poor: 'fas fa-wifi',
            'very-poor': 'fas fa-wifi-slash',
            offline: 'fas fa-times-circle'
        };

        // Create status element
        const statusElement = document.createElement('div');
        statusElement.className = `network-status-indicator ${qualityColors[quality]} text-sm`;
        statusElement.innerHTML = `
            <i class="${qualityIcons[quality]} me-1"></i>
            <span class="network-quality">${quality.charAt(0).toUpperCase() + quality.slice(1)}</span>
            <span class="network-type ms-2">(${status.connectionType.toUpperCase()})</span>
        `;

        return statusElement;
    }

    // Add network status to page
    addNetworkStatusToPage() {
        const statusElement = this.showNetworkStatus();
        statusElement.id = 'network-status';

        // Add to header or a fixed position
        const header = document.querySelector('header') || document.querySelector('.header');
        if (header) {
            const container = header.querySelector('.container') || header;
            const statusContainer = document.createElement('div');
            statusContainer.className = 'network-status-container ms-3';
            statusContainer.appendChild(statusElement);
            container.appendChild(statusContainer);
        }
    }

    // Monitor large file uploads/downloads
    monitorNetworkActivity() {
        // Monitor fetch requests
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = Date.now();
            const url = args[0];

            try {
                const response = await originalFetch.apply(this, args);
                const duration = Date.now() - startTime;

                // Log slow requests
                if (duration > 5000) {
                    console.warn(`Slow network request (${duration}ms):`, url);
                }

                return response;
            } catch (error) {
                const duration = Date.now() - startTime;
                console.error(`Network request failed (${duration}ms):`, url, error);
                throw error;
            }
        };

        // Monitor XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalSend = xhr.send;

            xhr.send = function() {
                const startTime = Date.now();
                xhr.addEventListener('loadend', () => {
                    const duration = Date.now() - startTime;
                    if (duration > 5000) {
                        console.warn(`Slow XHR request (${duration}ms):`, xhr.responseURL);
                    }
                });
                return originalSend.apply(this, arguments);
            };

            return xhr;
        };
    }

    // Auto-retry failed requests
    setupAutoRetry() {
        const retryFetch = async (url, options = {}, retries = 3) => {
            for (let i = 0; i < retries; i++) {
                try {
                    const response = await fetch(url, options);
                    if (response.ok) {
                        return response;
                    }
                } catch (error) {
                    if (i === retries - 1) {
                        throw error;
                    }
                    // Wait before retry (exponential backoff)
                    await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
                }
            }
        };

        // Replace fetch with retry version
        window.retryFetch = retryFetch;
    }

    // Clean up
    destroy() {
        this.stopPeriodicCheck();
        // Remove event listeners if needed
    }
}

// Global instance
window.ValidoAIInternetChecker = new ValidoAIInternetChecker();

// Auto-initialize network status in header
document.addEventListener('DOMContentLoaded', function() {
    if (typeof ValidoAIInternetChecker !== 'undefined') {
        setTimeout(() => {
            ValidoAIInternetChecker.addNetworkStatusToPage();
            ValidoAIInternetChecker.monitorNetworkActivity();
            ValidoAIInternetChecker.setupAutoRetry();
        }, 1000);
    }
});
