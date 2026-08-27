(function () {
    "use strict";

    function ready() {
        const body = document.body;
        if (!body || body.classList.contains("site-enhanced")) return;

        document.documentElement.classList.remove("dark");
        body.classList.add("site-enhanced");

        if (document.getElementById("creations")) {
            body.classList.add("site-home");
        } else if (document.querySelector(".notion-doc")) {
            body.classList.add("site-doc");
        } else {
            body.classList.add("site-hub");
        }

        setupLogo();
        setupMobileNavigation();
        if (!body.classList.contains("site-home")) setupReveals();
    }

    function setupLogo() {
        const header = document.querySelector("body > header");
        const svg = header && header.querySelector("svg");
        if (!svg) return;

        const linkedLogo = svg.closest("a");
        const target = linkedLogo || svg.parentElement;
        if (!target) return;

        target.classList.add("logo-reactive");
        if (!linkedLogo) {
            target.tabIndex = 0;
            target.setAttribute("role", "img");
            target.setAttribute("aria-label", "FACTORY 471");
        } else if (!linkedLogo.getAttribute("aria-label")) {
            linkedLogo.setAttribute("aria-label", "FACTORY 471 home");
        }

        const orbit = document.createElement("span");
        orbit.className = "logo-orbit";
        orbit.setAttribute("aria-hidden", "true");
        target.appendChild(orbit);

        if (window.matchMedia("(hover: none), (pointer: coarse)").matches &&
            !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            window.setTimeout(function () { target.classList.add("logo-awake"); }, 280);
            window.setTimeout(function () { target.classList.remove("logo-awake"); }, 980);
        }
    }

    function setupMobileNavigation() {
        const header = document.querySelector("body > header");
        if (!header) return;

        let button = header.querySelector("button.md\\:hidden");
        const sourceLinks = Array.from(header.querySelectorAll("a[href]"))
            .filter(function (link, index, links) {
                const text = link.textContent.trim();
                if (!text) return false;
                return links.findIndex(function (item) {
                    return item.getAttribute("href") === link.getAttribute("href") && item.textContent.trim() === text;
                }) === index;
            });

        if (!button && sourceLinks.length > 1) {
            button = document.createElement("button");
            button.type = "button";
            button.className = "mobile-nav-trigger";
            button.innerHTML = '<span class="material-symbols-outlined" aria-hidden="true">menu</span>';
            header.appendChild(button);
        }
        if (!button || sourceLinks.length === 0) return;

        button.type = "button";
        button.classList.add("mobile-nav-trigger");
        button.setAttribute("aria-label", "Open navigation");
        button.setAttribute("aria-expanded", "false");
        button.setAttribute("aria-controls", "mobile-site-navigation");

        const panel = document.createElement("div");
        panel.id = "mobile-site-navigation";
        panel.className = "mobile-nav-panel";
        panel.hidden = true;

        sourceLinks.forEach(function (link) {
            const clone = link.cloneNode(true);
            clone.removeAttribute("class");
            panel.appendChild(clone);
        });
        header.appendChild(panel);

        function setOpen(open) {
            button.setAttribute("aria-expanded", String(open));
            button.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
            panel.hidden = !open;
            header.classList.toggle("mobile-nav-open", open);
            const icon = button.querySelector(".material-symbols-outlined");
            if (icon) icon.textContent = open ? "close" : "menu";
        }

        button.addEventListener("click", function () {
            setOpen(button.getAttribute("aria-expanded") !== "true");
        });
        panel.addEventListener("click", function (event) {
            if (event.target.closest("a")) setOpen(false);
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && button.getAttribute("aria-expanded") === "true") {
                setOpen(false);
                button.focus();
            }
        });
    }

    function setupReveals() {
        const body = document.body;
        let targets = [];

        if (body.classList.contains("site-doc")) {
            targets = [
                document.querySelector(".doc-wrap > nav"),
                document.querySelector(".doc-wrap > .grid > div:first-child > div:first-child"),
                ...document.querySelectorAll("aside > div > div"),
                document.querySelector("footer")
            ];
        } else {
            targets = [
                document.querySelector("body > div.relative.w-full.border-b"),
                ...document.querySelectorAll(".flex-1 .grid > .group"),
                document.querySelector("footer")
            ];
        }

        targets = targets.filter(Boolean);
        targets.forEach(function (target, index) {
            target.classList.add("site-reveal");
            target.dataset.delay = String(Math.min(index % 4, 3));
        });
        if (!targets.length) return;

        document.documentElement.classList.add("reveal-ready");
        if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            targets.forEach(function (target) { target.classList.add("is-visible"); });
            return;
        }

        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });

        targets.forEach(function (target) { observer.observe(target); });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", ready, { once: true });
    } else {
        ready();
    }
})();
