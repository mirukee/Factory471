# FACTORY 471 Website Design Specification

> Reference: [Apple.com](https://www.apple.com/) (reviewed 2026-08-28)  
> Goal: redesign the FACTORY 471 website with an Apple-inspired, content-first visual system while preserving the studio’s own identity. This is a design reference, not a request to copy Apple trademarks, product imagery, or proprietary assets.

## 1. Design direction

The experience should feel calm, precise, and product-led. Replace the current dark neon/game-like treatment with generous white space, large editorial typography, crisp product imagery, and a restrained palette. Each section should communicate one idea and one primary action.

Key qualities:

- Minimal chrome and a compact translucent navigation bar
- One strong headline per section
- Large, edge-to-edge campaign panels followed by a modular product grid
- Mostly neutral colors with blue reserved for links and primary actions
- Soft motion used to clarify hierarchy, never as decoration
- Scroll-triggered reveals that introduce sections and cards as the user moves down the page

## 2. Information architecture

Global navigation:

1. Logo / FACTORY 471
2. Apps
3. About
4. Blog
5. Support
6. Search icon
7. Contact icon or button

Homepage order:

1. Global navigation
2. Optional announcement strip
3. Hero campaign
4. Featured app campaign
5. App collection with scroll-triggered card reveals
6. Studio values / capabilities
7. Latest articles or updates
8. Footer directory and legal information

## 3. Layout system

- Maximum content width: `1200px`
- Wide campaign width: `100%`, with `12px` page gutters on desktop and `0` on mobile
- Text measure: `620px` maximum for hero copy, `520px` for card copy
- Desktop grid: 12 columns, `24px` gutters
- Tablet grid: 8 columns, `20px` gutters
- Mobile grid: 4 columns, `16px` gutters
- Section spacing: `96–120px` desktop, `64–80px` tablet, `48–64px` mobile
- Card gap: `12px` on desktop, `10px` on mobile
- Breakpoints: mobile `< 734px`, tablet `734–1023px`, desktop `>= 1024px`

Cards should align to a consistent grid but may vary in size. Use a 2-column desktop mosaic for secondary campaigns and a single column on mobile.

## 4. Visual tokens

### Color

| Token | Value | Use |
|---|---:|---|
| `--color-text` | `#1D1D1F` | Primary text |
| `--color-muted` | `#6E6E73` | Supporting text |
| `--color-link` | `#0066CC` | Links and primary text actions |
| `--color-bg` | `#FFFFFF` | Main background |
| `--color-surface` | `#F5F5F7` | Navigation, cards, alternate sections |
| `--color-divider` | `#D2D2D7` | Rules and inactive controls |
| `--color-dark` | `#000000` | Dark campaign panels |
| `--color-focus` | `#0071E3` | Focus outline |

App-specific accent colors may appear inside product artwork, but interface controls remain neutral or blue.

### Typography

Use the system stack to approximate Apple’s clean typography without distributing proprietary fonts:

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif;
```

| Style | Desktop | Mobile | Weight / line height |
|---|---:|---:|---|
| Hero headline | `56px` | `40px` | `700 / 1.05` |
| Campaign headline | `48px` | `32px` | `700 / 1.08` |
| Section title | `40px` | `28px` | `700 / 1.12` |
| Card title | `28px` | `24px` | `650 / 1.15` |
| Lead copy | `24px` | `19px` | `400 / 1.35` |
| Body | `17px` | `16px` | `400 / 1.5` |
| Navigation | `12px` | `14px` | `400 / 1.2` |
| Footnote | `12px` | `12px` | `400 / 1.4` |

Use slightly negative letter spacing only on headlines. Korean copy should prioritize legibility and avoid aggressive tracking.

### Shape and elevation

- Navigation: no visible border; subtle bottom hairline when scrolled
- Campaign panels: `0–18px` radius depending on edge treatment
- Product cards: `18px` radius
- Buttons: pill shape, `999px` radius
- Shadows: use sparingly; prefer surface contrast
- Focus ring: `2px solid var(--color-focus)` plus `2px` offset

## 5. Core components

### Global navigation

- Height: `44px` desktop, `48px` mobile
- Background: `rgba(245,245,247,.82)` with `backdrop-filter: saturate(180%) blur(20px)`
- Sticky at the top, `z-index: 100`
- Desktop navigation items remain visually light and evenly spaced
- Mobile shows logo, search, and menu; the menu opens as a full-width sheet
- All icon-only buttons require visible accessible labels

### Announcement strip

- White background, centered copy, `14px`
- One sentence and one inline link only
- May be dismissed; remember dismissal locally

### Hero campaign

- Minimum height: `680px` desktop, `560px` mobile
- Center-aligned content with headline, one-line description, and one or two actions
- Product artwork occupies the lower or background portion of the panel
- Primary action: filled blue pill; secondary action: blue text link with chevron
- Use either a light or dark hero, chosen to match the artwork’s contrast

Suggested content:

```text
Useful apps. Thoughtfully made.
FACTORY 471 creates focused mobile products for everyday moments.
[Explore apps] [About the studio ›]
```

### Featured campaign

Highlight one current product at a time. The layout mirrors the hero at a smaller scale:

- Eyebrow: category or release status
- Product name
- Short value proposition
- `Learn more` and `Download` actions
- Large device mockup or abstract product artwork

### App collection

- Section title: “Our apps”
- Optional category filters above the grid: `All`, `Utility`, `Lifestyle`, `Sports`, `Music`
- Desktop: 3 cards per row
- Tablet: 2 cards per row
- Mobile: 1 card per row
- Render the full app collection on one continuous page; do not split it into numbered pages
- Card order must remain stable when filters change

Each app card contains:

1. Large image area in `4:3` or `16:10`
2. Category eyebrow
3. App name
4. Two-line summary
5. Platform/status metadata
6. `Quick view` button and `Learn more` text link

Hover may lift artwork by `2px` and slightly deepen the surface. Do not move the entire layout enough to cause reflow.

## 6. Scroll-triggered reveal animation

The homepage is one continuous scrolling experience. Sections and cards reveal when they enter the viewport, matching the interaction pattern already used on the current FACTORY 471 site. This is a scroll-triggered animation, not pagination.

### Initial states

Apply the hidden state only after JavaScript has initialized so content remains visible when JavaScript is unavailable.

```css
.anim-ready .reveal-up {
  opacity: 0;
  transform: translateY(32px);
}

.anim-ready .reveal-left {
  opacity: 0;
  transform: translateX(-32px);
}

.anim-ready .reveal-scale {
  opacity: 0;
  transform: scale(.96);
}
```

### Trigger behavior

- Hero elements reveal once on page load in this order: eyebrow, headline, description, actions, artwork
- Each section header begins when its top reaches approximately `80%` of the viewport height
- App cards begin when the first card reaches approximately `85%` of the viewport height
- Cards animate upward with a `60–120ms` stagger, following visual reading order
- Large campaign artwork uses a subtle scale reveal; supporting copy may slide in from the left
- Footer content uses one simple fade-up animation
- Animations play once by default and do not reverse when scrolling upward
- Anchor navigation must land with the target content visible rather than hidden mid-animation

### Timing and easing

| Element | Duration | Movement | Easing |
|---|---:|---:|---|
| Hero text | `650–800ms` | `24px` upward | `power3.out` |
| Section header | `600–750ms` | `32px` horizontally or upward | `power3.out` |
| App card | `650–800ms` | `28–36px` upward | `power3.out` |
| Campaign artwork | `800–1000ms` | scale `.96 → 1` | `power2.out` |
| Footer | `600–800ms` | `24px` upward | `power2.out` |

### Implementation guidance

- Use the existing GSAP and `ScrollTrigger` setup
- Register `ScrollTrigger` once and create one trigger per section or related card group
- Animate cards as a group with `stagger` instead of creating a separate observer for every card
- Use transforms and opacity only to avoid layout shifts
- Call `ScrollTrigger.refresh()` after late-loading images or fonts affect layout
- Ensure animated content is already present in the DOM and readable by assistive technology
- Do not use infinite scroll, numbered pagination, or scroll-jacking
- If filtering is retained, reveal the newly displayed cards without changing the user’s scroll position
- With JavaScript disabled, all content must remain visible and usable

## 7. Interactive design

### Cursor-reactive product lighting

Apply a soft spotlight to the hero artwork and featured product panels on devices with a fine pointer. The light follows the pointer inside the artwork bounds and should feel like reflected studio lighting rather than a cursor effect.

- Build the light as a CSS radial gradient overlay using `--pointer-x` and `--pointer-y` custom properties
- Gradient size: approximately `320–480px`; peak opacity: `0.14–0.22`
- Blend with `screen` on dark artwork and `soft-light` on light artwork
- Ease the rendered light toward the pointer position instead of matching every raw event
- Fade the light in on pointer entry and out within `250ms` on pointer leave
- Clamp the light to the artwork container; it must not spill across text or navigation
- Do not translate, rotate, or distort the product image
- Update CSS variables through one `requestAnimationFrame` loop; do not create DOM elements during pointer movement
- Disable the effect for touch input, coarse pointers, reduced motion, and low-power fallback mode

### Expandable app cards

Each app card includes a `Quick view` control. Activating it expands the selected card in place so the user can explore the product without leaving the homepage.

Expanded content:

1. Two or three product screenshots
2. Three concise feature highlights
3. Platform and availability information
4. `View details` and `Download on the App Store` actions
5. A visible `Close` control

Behavior:

- Only one card may be expanded at a time
- Desktop: the card grows across the full grid row while surrounding cards reposition smoothly
- Tablet and mobile: the card behaves as an inline accordion and remains within the document flow
- Expansion uses a FLIP-style layout transition lasting `350–450ms` with `power3.inOut`
- Do not use a modal unless the content later requires a complex task
- The control is a button with `aria-expanded` and `aria-controls`; expanded content has a persistent unique ID
- On open, move focus to the expanded card heading only when the expansion was triggered by keyboard
- `Escape` closes the card and returns focus to its `Quick view` button
- After closing, restore the user’s previous scroll position as closely as possible
- If JavaScript is unavailable, `Quick view` becomes a normal link to the app detail page

### Reactive logo

The FACTORY 471 symbol responds subtly to pointer hover and keyboard focus. Its geometric pieces separate slightly and settle back into place, suggesting a product being assembled.

- Separate internal logo shapes by no more than `4–6px` and rotate them by no more than `3deg`
- Animate out in `220ms` and settle back with a soft spring over `420–520ms`
- Trigger once per pointer entry or focus event; never loop continuously
- Keep the logo’s overall bounding box and navigation layout fixed
- The logo remains a standard link to the homepage with an accessible name such as `FACTORY 471 home`
- Keyboard focus receives the same visual response as hover plus a visible focus ring
- Mobile receives one short assembly motion on initial page load only; do not replay it on every scroll
- Reduced-motion mode shows only a color or opacity change

## 8. Motion

- Page-load text reveal: opacity `0 → 1`, translateY `12px → 0`, `500ms`
- Card entrance: `60–120ms` stagger per card
- Hover transitions: `180ms ease-out`
- Scroll reveals should play once and should not flicker when the user moves around a trigger boundary
- Avoid parallax on mobile and disable non-essential animation when `prefers-reduced-motion: reduce`
- Do not run the cursor light, card layout animation, and large scroll reveal simultaneously in the same viewport; prioritize the user-triggered interaction

## 9. Responsive behavior

### Desktop

- Full global navigation
- Centered hero content
- Three-column app grid
- Scroll-triggered section and card reveals

### Tablet

- Reduce navigation spacing; collapse secondary items if necessary
- Two-column app grid with the same reveal sequence
- Expanded cards span both columns

### Mobile

- Menu sheet replaces desktop links
- Headline wraps to two or three short lines
- Artwork sits below copy rather than behind it when contrast is uncertain
- Single-column app grid
- Single-column cards reveal individually with reduced movement
- Cursor lighting is disabled; cards expand as inline accordions
- Logo response is limited to a single page-load assembly motion
- Footer directory becomes accordions

## 10. Accessibility and content rules

- Target WCAG 2.2 AA contrast
- Preserve logical heading order: one `h1`, section titles as `h2`, card titles as `h3`
- Use real buttons for UI actions and real links for navigation
- Provide descriptive alt text for meaningful product imagery; decorative imagery uses empty alt text
- Never place essential copy inside images
- Support keyboard navigation, `200%` zoom, and text reflow at `320px`
- Touch targets are at least `44 × 44px`
- Avoid generic labels such as “Click here”; use “Learn more about Snow Record” for accessible names
- Keep marketing sentences short: one product, one promise, one action
- Expanded cards must preserve a logical focus order and expose their open/closed state to assistive technology
- No information may depend exclusively on cursor position, hover, animation, or lighting

## 11. Footer

- Surface color: `#F5F5F7`
- Begin with footnotes and legal/product availability notes
- Follow with a multi-column directory for Apps, Support, Company, and Legal
- Desktop uses columns; mobile uses disclosure accordions
- Final row contains copyright, privacy policy, terms, and language/region

## 12. Implementation acceptance criteria

- The navigation becomes sticky and translucent without obscuring anchor targets
- The hero and featured campaigns remain readable across all breakpoints
- App cards render as 3/2/1 columns on desktop/tablet/mobile
- Scroll-triggered animations use transforms and opacity without affecting reading order or keyboard access
- Product lighting follows the pointer smoothly without covering copy or running on touch devices
- App cards open and close in place with correct focus restoration and `aria-expanded` state
- Logo response works on hover and keyboard focus without shifting the navigation layout
- Interactive elements have clear active, hover, focus, and disabled states
- Reduced-motion users receive no forced transitions
- No Apple logo, Apple product image, or proprietary marketing copy is reused
- Lighthouse accessibility score target: 95 or higher
