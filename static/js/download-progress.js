/**
 * Download Progress Management
 * Handles model download progress tracking and UI updates
 */

class DownloadProgressManager {
    constructor() {
        this.downloads = new Map();
        this.progressCallbacks = [];
        this.toastContainer = null;
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'toast-container';
            this.toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(this.toastContainer);
        }
    }

    // API Methods
    async startDownload(modelId, modelName) {
        try {
            const response = await fetch(`/api/download/models/${modelId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            // Show success toast
            this.showToast(`Started downloading ${modelName}`, 'success');

            // Start progress polling
            this.startProgressPolling(modelId);

            return result;
        } catch (error) {
            console.error('Error starting download:', error);
            this.showToast(`Failed to start download: ${error.message}`, 'error');
            throw error;
        }
    }

    async cancelDownload(modelId) {
        try {
            const response = await fetch(`/api/download/models/${modelId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.showToast('Download cancelled', 'info');
            return await response.json();
        } catch (error) {
            console.error('Error cancelling download:', error);
            this.showToast(`Failed to cancel download: ${error.message}`, 'error');
            throw error;
        }
    }

    async getDownloadStatus(modelId) {
        try {
            const response = await fetch(`/api/download/models/${modelId}/status`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting download status:', error);
            throw error;
        }
    }

    async getAllDownloadsStatus() {
        try {
            const response = await fetch('/api/download/models/status');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting all download statuses:', error);
            throw error;
        }
    }

    async startBatchDownload(modelIds) {
        try {
            const response = await fetch('/api/download/models/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ model_ids: modelIds })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            // Show success toast
            this.showToast(`Started ${result.download_ids.length} downloads`, 'success');

            // Start progress polling for all downloads
            modelIds.forEach(modelId => this.startProgressPolling(modelId));

            return result;
        } catch (error) {
            console.error('Error starting batch download:', error);
            this.showToast(`Failed to start downloads: ${error.message}`, 'error');
            throw error;
        }
    }

    // Progress Polling
    startProgressPolling(modelId) {
        const pollInterval = setInterval(async () => {
            try {
                const result = await this.getDownloadStatus(modelId);
                const status = result.status;

                // Update progress callbacks
                this.progressCallbacks.forEach(callback => {
                    callback(modelId, status);
                });

                // Check if download is complete
                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    this.showToast(`${status.model_name} download completed!`, 'success');
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    this.showToast(`${status.model_name} download failed: ${status.error_message}`, 'error');
                } else if (status.status === 'cancelled') {
                    clearInterval(pollInterval);
                    this.showToast(`${status.model_name} download cancelled`, 'info');
                }

            } catch (error) {
                console.error('Error polling download status:', error);
                clearInterval(pollInterval);
            }
        }, 1000); // Poll every second

        // Store interval for cleanup
        this.downloads.set(modelId, { pollInterval });
    }

    stopProgressPolling(modelId) {
        if (this.downloads.has(modelId)) {
            const { pollInterval } = this.downloads.get(modelId);
            clearInterval(pollInterval);
            this.downloads.delete(modelId);
        }
    }

    // Toast Notifications
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 transform transition-all duration-300 ease-in-out`;

        const colors = {
            success: 'border-green-500 bg-green-50',
            error: 'border-red-500 bg-red-50',
            warning: 'border-yellow-500 bg-yellow-50',
            info: 'border-blue-500 bg-blue-50'
        };

        toast.innerHTML = `
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i class="fas ${this.getIconForType(type)} text-${type === 'success' ? 'green' : type === 'error' ? 'red' : type === 'warning' ? 'yellow' : 'blue'}-600"></i>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-gray-900">${message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" onclick="this.parentElement.parentElement.parentElement.remove()">
                            <span class="sr-only">Close</span>
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        toast.classList.add(colors[type]);
        this.toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }

    getIconForType(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            case 'info': default: return 'fa-info-circle';
        }
    }

    // Progress Callbacks
    addProgressCallback(callback) {
        this.progressCallbacks.push(callback);
    }

    removeProgressCallback(callback) {
        const index = this.progressCallbacks.indexOf(callback);
        if (index > -1) {
            this.progressCallbacks.splice(index, 1);
        }
    }

    // Utility Methods
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatTime(seconds) {
        if (seconds < 60) return `${Math.round(seconds)}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.round(seconds % 60);
        return `${minutes}m ${remainingSeconds}s`;
    }

    // Cleanup
    cleanup() {
        // Stop all polling intervals
        this.downloads.forEach(({ pollInterval }) => {
            clearInterval(pollInterval);
        });
        this.downloads.clear();

        // Remove toast container
        if (this.toastContainer) {
            this.toastContainer.remove();
        }
    }
}

// Global instance
const downloadProgressManager = new DownloadProgressManager();

// Export for global use
window.DownloadProgressManager = DownloadProgressManager;
window.downloadProgressManager = downloadProgressManager;
