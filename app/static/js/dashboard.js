/**
 * CrisisSignal AI — Dashboard Module v2.0
 * Counter animations, stat refresh, and admin dashboard utilities.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Animate stat counters on load ──────────────────────
    animateStatCounters();

    // ── Initialize intersection observers for scroll animations
    initScrollAnimations();
});

/**
 * Animate all stat counter elements from 0 to their target value.
 * Uses data-counter attribute for the target number.
 */
function animateStatCounters() {
    const counters = document.querySelectorAll('[data-counter]');
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.counter, 10);
        if (isNaN(target) || target === 0) {
            counter.textContent = '0';
            return;
        }

        const duration = 800;
        const startTime = performance.now();
        counter.textContent = '0';

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            counter.textContent = Math.round(target * eased);

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                counter.textContent = target;
            }
        }
        requestAnimationFrame(update);
    });
}

/**
 * Initialize scroll-based animations for elements with data-animate attribute.
 * Elements fade/slide in when they enter the viewport.
 */
function initScrollAnimations() {
    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('[data-animate]').forEach(el => {
        observer.observe(el);
    });
}

/**
 * Refresh dashboard stats from the API (for periodic updates)
 */
async function refreshDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) return;

        const data = await response.json();
        const stats = data.stats || data;

        // Update stat counters with animation
        const mappings = {
            'stat-critical': stats.critical,
            'stat-verified': stats.verified,
            'stat-verifying': stats.verifying,
            'stat-total-active': stats.total_active,
        };

        Object.entries(mappings).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el && value !== undefined) {
                const current = parseInt(el.textContent) || 0;
                if (current !== value) {
                    animateCounterTo(el, current, value);
                }
            }
        });
    } catch (err) {
        console.warn('[Dashboard] Stats refresh failed:', err.message);
    }
}

/**
 * Animate a single counter from one value to another
 */
function animateCounterTo(element, from, to) {
    const duration = 600;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = from + (to - from) * eased;
        element.textContent = Math.round(current);

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = to;
        }
    }
    requestAnimationFrame(update);
}
