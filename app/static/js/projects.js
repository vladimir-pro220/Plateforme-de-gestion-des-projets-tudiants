/**
 * projects.js
 * -----------
 * Recherche live et filtres dynamiques sur la liste des projets.
 * Chargé uniquement sur projects/list.html via {% block extra_js %}.
 */

"use strict";

// ── Recherche live ──────────────────────────────────────────────────────
/**
 * Filtre les cartes projets en temps réel selon la saisie
 * dans le champ de recherche, sans rechargement de page.
 * Si aucun résultat local, soumet le formulaire vers le serveur.
 */
(function initLiveSearch() {
    document.addEventListener("DOMContentLoaded", function () {
        const searchInput = document.querySelector('input[name="search"]');
        const projectCards = document.querySelectorAll(".project-card");
        const noResultsEl = document.getElementById("noResultsLocal");

        if (!searchInput || projectCards.length === 0) return;

        searchInput.addEventListener("input", function () {
            const query = searchInput.value.trim().toLowerCase();
            let visibleCount = 0;

            projectCards.forEach(function (card) {
                const title = card.querySelector(".project-card-title");
                const domain = card.querySelector(".domain-badge");
                const desc = card.querySelector(".project-card-desc");

                const titleText  = title  ? title.textContent.toLowerCase()  : "";
                const domainText = domain ? domain.textContent.toLowerCase() : "";
                const descText   = desc   ? desc.textContent.toLowerCase()   : "";

                const matches = !query
                    || titleText.includes(query)
                    || domainText.includes(query)
                    || descText.includes(query);

                const wrapper = card.closest(".col-md-6, .col-lg-4, [class*='col-']");
                if (wrapper) {
                    wrapper.style.display = matches ? "" : "none";
                }

                if (matches) visibleCount++;
            });

            // Message aucun résultat local
            if (noResultsEl) {
                noResultsEl.style.display = visibleCount === 0 ? "block" : "none";
            }
        });

        // Efface la recherche live si le champ est vidé
        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                searchInput.value = "";
                searchInput.dispatchEvent(new Event("input"));
            }
        });
    });
})();


// ── Filtre dynamique par domaine ────────────────────────────────────────
/**
 * Met à jour la liste en temps réel quand on change le select domaine,
 * puis soumet le formulaire si nécessaire pour la pagination serveur.
 */
(function initDomainFilter() {
    document.addEventListener("DOMContentLoaded", function () {
        const domainSelect = document.querySelector('select[name="domain"]');
        const statusSelect = document.querySelector('select[name="status"]');

        if (!domainSelect && !statusSelect) return;

        // Soumission automatique au changement de filtre
        [domainSelect, statusSelect].forEach(function (select) {
            if (!select) return;
            select.addEventListener("change", function () {
                // Réinitialise la page à 1 avant de soumettre
                const form = select.closest("form");
                if (!form) return;

                let pageInput = form.querySelector('input[name="page"]');
                if (!pageInput) {
                    pageInput = document.createElement("input");
                    pageInput.type = "hidden";
                    pageInput.name = "page";
                    form.appendChild(pageInput);
                }
                pageInput.value = "1";
                form.submit();
            });
        });
    });
})();


// ── Compteur de caractères (motivation) ────────────────────────────────
/**
 * Affiche un compteur de caractères sous le textarea de motivation.
 */
(function initCharCounter() {
    document.addEventListener("DOMContentLoaded", function () {
        const textarea = document.querySelector('textarea[name="motivation"]');
        if (!textarea) return;

        const MIN_CHARS = 50;
        const counter = document.createElement("div");
        counter.className = "form-text mt-1 char-counter";
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);

        function updateCounter() {
            const len = textarea.value.length;
            const remaining = Math.max(0, MIN_CHARS - len);

            if (remaining > 0) {
                counter.textContent = `Encore ${remaining} caractère(s) minimum requis.`;
                counter.style.color = "var(--warning)";
            } else {
                counter.textContent = `${len} caractère(s) — ✓`;
                counter.style.color = "var(--success)";
            }
        }

        textarea.addEventListener("input", updateCounter);
        updateCounter();
    });
})();


// ── Confirmation upload CV ──────────────────────────────────────────────
/**
 * Affiche le nom du fichier sélectionné sous l'input file.
 */
(function initFileInput() {
    document.addEventListener("DOMContentLoaded", function () {
        const fileInput = document.querySelector('input[type="file"][name="cv_file"]');
        if (!fileInput) return;

        fileInput.addEventListener("change", function () {
            const file = fileInput.files[0];
            if (!file) return;

            // Vérification taille côté client (5 Mo)
            const MAX_SIZE = 5 * 1024 * 1024;
            if (file.size > MAX_SIZE) {
                alert("Le fichier dépasse la taille maximale autorisée (5 Mo).");
                fileInput.value = "";
                return;
            }

            // Affiche le nom du fichier
            let feedback = fileInput.parentNode.querySelector(".file-feedback");
            if (!feedback) {
                feedback = document.createElement("div");
                feedback.className = "form-text file-feedback mt-1";
                fileInput.parentNode.appendChild(feedback);
            }
            feedback.innerHTML =
                `<i class="bi bi-file-earmark-check text-success me-1"></i>
                 Fichier sélectionné : <strong>${file.name}</strong>
                 (${(file.size / 1024).toFixed(1)} Ko)`;
        });
    });
})();


// ── Highlight mot recherché ─────────────────────────────────────────────
/**
 * Met en surbrillance le terme recherché dans les titres des cartes.
 */
(function initSearchHighlight() {
    document.addEventListener("DOMContentLoaded", function () {
        const searchInput = document.querySelector('input[name="search"]');
        if (!searchInput || !searchInput.value.trim()) return;

        const query = searchInput.value.trim();
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");

        document.querySelectorAll(".project-card-title").forEach(function (el) {
            el.innerHTML = el.textContent.replace(
                regex,
                '<mark class="bg-warning px-0">$1</mark>'
            );
        });
    });
})();