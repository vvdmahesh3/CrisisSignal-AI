/**
 * CrisisSignal AI — Dark Intelligence Premium UX Engine v4.0
 *
 * Implements all spec micro-interactions:
 *  1. IntersectionObserver fade-in (.reveal elements)
 *  2. Animated stat counters (count up from 0)
 *  3. Confidence bar fill on load (cubic-bezier premium easing)
 *  4. Confidence ring counter (SVG stroke-dashoffset animation)
 *  5. Scroll topbar blur (adds .scrolled to body)
 *  6. Vote button click ripple
 *  7. Toast notification system
 */

(function () {
    "use strict";

    /* ── 1. IntersectionObserver Fade-in ──────────────────────── */
    const revealObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    revealObserver.unobserve(entry.target); // fire once
                }
            });
        },
        { threshold: 0.08, rootMargin: "0px 0px -32px 0px" }
    );

    function initReveal() {
        document.querySelectorAll(".reveal").forEach((el) => {
            revealObserver.observe(el);
        });
    }

    /* ── 2. Stat Counter Animation ──────────────────────────────
       Usage: <span data-counter="42">0</span>
       Counts from 0 → target value on first viewport entry.      */
    const counterObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                const el = entry.target;
                const target = parseFloat(el.dataset.counter);
                const isFloat = el.dataset.counter.includes(".");
                const decimals = isFloat
                    ? (el.dataset.counter.split(".")[1] || "").length
                    : 0;
                const duration = 900;
                const start = performance.now();

                el.classList.add("counting");

                function tick(now) {
                    const elapsed = now - start;
                    const progress = Math.min(elapsed / duration, 1);
                    // ease-out cubic
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const value = target * eased;
                    el.textContent = isFloat
                        ? value.toFixed(decimals)
                        : Math.round(value);

                    if (progress < 1) {
                        requestAnimationFrame(tick);
                    } else {
                        el.textContent = isFloat
                            ? target.toFixed(decimals)
                            : target;
                        el.classList.remove("counting");
                    }
                }

                requestAnimationFrame(tick);
                counterObserver.unobserve(el);
            });
        },
        { threshold: 0.5 }
    );

    function initCounters() {
        document.querySelectorAll("[data-counter]").forEach((el) => {
            counterObserver.observe(el);
        });
    }

    /* ── 3. Confidence Bar Fill ─────────────────────────────────
       Usage: <div class="confidence-bar">
                <div class="confidence-fill" data-width="72"></div>
              </div>
       Animates width 0 → data-width% on page load.              */
    function initConfidenceBars() {
        // Small delay so page has rendered before animating
        setTimeout(() => {
            document.querySelectorAll(".confidence-fill[data-width]").forEach((bar) => {
                bar.style.width = bar.dataset.width + "%";
            });
        }, 150);
    }

    /* ── 4. Confidence Ring (SVG stroke-dashoffset) ─────────────
       Usage: <svg><circle class="confidence-ring-progress"
                    data-percent="72" ... /></svg>              */
    function initConfidenceRings() {
        document.querySelectorAll(".confidence-ring-progress").forEach((circle) => {
            const percent = parseFloat(circle.dataset.percent || 0);
            const r = parseFloat(circle.getAttribute("r") || 36);
            const circumference = 2 * Math.PI * r;

            circle.style.strokeDasharray = circumference;
            circle.style.strokeDashoffset = circumference; // start empty

            // Animate on next frame with premium easing via CSS transition
            circle.style.transition = `stroke-dashoffset 1s cubic-bezier(.16,1,.3,1)`;

            setTimeout(() => {
                const offset = circumference - (percent / 100) * circumference;
                circle.style.strokeDashoffset = offset;
            }, 200);
        });
    }

    /* ── 5. Scroll Topbar Blur ──────────────────────────────────
       Adds .scrolled to <body> when page is scrolled > 10px.
       CSS handles the blur effect on .topbar.                   */
    function initScrollBlur() {
        let ticking = false;
        window.addEventListener("scroll", () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    document.body.classList.toggle("scrolled", window.scrollY > 10);
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    /* ── 6. Ripple Effect on Buttons ────────────────────────────
       Adds a CSS ripple on click for any .btn element.          */
    function initRipple() {
        document.addEventListener("click", (e) => {
            const btn = e.target.closest(".btn");
            if (!btn) return;

            const ripple = document.createElement("span");
            const rect = btn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height) * 1.5;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px; height: ${size}px;
                left: ${e.clientX - rect.left - size / 2}px;
                top: ${e.clientY - rect.top - size / 2}px;
                background: rgba(255,255,255,0.08);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple-expand 0.4s ease-out forwards;
                pointer-events: none;
            `;

            // Ensure btn has position:relative for absolute ripple
            const prevPos = getComputedStyle(btn).position;
            if (prevPos === "static") btn.style.position = "relative";
            btn.style.overflow = "hidden";
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 450);
        });
    }

    /* ── 7. Toast Notification API ──────────────────────────────
       Usage: CrisisUI.toast("Alert saved", "success")
       Types: success | warning | error | info              */
    function createToastContainer() {
        let container = document.getElementById("toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            container.style.cssText = `
                position: fixed; top: 20px; right: 20px;
                z-index: 900; display: flex; flex-direction: column;
                gap: 10px; max-width: 360px; pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    function toast(message, type = "info", duration = 4000) {
        const colors = {
            success: { border: "rgba(34,197,94,0.35)", icon: "✓", color: "#22C55E" },
            warning: { border: "rgba(245,158,11,0.35)", icon: "!", color: "#F59E0B" },
            error:   { border: "rgba(239,68,68,0.35)",  icon: "✕", color: "#EF4444" },
            info:    { border: "rgba(59,130,246,0.35)",  icon: "i", color: "#3B82F6" },
        };
        const style = colors[type] || colors.info;
        const container = createToastContainer();

        const el = document.createElement("div");
        el.style.cssText = `
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px;
            background: #111318;
            border: 1px solid ${style.border};
            border-radius: 8px;
            font-size: 0.8125rem;
            color: #E5E7EB;
            box-shadow: 0 4px 16px rgba(0,0,0,0.5);
            pointer-events: all; cursor: pointer;
            opacity: 0; transform: translateX(16px);
            transition: opacity 0.25s ease, transform 0.25s ease;
        `;
        el.innerHTML = `
            <span style="color:${style.color};font-weight:700;font-size:1rem;">${style.icon}</span>
            <span style="flex:1">${message}</span>
            <span style="color:#4B5563;font-size:0.7rem;cursor:pointer;" onclick="this.closest('div').remove()">✕</span>
        `;

        container.appendChild(el);
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                el.style.opacity = "1";
                el.style.transform = "translateX(0)";
            });
        });

        const timer = setTimeout(() => dismissToast(el), duration);
        el.addEventListener("click", () => {
            clearTimeout(timer);
            dismissToast(el);
        });
    }

    function dismissToast(el) {
        el.style.opacity = "0";
        el.style.transform = "translateX(16px)";
        setTimeout(() => el.remove(), 260);
    }

    /* ── 8. Add .status-{status} class to alert rows ───────────
       Enables left-border color coding without modifying Python. */
    function initAlertStatusClasses() {
        document.querySelectorAll("[data-status]").forEach((el) => {
            const status = el.dataset.status;
            if (status) {
                el.classList.add(`status-${status.replace(/\s+/g, "_").toLowerCase()}`);
            }
        });
    }

    /* ── 9. Evidence Strength Preview ───────────────────────────
       3-bar quality indicator that updates as user types.
       Targets: #message textarea + #strength-bar-{1,2,3}       */
    function initEvidenceStrength() {
        const textarea = document.getElementById("message");
        if (!textarea) return;

        const bars = [1, 2, 3].map((n) =>
            document.getElementById(`strength-bar-${n}`)
        );
        if (!bars[0]) return;

        const scoreLabel = document.getElementById("strength-label");

        function calcScore(text) {
            let score = 0;
            if (text.length > 10) score++;
            if (text.length > 40) score++;
            if (text.length > 100) score++;
            // keyword bonus
            const keywords = [
                "fire", "smoke", "blood", "weapon", "unconscious",
                "broken", "leaking", "stuck", "help", "emergency",
                "floor", "block", "hostel", "gate", "road"
            ];
            if (keywords.some((kw) => text.toLowerCase().includes(kw))) score = Math.min(score + 1, 3);
            return score;
        }

        function updateBars(score) {
            const colors = ["#EF4444", "#F59E0B", "#22C55E"];
            const labels = ["Weak", "Moderate", "Strong"];
            bars.forEach((bar, i) => {
                if (!bar) return;
                bar.style.background = i < score ? colors[score - 1] : "rgba(255,255,255,0.08)";
                bar.style.transition = "background 0.3s ease";
            });
            if (scoreLabel) {
                scoreLabel.textContent = score > 0 ? labels[score - 1] : "";
                scoreLabel.style.color =
                    score === 3 ? "#22C55E" : score === 2 ? "#F59E0B" : "#EF4444";
            }
        }

        let debounce;
        textarea.addEventListener("input", () => {
            clearTimeout(debounce);
            debounce = setTimeout(() => updateBars(calcScore(textarea.value)), 120);
        });
    }

    /* ── CSS for ripple ─────────────────────────────────────────── */
    const style = document.createElement("style");
    style.textContent = `
        @keyframes ripple-expand {
            to { transform: scale(1); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    /* ── Initialize all modules on DOM ready ─────────────────── */
    function init() {
        initReveal();
        initCounters();
        initConfidenceBars();
        initConfidenceRings();
        initScrollBlur();
        initRipple();
        initAlertStatusClasses();
        initEvidenceStrength();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    /* ── Public API ───────────────────────────────────────────── */
    window.CrisisUI = {
        toast,
        initReveal,
        initCounters,
        initConfidenceBars,
        initConfidenceRings,
    };
})();
