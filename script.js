gsap.registerPlugin(ScrollTrigger);

// ── Hero: page-load sequential reveal ──────────────────────────
const heroTl = gsap.timeline({ defaults: { duration: 0.8, ease: "power3.out" } });
heroTl
    .to("#hero-badge", { opacity: 1, y: 0, delay: 0.2 })
    .to("#hero-title", { opacity: 1, y: 0 }, "-=0.5")
    .to("#hero-desc", { opacity: 1, y: 0 }, "-=0.5")
    .to("#hero-buttons", { opacity: 1, y: 0 }, "-=0.5")
    .to("#hero-image", { opacity: 1, y: 0, duration: 1 }, "-=0.6");

// ── Our Creations: header slides from left, link fades ─────────
gsap.to("#creations-header", {
    scrollTrigger: { trigger: "#creations", start: "top 80%" },
    opacity: 1, x: 0, duration: 0.8, ease: "power3.out"
});
gsap.to("#creations-link", {
    scrollTrigger: { trigger: "#creations", start: "top 75%" },
    opacity: 1, y: 0, duration: 0.7, ease: "power3.out", delay: 0.2
});

// ── App cards: staggered slide-up ──────────────────────────────
gsap.to(".app-card", {
    scrollTrigger: { trigger: ".app-card", start: "top 85%" },
    opacity: 1, y: 0,
    duration: 0.8,
    ease: "power3.out",
    stagger: 0.18
});

// ── CTA card: scale up ─────────────────────────────────────────
gsap.to("#cta-card", {
    scrollTrigger: { trigger: "#cta-card", start: "top 85%" },
    opacity: 1, scale: 1,
    duration: 0.9,
    ease: "power3.out"
});

// ── Footer: fade in items ──────────────────────────────────────
gsap.from("footer", {
    scrollTrigger: { trigger: "footer", start: "top 90%" },
    opacity: 0, y: 30,
    duration: 0.8,
    ease: "power2.out"
});
