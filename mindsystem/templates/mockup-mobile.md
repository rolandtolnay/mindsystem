# Mobile Mockup Template

Template for generating self-contained HTML/CSS mockups in an iPhone 15 device frame.

**Purpose:** Provide a realistic mobile device frame so mockup designers can focus on content area design without worrying about device chrome. The frame includes status bar, safe areas, and home indicator — agents fill only the content area.

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
  /* === PAGE BACKGROUND === */
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #e5e5e5;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }

  /* === DEVICE FRAME === */
  .device {
    width: 393px;
    height: 852px;
    background: #000;
    border-radius: 47px;
    padding: 12px;
    position: relative;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3), inset 0 0 0 2px #333;
  }

  .device-screen {
    width: 100%;
    height: 100%;
    background: #fff;
    border-radius: 39px;
    overflow: hidden;
    position: relative;
    display: flex;
    flex-direction: column;
  }

  /* === DYNAMIC ISLAND === */
  .dynamic-island {
    position: absolute;
    top: 11px;
    left: 50%;
    transform: translateX(-50%);
    width: 126px;
    height: 37px;
    background: #000;
    border-radius: 20px;
    z-index: 10;
  }

  /* === STATUS BAR === */
  .status-bar {
    height: 59px;
    padding: 17px 24px 0;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-shrink: 0;
    position: relative;
    z-index: 5;
  }
  .status-bar .time {
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.2px;
  }
  .status-bar .icons {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 500;
  }
  .status-bar .icons .signal {
    display: flex;
    gap: 1.5px;
    align-items: flex-end;
  }
  .status-bar .icons .signal span {
    display: block;
    width: 3px;
    background: currentColor;
    border-radius: 1px;
  }
  .status-bar .icons .signal span:nth-child(1) { height: 4px; }
  .status-bar .icons .signal span:nth-child(2) { height: 7px; }
  .status-bar .icons .signal span:nth-child(3) { height: 10px; }
  .status-bar .icons .signal span:nth-child(4) { height: 13px; }
  .status-bar .icons .wifi { font-size: 15px; }
  .status-bar .icons .battery {
    width: 27px;
    height: 13px;
    border: 1.5px solid currentColor;
    border-radius: 3px;
    position: relative;
    display: flex;
    align-items: center;
    padding: 2px;
  }
  .status-bar .icons .battery::after {
    content: '';
    position: absolute;
    right: -4px;
    width: 2px;
    height: 6px;
    background: currentColor;
    border-radius: 0 1px 1px 0;
  }
  .status-bar .icons .battery .fill {
    width: 75%;
    height: 100%;
    background: currentColor;
    border-radius: 1px;
  }

  /* === CONTENT AREA === */
  .content {
    flex: 1;
    overflow-y: auto;
    position: relative;
    /* Agent fills this area */
  }

  /* === BOTTOM NAV (optional — agent can replace or remove) === */
  .bottom-nav {
    height: 83px;
    padding: 8px 0 34px;
    display: flex;
    justify-content: space-around;
    align-items: flex-start;
    border-top: 0.5px solid #e0e0e0;
    flex-shrink: 0;
    background: inherit;
  }
  .bottom-nav .tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    font-size: 10px;
    color: #999;
    text-decoration: none;
  }
  .bottom-nav .tab.active { color: #007AFF; }
  .bottom-nav .tab .icon { font-size: 24px; line-height: 1; }

  /* === HOME INDICATOR === */
  .home-indicator {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 134px;
    height: 5px;
    background: #000;
    border-radius: 3px;
    opacity: 0.2;
    z-index: 10;
  }

  /* ================================================================
     AGENT: Add your custom CSS below this line.
     Do NOT modify the device frame, status bar, or home indicator.
     Style the .content area and .bottom-nav (or replace bottom-nav).
     ================================================================ */

</style>
</head>
<body>
<div class="device">
  <div class="device-screen">
    <div class="dynamic-island"></div>

    <!-- Status Bar -->
    <div class="status-bar">
      <span class="time">9:41</span>
      <div class="icons">
        <div class="signal">
          <span></span><span></span><span></span><span></span>
        </div>
        <span class="wifi">&#9679;</span>
        <div class="battery"><div class="fill"></div></div>
      </div>
    </div>

    <!-- ============================================================
         AGENT: Replace or fill the content below.
         Keep your content inside .content div.
         You may replace .bottom-nav with your own navigation.
         ============================================================ -->

    <div class="content">
      <!-- YOUR CONTENT HERE -->
    </div>

    <nav class="bottom-nav">
      <a class="tab active">
        <span class="icon">&#9679;</span>
        <span>Tab 1</span>
      </a>
      <a class="tab">
        <span class="icon">&#9679;</span>
        <span>Tab 2</span>
      </a>
      <a class="tab">
        <span class="icon">&#9679;</span>
        <span>Tab 3</span>
      </a>
      <a class="tab">
        <span class="icon">&#9679;</span>
        <span>Tab 4</span>
      </a>
    </nav>

    <div class="home-indicator"></div>
  </div>
</div>
</body>
</html>
```
</template>

<agent_instructions>
**What to modify:**
- Fill the `.content` div with your screen design
- Replace `.bottom-nav` with appropriate navigation (or remove if not needed)
- Add custom CSS below the marked comment line

**What NOT to modify:**
- Device frame (`.device`, `.device-screen`)
- Dynamic island (`.dynamic-island`)
- Status bar (`.status-bar` and children)
- Home indicator (`.home-indicator`)
- Page background (`body` styles)

**Content area dimensions:**
- Width: 369px (393 - 12px bezel on each side)
- Available height: ~710px (852 - 59px status bar - 83px bottom nav, minus bezel)
- If no bottom nav: ~793px available

**Status bar color:**
- Default text color is inherited — set color on `.status-bar` to match your background
- Dark background → use `color: #fff` on `.status-bar`
- Light background → use `color: #000` on `.status-bar`

**Sizing guidance:**
- Touch targets: 44pt minimum (44px in this frame)
- Body text: 17px (iOS default)
- Navigation bar height: 44px
- Standard horizontal padding: 16px
- Keep total HTML under 500 lines
</agent_instructions>
