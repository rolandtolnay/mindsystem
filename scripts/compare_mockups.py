#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Combine variant-*.html mockup files into a single side-by-side comparison page."""

import re
import sys
from pathlib import Path


def extract_title(html: str) -> str:
    """Extract the content of the <title> tag from an HTML string."""
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
    return match.group(1) if match else "Untitled"


def is_device_mockup(html: str) -> bool:
    """Detect if the HTML is a phone-frame mockup (has a fixed-size .device element)."""
    return bool(re.search(r"\.device\s*\{", html))


def build_device_html(panels: list[tuple[str, str]]) -> str:
    """Side-by-side layout for phone-frame mockups."""
    panels_html = ""
    for label, filename in panels:
        panels_html += f"""
      <div class="panel">
        <h2>{label}</h2>
        <iframe src="{filename}"></iframe>
      </div>"""

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mockup Comparison</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1a1a1a;
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    padding: 24px;
  }}
  h1 {{
    text-align: center;
    margin-bottom: 24px;
    font-size: 24px;
    font-weight: 600;
  }}
  .container {{
    display: flex;
    justify-content: center;
    gap: 32px;
    flex-wrap: wrap;
  }}
  .panel {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }}
  .panel h2 {{
    font-size: 16px;
    font-weight: 500;
    color: #ccc;
  }}
  iframe {{
    border: none;
    border-radius: 8px;
    background: #e5e5e5;
    width: 450px;
    height: 920px;
  }}
</style>
</head>
<body>
  <h1>Mockup Comparison</h1>
  <div class="container">{panels_html}
  </div>
</body>
</html>
"""


def build_fluid_html(panels: list[tuple[str, str]]) -> str:
    """Tabbed layout for full web page mockups."""
    tabs_html = ""
    panes_html = ""
    for i, (label, filename) in enumerate(panels):
        active = " active" if i == 0 else ""
        tabs_html += f"""
        <button class="tab{active}" data-index="{i}">{label}</button>"""
        panes_html += f"""
      <iframe class="pane{active}" data-index="{i}" src="{filename}"></iframe>"""

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mockup Comparison</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ height: 100%; }}
  body {{
    background: #1a1a1a;
    color: #fff;
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    display: flex;
    flex-direction: column;
  }}
  .tab-bar {{
    display: flex;
    gap: 4px;
    padding: 16px 24px 0;
    flex-shrink: 0;
  }}
  .tab {{
    padding: 10px 24px;
    border: none;
    border-radius: 8px 8px 0 0;
    background: #2a2a2a;
    color: #888;
    font-size: 14px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }}
  .tab:hover {{
    background: #333;
    color: #bbb;
  }}
  .tab.active {{
    background: #e5e5e5;
    color: #111;
  }}
  .pane-container {{
    flex: 1;
    padding: 0 24px 24px;
    min-height: 0;
  }}
  .pane {{
    display: none;
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 0 8px 8px 8px;
    background: #e5e5e5;
  }}
  .pane.active {{
    display: block;
  }}
</style>
</head>
<body>
  <div class="tab-bar">{tabs_html}
  </div>
  <div class="pane-container">{panes_html}
  </div>
  <script>
    document.querySelectorAll('.tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        const idx = tab.dataset.index;
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.pane').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.querySelector('.pane[data-index="' + idx + '"]').classList.add('active');
      }});
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    if len(sys.argv) > 1:
        mockups_dir = Path(sys.argv[1])
    else:
        mockups_dir = Path.cwd()

    variants = sorted(mockups_dir.glob("variant-*.html"))
    if not variants:
        print(f"No variant-*.html files found in {mockups_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(variants)} variants: {', '.join(v.name for v in variants)}")

    # Read variants and detect layout mode
    panels: list[tuple[str, str]] = []
    all_device = True
    for path in variants:
        html = path.read_text()
        letter = path.stem.split("-")[-1].upper()
        title = extract_title(html)
        label = f"Variant {letter}: {title}"
        if not is_device_mockup(html):
            all_device = False
        panels.append((label, path.name))

    mode = "device" if all_device else "fluid"
    print(f"Layout mode: {mode}")

    if mode == "device":
        comparison = build_device_html(panels)
    else:
        comparison = build_fluid_html(panels)

    output = mockups_dir / "comparison.html"
    output.write_text(comparison)
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
