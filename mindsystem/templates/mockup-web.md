# Web Mockup Template

Template for generating self-contained HTML/CSS mockups for web interfaces.

**Purpose:** Provide a minimal, clean scaffold so mockup designers can focus on layout and component design. Includes CSS reset, system font stack, and basic utility classes. No device frame — renders at full viewport.

---

<template>
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{DIRECTION_NAME}} — {{SCREEN_NAME}}</title>
<style>
  /* === RESET === */
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, Roboto, "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    line-height: 1.5;
    color: #111827;
    background: #ffffff;
  }

  /* === CONTAINER === */
  .container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
  }

  .container-narrow {
    max-width: 768px;
    margin: 0 auto;
    padding: 0 24px;
  }

  /* === LAYOUT UTILITIES === */
  .flex { display: flex; }
  .flex-col { display: flex; flex-direction: column; }
  .flex-center { display: flex; align-items: center; justify-content: center; }
  .flex-between { display: flex; align-items: center; justify-content: space-between; }
  .flex-1 { flex: 1; }
  .flex-wrap { flex-wrap: wrap; }

  .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); }

  /* === SPACING === */
  .gap-xs { gap: 4px; }
  .gap-sm { gap: 8px; }
  .gap-md { gap: 16px; }
  .gap-lg { gap: 24px; }
  .gap-xl { gap: 32px; }
  .gap-2xl { gap: 48px; }

  .p-sm { padding: 8px; }
  .p-md { padding: 16px; }
  .p-lg { padding: 24px; }

  .py-sm { padding-top: 8px; padding-bottom: 8px; }
  .py-md { padding-top: 16px; padding-bottom: 16px; }
  .py-lg { padding-top: 24px; padding-bottom: 24px; }
  .py-xl { padding-top: 48px; padding-bottom: 48px; }

  /* === TYPOGRAPHY === */
  h1 { font-size: 36px; font-weight: 700; line-height: 1.2; letter-spacing: -0.02em; }
  h2 { font-size: 24px; font-weight: 600; line-height: 1.3; }
  h3 { font-size: 20px; font-weight: 600; line-height: 1.4; }
  h4 { font-size: 16px; font-weight: 600; line-height: 1.5; }
  .text-sm { font-size: 14px; }
  .text-xs { font-size: 12px; }
  .text-muted { color: #6b7280; }

  /* ================================================================
     AGENT: Add your custom CSS below this line.
     Utility classes above are optional — use or override as needed.
     Custom CSS is encouraged for layout, colors, and components.
     ================================================================ */

</style>
</head>
<body>

  <!-- ============================================================
       AGENT: Build your layout below.
       Use .container for max-width centered content.
       Use .container-narrow for forms/text-heavy pages.
       Full-width sections can skip the container.
       ============================================================ -->



</body>
</html>
```
</template>

<agent_instructions>
**What to modify:**
- Build layout inside `<body>` using `.container` or custom structure
- Add custom CSS below the marked comment line
- Override any utility class as needed

**What NOT to modify:**
- CSS reset block
- Font stack declaration (unless design direction specifies different fonts)

**Layout guidance:**
- `.container` (1280px) for dashboards, wide layouts
- `.container-narrow` (768px) for forms, articles, settings
- Full-width sections: skip container, use direct body children
- Utility classes are helpers — custom CSS is expected and encouraged

**Sizing guidance:**
- Click targets: 32x32px minimum
- Body text: 16px minimum
- Keep total HTML under 500 lines
- No JavaScript, no external CDN resources, no images (use CSS shapes/unicode/inline SVG)
</agent_instructions>
