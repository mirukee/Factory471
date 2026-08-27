(function () {
    "use strict";

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

    function init() {
        setupScrollMotion();
        setupSpotlights();
        setupExpandableCards();
    }

    function setupScrollMotion() {
        if (reduceMotion || typeof window.gsap === "undefined") return;

        const gsap = window.gsap;
        if (window.ScrollTrigger) gsap.registerPlugin(window.ScrollTrigger);

        const heroItems = ["#hero-badge", "#hero-title", "#hero-desc", "#hero-buttons", "#hero-image"]
            .map(function (selector) { return document.querySelector(selector); })
            .filter(Boolean);

        gsap.timeline({ defaults: { duration: .78, ease: "power3.out" } })
            .from(heroItems, { opacity: 0, y: 28, stagger: .1, clearProps: "transform,opacity" });

        if (!window.ScrollTrigger) return;

        const sectionHeader = document.getElementById("creations-header");
        if (sectionHeader) {
            gsap.from(sectionHeader, {
                scrollTrigger: { trigger: "#creations", start: "top 80%", once: true },
                opacity: 0, x: -28, duration: .72, ease: "power3.out", clearProps: "transform,opacity"
            });
        }

        const cards = gsap.utils.toArray(".app-card");
        if (cards.length) {
            gsap.from(cards, {
                scrollTrigger: { trigger: "#creations", start: "top 72%", once: true },
                opacity: 0, y: 34, duration: .74, ease: "power3.out", stagger: .09,
                clearProps: "transform,opacity"
            });
        }

        const cta = document.getElementById("cta-card");
        if (cta) {
            gsap.from(cta, {
                scrollTrigger: { trigger: cta, start: "top 84%", once: true },
                opacity: 0, scale: .965, duration: .84, ease: "power2.out", clearProps: "transform,opacity"
            });
        }

        const footer = document.querySelector("footer");
        if (footer) {
            gsap.from(footer, {
                scrollTrigger: { trigger: footer, start: "top 92%", once: true },
                opacity: 0, y: 24, duration: .7, ease: "power2.out", clearProps: "transform,opacity"
            });
        }

        window.addEventListener("load", function () { window.ScrollTrigger.refresh(); }, { once: true });
    }

    function setupSpotlights() {
        if (!finePointer || reduceMotion) return;

        const hero = document.getElementById("hero-image");
        const cardArtwork = Array.from(document.querySelectorAll(".app-card"))
            .map(function (card) { return card.querySelector('[style*="background-image"]')?.parentElement; })
            .filter(Boolean);
        const targets = [hero].concat(cardArtwork).filter(Boolean);

        targets.forEach(function (element) {
            element.classList.add("spotlight-target");
            let targetX = .5;
            let targetY = .5;
            let currentX = .5;
            let currentY = .5;
            let frame = 0;

            function render() {
                currentX += (targetX - currentX) * .18;
                currentY += (targetY - currentY) * .18;
                element.style.setProperty("--pointer-x", (currentX * 100).toFixed(2) + "%");
                element.style.setProperty("--pointer-y", (currentY * 100).toFixed(2) + "%");
                if (Math.abs(targetX - currentX) > .002 || Math.abs(targetY - currentY) > .002) {
                    frame = requestAnimationFrame(render);
                } else {
                    frame = 0;
                }
            }

            element.addEventListener("pointerenter", function () { element.classList.add("is-lit"); });
            element.addEventListener("pointermove", function (event) {
                const rect = element.getBoundingClientRect();
                targetX = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
                targetY = Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height));
                if (!frame) frame = requestAnimationFrame(render);
            });
            element.addEventListener("pointerleave", function () { element.classList.remove("is-lit"); });
        });
    }

    function setupExpandableCards() {
        const cards = Array.from(document.querySelectorAll(".app-card"));
        if (!cards.length) return;

        let expandedCard = null;
        let openScrollY = 0;

        cards.forEach(function (card, index) {
            const title = card.querySelector("h3");
            const description = card.querySelector("p");
            const actionArea = card.lastElementChild;
            const image = card.querySelector('[style*="background-image"]');
            if (!title || !description || !actionArea) return;

            actionArea.classList.add("app-card-actions");
            const panelId = "app-quick-view-" + (index + 1);
            const button = document.createElement("button");
            button.type = "button";
            button.className = "quick-view-button";
            button.textContent = "Quick view";
            button.setAttribute("aria-expanded", "false");
            button.setAttribute("aria-controls", panelId);
            actionArea.appendChild(button);

            const panel = document.createElement("div");
            panel.id = panelId;
            panel.className = "quick-view-panel";
            panel.setAttribute("aria-hidden", "true");
            panel.setAttribute("inert", "");

            const artwork = document.createElement("div");
            artwork.className = "quick-view-artwork";
            if (image && image.style.backgroundImage) artwork.style.backgroundImage = image.style.backgroundImage;

            const content = document.createElement("div");
            content.className = "quick-view-content";
            const kicker = document.createElement("span");
            kicker.className = "quick-view-kicker";
            kicker.textContent = "Product overview";
            const expandedTitle = document.createElement("h4");
            expandedTitle.className = "quick-view-title";
            expandedTitle.tabIndex = -1;
            expandedTitle.textContent = title.textContent.trim();
            const expandedDescription = document.createElement("p");
            expandedDescription.className = "quick-view-description";
            expandedDescription.textContent = description.textContent.trim();
            const links = document.createElement("div");
            links.className = "quick-view-links";
            Array.from(actionArea.querySelectorAll("a[href]")).forEach(function (link) {
                const clone = link.cloneNode(true);
                clone.removeAttribute("class");
                links.appendChild(clone);
            });
            content.append(kicker, expandedTitle, expandedDescription, links);
            panel.append(artwork, content);

            const close = document.createElement("button");
            close.type = "button";
            close.className = "quick-view-close";
            close.setAttribute("aria-label", "Close quick view");
            close.innerHTML = '<span class="material-symbols-outlined" aria-hidden="true">close</span>';
            card.append(panel, close);
            close.hidden = true;

            button.addEventListener("click", function (event) {
                const wasKeyboard = event.detail === 0;
                if (card === expandedCard) {
                    closeCard(card, button, panel, close, true);
                    return;
                }

                const previous = expandedCard;
                if (previous) {
                    const previousButton = previous.querySelector(".quick-view-button");
                    const previousPanel = previous.querySelector(".quick-view-panel");
                    const previousClose = previous.querySelector(".quick-view-close");
                    closeCard(previous, previousButton, previousPanel, previousClose, false);
                }

                animateGrid(function () {
                    expandedCard = card;
                    openScrollY = window.scrollY;
                    card.classList.add("is-expanded");
                    button.setAttribute("aria-expanded", "true");
                    button.textContent = "Close quick view";
                    panel.setAttribute("aria-hidden", "false");
                    panel.removeAttribute("inert");
                    close.hidden = false;
                });

                const cardTop = card.getBoundingClientRect().top + window.scrollY - 72;
                window.scrollTo({ top: cardTop, behavior: "auto" });

                window.setTimeout(function () {
                    if (wasKeyboard) expandedTitle.focus({ preventScroll: true });
                    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
                }, reduceMotion ? 0 : 430);
            });

            close.addEventListener("click", function () { closeCard(card, button, panel, close, true); });
            card.addEventListener("keydown", function (event) {
                if (event.key === "Escape" && card.classList.contains("is-expanded")) {
                    event.preventDefault();
                    closeCard(card, button, panel, close, true);
                }
            });
        });

        function closeCard(card, button, panel, close, restoreFocus) {
            if (!card || !button || !panel || !close) return;
            const beforeTop = button.getBoundingClientRect().top;
            animateGrid(function () {
                card.classList.remove("is-expanded");
                button.setAttribute("aria-expanded", "false");
                button.textContent = "Quick view";
                panel.setAttribute("aria-hidden", "true");
                panel.setAttribute("inert", "");
                close.hidden = true;
                if (expandedCard === card) expandedCard = null;
            });
            window.setTimeout(function () {
                const delta = button.getBoundingClientRect().top - beforeTop;
                if (Math.abs(delta) > 1) window.scrollBy({ top: delta, behavior: "auto" });
                if (restoreFocus) button.focus({ preventScroll: true });
                if (window.ScrollTrigger) window.ScrollTrigger.refresh();
            }, reduceMotion ? 0 : 430);
        }

        function animateGrid(change) {
            const first = new Map(cards.map(function (card) { return [card, card.getBoundingClientRect()]; }));
            change();
            if (reduceMotion || !("animate" in Element.prototype)) return;
            requestAnimationFrame(function () {
                cards.forEach(function (card) {
                    const start = first.get(card);
                    const end = card.getBoundingClientRect();
                    const dx = start.left - end.left;
                    const dy = start.top - end.top;
                    if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
                    card.animate([
                        { transform: "translate(" + dx + "px," + dy + "px)" },
                        { transform: "translate(0,0)" }
                    ], { duration: 420, easing: "cubic-bezier(.16,1,.3,1)" });
                });
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init, { once: true });
    } else {
        init();
    }
})();
