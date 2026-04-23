/**
 * main.js
 * -------
 * Scripts globaux : flash messages, confirmations, tooltips Bootstrap.
 * Chargé sur toutes les pages via base.html.
 */

"use strict";

// ── Auto-dismiss flash messages ─────────────────────────────────────────
(function initFlashMessages() {
    const DELAY_MS = 5000;

    document.addEventListener("DOMContentLoaded", function () {
        const alerts = document.querySelectorAll(".flash-alert");

        alerts.forEach(function (alert) {
            // Disparition automatique après DELAY_MS
            setTimeout(function () {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            }, DELAY_MS);
        });
    });
})();


// ── Tooltips Bootstrap ──────────────────────────────────────────────────
(function initTooltips() {
    document.addEventListener("DOMContentLoaded", function () {
        const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipEls.forEach(function (el) {
            new bootstrap.Tooltip(el, { trigger: "hover" });
        });
    });
})();


// ── Popovers Bootstrap ──────────────────────────────────────────────────
(function initPopovers() {
    document.addEventListener("DOMContentLoaded", function () {
        const popoverEls = document.querySelectorAll('[data-bs-toggle="popover"]');
        popoverEls.forEach(function (el) {
            new bootstrap.Popover(el);
        });
    });
})();


// ── Confirmation avant suppression ──────────────────────────────────────
/**
 * Ajoute une confirmation sur tous les formulaires de suppression.
 * Usage : <form data-confirm="Supprimer ce projet ?"> ... </form>
 */
(function initConfirmForms() {
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("form[data-confirm]").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                const message = form.dataset.confirm || "Confirmer cette action ?";
                if (!window.confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    });
})();


// ── Active nav link ─────────────────────────────────────────────────────
/**
 * Met en évidence le lien de navigation correspondant à l'URL courante.
 */
(function highlightActiveNav() {
    document.addEventListener("DOMContentLoaded", function () {
        const currentPath = window.location.pathname;
        document.querySelectorAll(".navbar-custom .nav-link").forEach(function (link) {
            const href = link.getAttribute("href");
            if (href && href !== "/" && currentPath.startsWith(href)) {
                link.classList.add("active");
            }
        });
    });
})();


// ── Toggle visibilité mot de passe ──────────────────────────────────────
/**
 * Exposée globalement pour les boutons inline dans les templates.
 * Usage : onclick="togglePassword('inputId', this)"
 */
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon  = btn.querySelector("i");
    if (!input || !icon) return;

    if (input.type === "password") {
        input.type    = "text";
        icon.className = "bi bi-eye-slash";
    } else {
        input.type    = "password";
        icon.className = "bi bi-eye";
    }
}


// ── Fade-in au chargement ───────────────────────────────────────────────
(function initFadeIn() {
    document.addEventListener("DOMContentLoaded", function () {
        document.body.style.opacity = "0";
        document.body.style.transition = "opacity .25s ease";
        requestAnimationFrame(function () {
            document.body.style.opacity = "1";
        });
    });
})();


// ── Retour en haut de page ──────────────────────────────────────────────
(function initBackToTop() {
    document.addEventListener("DOMContentLoaded", function () {
        // Crée le bouton dynamiquement
        const btn = document.createElement("button");
        btn.id        = "backToTop";
        btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        btn.title     = "Retour en haut";
        btn.setAttribute("aria-label", "Retour en haut de page");
        Object.assign(btn.style, {
            position:   "fixed",
            bottom:     "1.5rem",
            right:      "1.5rem",
            zIndex:     "999",
            width:      "42px",
            height:     "42px",
            borderRadius: "50%",
            border:     "none",
            background: "var(--primary)",
            color:      "white",
            fontSize:   "1.1rem",
            cursor:     "pointer",
            boxShadow:  "0 4px 12px rgba(37,99,235,.35)",
            display:    "none",
            alignItems: "center",
            justifyContent: "center",
            transition: "opacity .2s, transform .2s",
        });
        document.body.appendChild(btn);

        window.addEventListener("scroll", function () {
            if (window.scrollY > 300) {
                btn.style.display = "flex";
            } else {
                btn.style.display = "none";
            }
        });

        btn.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    });
})();