// Enhanced QR Scanner JavaScript
class QRScannerManager {
    constructor() {
        this.scanner = null;
        this.isScanning = false;
        this.lastScanTime = 0;
        this.scanCooldown = 2000; // 2 seconds between scans
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeScanner();
    }

    setupEventListeners() {
        // Camera toggle button
        const cameraToggle = document.getElementById('camera-toggle');
        if (cameraToggle) {
            cameraToggle.addEventListener('click', () => this.toggleScanner());
        }

        // Manual entry form
        const manualForm = document.getElementById('manual-qr-form');
        if (manualForm) {
            manualForm.addEventListener('submit', (e) => this.handleManualEntry(e));
        }

        // Switch camera button
        const switchCamera = document.getElementById('switch-camera');
        if (switchCamera) {
            switchCamera.addEventListener('click', () => this.switchCamera());
        }
    }

    async initializeScanner() {
        try {
            // Check for camera permissions
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            
            this.updateStatus('Camera access granted. Click "Start Scanner" to begin.', 'success');
            document.getElementById('camera-toggle').disabled = false;
        } catch (error) {
            console.error('Camera access denied:', error);
            this.updateStatus('Camera access denied. Please use manual entry.', 'error');
            this.showManualEntry();
        }
    }

    async toggleScanner() {
        if (this.isScanning) {
            this.stopScanner();
        } else {
            await this.startScanner();
        }
    }

    async startScanner() {
        try {
            const qrCodeReader = document.getElementById('qr-reader');
            const toggleBtn = document.getElementById('camera-toggle');
            
            if (!qrCodeReader) return;

            // Import Html5Qrcode dynamically
            if (!window.Html5Qrcode) {
                await this.loadQRLibrary();
            }

            this.scanner = new Html5Qrcode("qr-reader");
            
            const qrCodeSuccessCallback = (decodedText, decodedResult) => {
                this.handleScanSuccess(decodedText);
            };

            const qrCodeErrorCallback = (errorMessage) => {
                // Handle scan errors silently for better UX
                console.log('QR scan error:', errorMessage);
            };

            const config = {
                fps: 10,
                qrbox: { width: 250, height: 250 },
                aspectRatio: 1.0,
                supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_QR_CODE]
            };

            await this.scanner.start(
                { facingMode: "environment" }, // Back camera
                config,
                qrCodeSuccessCallback,
                qrCodeErrorCallback
            );

            this.isScanning = true;
            toggleBtn.textContent = 'Stop Scanner';
            toggleBtn.classList.remove('btn-primary');
            toggleBtn.classList.add('btn-danger');
            
            this.updateStatus('Scanner active. Point camera at QR code.', 'info');
            this.hideManualEntry();

        } catch (error) {
            console.error('Error starting scanner:', error);
            this.updateStatus('Failed to start camera. Please try manual entry.', 'error');
            this.showManualEntry();
        }
    }

    stopScanner() {
        if (this.scanner && this.isScanning) {
            this.scanner.stop().then(() => {
                this.scanner.clear();
                this.scanner = null;
            }).catch(err => {
                console.error('Error stopping scanner:', err);
            });

            this.isScanning = false;
            const toggleBtn = document.getElementById('camera-toggle');
            toggleBtn.textContent = 'Start Scanner';
            toggleBtn.classList.remove('btn-danger');
            toggleBtn.classList.add('btn-primary');
            
            this.updateStatus('Scanner stopped.', 'info');
        }
    }

    async switchCamera() {
        if (!this.isScanning) return;

        try {
            await this.scanner.stop();
            
            // Try front camera
            await this.scanner.start(
                { facingMode: "user" },
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 },
                    aspectRatio: 1.0
                },
                (decodedText) => this.handleScanSuccess(decodedText),
                (errorMessage) => console.log('QR scan error:', errorMessage)
            );

            this.updateStatus('Switched to front camera.', 'info');
        } catch (error) {
            console.error('Error switching camera:', error);
            this.updateStatus('Failed to switch camera.', 'error');
        }
    }

    handleScanSuccess(qrText) {
        const now = Date.now();
        if (now - this.lastScanTime < this.scanCooldown) {
            return; // Prevent duplicate scans
        }
        this.lastScanTime = now;

        // Extract UUID from QR code
        const uuid = this.extractUUID(qrText);
        if (uuid) {
            this.processCheckin(uuid, qrText);
        } else {
            this.updateStatus('Invalid QR code format.', 'error');
        }
    }

    handleManualEntry(event) {
        event.preventDefault();
        const qrInput = document.getElementById('manual-qr-input');
        const qrText = qrInput.value.trim();
        
        if (!qrText) {
            this.updateStatus('Please enter a QR code.', 'error');
            return;
        }

        const uuid = this.extractUUID(qrText);
        if (uuid) {
            this.processCheckin(uuid, qrText);
            qrInput.value = '';
        } else {
            this.updateStatus('Invalid QR code format.', 'error');
        }
    }

    extractUUID(qrText) {
        // Extract UUID from various QR code formats
        const uuidRegex = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
        const match = qrText.match(uuidRegex);
        return match ? match[0] : null;
    }

    async processCheckin(uuid, originalText) {
        try {
            this.updateStatus('Processing check-in...', 'info');
            
            const response = await fetch(`/checkin/process/${uuid}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ qr_code: originalText })
            });

            const data = await response.json();

            if (data.success) {
                this.updateStatus(`✅ ${data.message}`, 'success');
                this.showParticipantInfo(data.participant);
                this.updateEventStats(data.stats);
                this.playSuccessSound();
            } else {
                this.updateStatus(`❌ ${data.message}`, 'error');
                this.playErrorSound();
            }
        } catch (error) {
            console.error('Check-in error:', error);
            this.updateStatus('Network error. Please try again.', 'error');
            this.playErrorSound();
        }
    }

    showParticipantInfo(participant) {
        const infoDiv = document.getElementById('participant-info');
        if (!infoDiv || !participant) return;

        infoDiv.innerHTML = `
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-user-check"></i> Check-in Successful
                    </h6>
                </div>
                <div class="card-body">
                    <p><strong>Name:</strong> ${participant.name}</p>
                    <p><strong>Email:</strong> ${participant.email}</p>
                    ${participant.phone ? `<p><strong>Phone:</strong> ${participant.phone}</p>` : ''}
                    <p><strong>Status:</strong> <span class="badge bg-success">Attended</span></p>
                    <p><strong>Check-in Time:</strong> ${new Date().toLocaleString()}</p>
                </div>
            </div>
        `;
        infoDiv.style.display = 'block';

        // Hide after 5 seconds
        setTimeout(() => {
            infoDiv.style.display = 'none';
        }, 5000);
    }

    updateEventStats(stats) {
        if (!stats) return;

        const totalElement = document.getElementById('total-registered');
        const attendedElement = document.getElementById('total-attended');
        const pendingElement = document.getElementById('total-pending');

        if (totalElement) totalElement.textContent = stats.total_registered;
        if (attendedElement) attendedElement.textContent = stats.total_attended;
        if (pendingElement) pendingElement.textContent = stats.total_pending;
    }

    updateStatus(message, type) {
        const statusDiv = document.getElementById('scan-status');
        if (!statusDiv) return;

        statusDiv.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'}`;
        statusDiv.textContent = message;
        statusDiv.style.display = 'block';
    }

    showManualEntry() {
        const manualSection = document.getElementById('manual-entry-section');
        if (manualSection) {
            manualSection.style.display = 'block';
        }
    }

    hideManualEntry() {
        const manualSection = document.getElementById('manual-entry-section');
        if (manualSection) {
            manualSection.style.display = 'none';
        }
    }

    playSuccessSound() {
        // Play success sound if available
        if (window.Audio) {
            try {
                const audio = new Audio('/static/sounds/success.mp3');
                audio.volume = 0.3;
                audio.play().catch(() => {}); // Ignore errors
            } catch (e) {}
        }
    }

    playErrorSound() {
        // Play error sound if available
        if (window.Audio) {
            try {
                const audio = new Audio('/static/sounds/error.mp3');
                audio.volume = 0.3;
                audio.play().catch(() => {}); // Ignore errors
            } catch (e) {}
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    async loadQRLibrary() {
        return new Promise((resolve, reject) => {
            if (window.Html5Qrcode) {
                resolve();
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
}

// Initialize scanner when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('qr-reader')) {
        new QRScannerManager();
    }
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}
