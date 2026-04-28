/**
 * CrisisSignal AI — Core Application Logic (app.js)
 * Navigation, flash message auto-dismiss, sidebar toggle, global utilities
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((msg, index) => {
        setTimeout(() => {
            msg.style.animation = 'slideInRight 0.3s ease reverse forwards';
            setTimeout(() => msg.remove(), 300);
        }, 5000 + (index * 500));
    });

    // Re-initialize Lucide icons after dynamic content
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // ── Mobile Sidebar Toggle ────────────────────────────
    initSidebarToggle();

    // ── Active Nav Highlighting ──────────────────────────
    highlightActiveNav();

    // ── Smooth page entrance ─────────────────────────────
    document.body.classList.add('page-loaded');
});

/**
 * Initialize mobile sidebar toggle functionality
 */
function initSidebarToggle() {
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (!sidebar || !toggleBtn) return;

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close sidebar on outside click (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024 &&
            sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            e.target !== toggleBtn) {
            sidebar.classList.remove('open');
        }
    });
}

/**
 * Highlight the active navigation item based on current URL
 */
function highlightActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && (path === href || (href !== '/' && path.startsWith(href)))) {
            item.classList.add('active');
        }
    });
}

/**
 * Format a timestamp for display
 */
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = (now - date) / 1000;

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}

/**
 * Format a number with K/M suffixes for large values
 */
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

/**
 * Debounce utility — delays function execution until after wait period
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Copy text to clipboard with user feedback
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        if (typeof showToast !== 'undefined') {
            showToast('Copied to clipboard', 'success');
        }
    } catch (err) {
        console.error('Copy failed:', err);
    }
}
