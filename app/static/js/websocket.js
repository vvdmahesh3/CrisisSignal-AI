/**
 * CrisisSignal AI — WebSocket Client v2.0
 * Real-time connection for live dashboard updates.
 * Includes: toast notifications, counter animations, live card injection.
 */

// Initialize Socket.IO connection
const socket = io();

// ── Connection Status ─────────────────────────────────────
socket.on('connect', () => {
    console.log('[WS] Connected to CrisisSignal AI');
    document.body.classList.add('ws-connected');
    document.body.classList.remove('ws-disconnected');

    // Show subtle connection indicator
    const indicator = document.getElementById('ws-indicator');
    if (indicator) {
        indicator.classList.add('connected');
        indicator.title = 'Real-time: Connected';
    }
});

socket.on('disconnect', () => {
    console.log('[WS] Disconnected');
    document.body.classList.remove('ws-connected');
    document.body.classList.add('ws-disconnected');

    const indicator = document.getElementById('ws-indicator');
    if (indicator) {
        indicator.classList.remove('connected');
        indicator.title = 'Real-time: Disconnected';
    }
});

socket.on('connect_error', (err) => {
    console.warn('[WS] Connection error:', err.message);
});

// ── New Alert Event ───────────────────────────────────────
socket.on('new_alert', (data) => {
    console.log('[WS] New alert:', data);

    // Show toast notification
    showToast(`New ${(data.type || 'GENERAL').toUpperCase()} alert at ${data.location || 'Unknown'}`, 'info');

    // If on admin dashboard, prepend to alert list
    const alertsList = document.getElementById('alerts-list');
    if (alertsList) {
        const row = createAlertRow(data);
        alertsList.insertBefore(row, alertsList.firstChild);
        lucide.createIcons();

        // Highlight new row briefly
        row.classList.add('alert-new-highlight');
        setTimeout(() => row.classList.remove('alert-new-highlight'), 3000);
    }

    // Update stat counters
    incrementStatCounter('stat-total-active', 1);
    incrementStatCounter('stat-total-alerts', 1);

    // Update the status-specific counter
    if (data.status) {
        incrementStatCounter(`stat-${data.status}`, 1);
    }
});

// ── Vote Update ───────────────────────────────────────────
socket.on('vote_update', (data) => {
    console.log('[WS] Vote update:', data);
    const alert = data.alert || data;
    const alertId = alert.id || alert.alert_id;

    // Update vote counts on detail page
    const confirmEl = document.getElementById(`confirm-count-${alertId}`);
    const rejectEl = document.getElementById(`reject-count-${alertId}`);

    if (confirmEl && alert.confirmations_count !== undefined) {
        animateCounter(confirmEl, parseInt(confirmEl.textContent) || 0, alert.confirmations_count);
    }
    if (rejectEl && alert.rejections_count !== undefined) {
        animateCounter(rejectEl, parseInt(rejectEl.textContent) || 0, alert.rejections_count);
    }
});

// ── Confidence Update ─────────────────────────────────────
socket.on('confidence_update', (data) => {
    console.log('[WS] Confidence update:', data);

    // Animate confidence bar
    const bar = document.querySelector(`#confidence-bar-${data.alert_id} .confidence-fill`);
    if (bar) {
        const newWidth = Math.round((data.new_confidence || 0) * 100);
        bar.style.width = `${newWidth}%`;
        bar.style.transition = 'width 0.6s cubic-bezier(0, 0, 0.2, 1)';
    }

    // Update confidence text with animation
    const valueEl = document.getElementById(`confidence-value-${data.alert_id}`);
    if (valueEl) {
        const oldVal = (data.old_confidence || 0) * 100;
        const newVal = (data.new_confidence || 0) * 100;
        animateCounter(valueEl, oldVal, newVal, '%');
    }
});

// ── Status Change ─────────────────────────────────────────
socket.on('status_change', (data) => {
    console.log('[WS] Status change:', data);

    // Update status badges on page
    const alertRow = document.querySelector(`[data-alert-id="${data.alert_id}"]`);
    if (alertRow) {
        // Remove old status class, add new
        alertRow.className = alertRow.className.replace(/status-\w+/g, '');
        alertRow.classList.add(`status-${data.new_status}`);

        // Update badge text
        const badge = alertRow.querySelector('.status-badge');
        if (badge) {
            badge.className = `status-badge badge-${data.new_status}`;
            badge.textContent = (data.new_status || '').replace('_', ' ').toUpperCase();

            // Flash the badge
            badge.style.animation = 'none';
            badge.offsetHeight; // trigger reflow
            badge.style.animation = 'pulseScale 0.4s ease';
        }
    }

    const oldStatus = (data.old_status || 'unknown').replace('_', ' ').toUpperCase();
    const newStatus = (data.new_status || 'unknown').replace('_', ' ').toUpperCase();
    const toastType = data.new_status === 'critical' ? 'error' : 'warning';
    showToast(`Alert #${data.alert_id}: ${oldStatus} → ${newStatus}`, toastType);
});

// ── Critical Alert ────────────────────────────────────────
socket.on('critical_alert', (data) => {
    console.log('[WS] CRITICAL ALERT:', data);

    // Full-screen flash effect
    const overlay = document.createElement('div');
    overlay.className = 'critical-overlay';
    document.body.appendChild(overlay);
    setTimeout(() => overlay.remove(), 3000);

    showToast(`🚨 CRITICAL: ${(data.type || 'UNKNOWN').toUpperCase()} at ${data.location || 'Unknown'}`, 'error');
});

// ── System Reset ──────────────────────────────────────────
socket.on('system_reset', (data) => {
    console.log('[WS] System reset');
    showToast('System has been reset. Refreshing...', 'info');
    setTimeout(() => location.reload(), 1500);
});

// ═══ UTILITY FUNCTIONS ════════════════════════════════════

/**
 * Show a toast notification with icon and auto-dismiss
 */
function showToast(message, type = 'info') {
    let container = document.getElementById('flash-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-container';
        container.id = 'flash-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info',
    };

    const toast = document.createElement('div');
    toast.className = `flash-message flash-${type} animate-fade-in`;
    toast.innerHTML = `
        <i data-lucide="${icons[type] || 'info'}"></i>
        <span>${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()" aria-label="Close notification">
            <i data-lucide="x" style="width:14px;height:14px;"></i>
        </button>
    `;
    container.appendChild(toast);

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(30px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

/**
 * Animate a counter from old value to new value
 */
function animateCounter(element, from, to, suffix = '') {
    const duration = 600;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = from + (to - from) * eased;
        element.textContent = Math.round(current) + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    requestAnimationFrame(update);
}

/**
 * Increment a stat counter by a given amount
 */
function incrementStatCounter(id, amount = 1) {
    const el = document.getElementById(id);
    if (!el) return;

    const current = parseInt(el.textContent) || 0;
    const target = current + amount;
    animateCounter(el, current, target);
}

/**
 * Create an alert row element from data (for live insertion)
 */
function createAlertRow(data) {
    const severity = (data.severity || 0) >= 7 ? 'high' : ((data.severity || 0) >= 4 ? 'medium' : 'low');
    const status = data.status || 'new';
    const confidence = data.confidence || 0;
    const type = data.type || 'general';

    const row = document.createElement('div');
    row.className = `alert-row status-${status} animate-fade-in-up`;
    row.setAttribute('data-alert-id', data.id || '');
    row.setAttribute('data-status', status);
    row.setAttribute('data-type', type);

    row.innerHTML = `
        <div class="alert-row-priority">
            <div class="severity-indicator severity-${severity}">${data.severity || 0}</div>
        </div>
        <div class="alert-row-main">
            <div class="alert-row-header">
                <span class="status-badge badge-${status}">${status.replace('_', ' ').toUpperCase()}</span>
                <span class="type-badge type-${type}">${type.toUpperCase()}</span>
                <span class="alert-location">
                    <i data-lucide="map-pin"></i>
                    ${data.location || 'Unknown'}
                </span>
            </div>
            <p class="alert-row-message">${(data.message || '').substring(0, 200)}</p>
            <div class="alert-row-meta">
                <span class="confidence-inline">
                    <span class="confidence-bar-mini">
                        <span class="confidence-fill" style="width: ${Math.round(confidence * 100)}%"></span>
                    </span>
                    ${Math.round(confidence * 100)}%
                </span>
                <span class="votes-inline">✅ ${data.confirmations_count || 0} / ❌ ${data.rejections_count || 0}</span>
                <span class="evidence-inline evidence-${(data.evidence_strength || 'weak').toLowerCase()}">${data.evidence_strength || 'Unknown'}</span>
            </div>
        </div>
        <div class="alert-row-actions">
            <a href="/alert/${data.id}" class="btn btn-ghost btn-sm">Details</a>
        </div>
    `;
    return row;
}
