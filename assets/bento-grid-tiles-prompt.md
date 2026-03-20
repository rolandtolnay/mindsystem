# Nano Banana 2 — Mindsystem Bento Grid (Tile-by-Tile)

Generate each tile individually, then composite into a final bento grid.

**Reference images:** Attach 1-2 Apple WWDC Bento screenshots with every tile prompt for consistent styling.

**Shared style directive (prepend to every tile prompt):**

> In the style of the attached Apple WWDC feature bento grid tiles: white card with soft rounded corners, light gray (#F5F5F7) background visible as padding around the card, bold sans-serif font (SF Pro Display Bold style) for headings, medium weight for description text, generous white space inside the card. Clean, flat, minimal. No gradients on the card itself unless specified. No photorealism.

---

## Tile 1 — Hero (Mindsystem)

**Aspect ratio:** 16:9 | **Resolution:** 4K

A wide rectangular card with a smooth gradient background flowing from deep indigo on the left through royal blue to soft teal on the right. In the center, the word "Mindsystem" in large, bold, semi-translucent white sans-serif text. Below it in smaller white text: "Full-cycle development system for Claude Code". Nothing else — no icons, no imagery. Just elegant typography floating on the gradient. Match the exact style of the "iOS", "macOS", "tvOS" hero tiles from the attached Apple WWDC references.

---

## Tile 2 — Knowledge Compounding (large)

**Aspect ratio:** 1:1 | **Resolution:** 2K

White card. At the top, the heading "Knowledge Compounding" in bold dark sans-serif text. Centered below, a minimal flat illustration: three translucent document shapes stacked vertically, each slightly offset upward and to the right, getting progressively more opaque and more blue — the bottom one barely visible in light gray, the middle one in soft blue, the top one in vivid indigo. Represents knowledge layers accumulating over time. Below the illustration in smaller gray text: "Phase 1 starts from scratch. Phase 10 starts with everything." Plenty of white space around everything.

---

## Tile 3 — Full Lifecycle (wide)

**Aspect ratio:** 2:1 | **Resolution:** 2K

White card. Heading "Full Lifecycle" in bold dark sans-serif at the top. Below, a horizontal pipeline of 6 small circles connected by a thin gray line. Each circle contains a simple single-color icon in muted blue: lightbulb, magnifying glass, palette, document page, play triangle, checkmark. Below the pipeline in small gray text, the labels: "discover → research → design → plan → execute → verify". Clean, airy, lots of breathing room between elements.

---

## Tile 4 — Parallel Research

**Aspect ratio:** 4:3 | **Resolution:** 2K

White card. Heading "Parallel Research" in bold dark sans-serif at the top. Centered illustration: three horizontal arrows in blue, indigo, and teal, running parallel from left to right, converging into a single point on the right side — like three streams merging. Simple flat vector, no outlines. Below in smaller gray text: "3 agents. Docs, codebase, community — simultaneously."

---

## Tile 5 — Context Engineering

**Aspect ratio:** 4:3 | **Resolution:** 2K

White card. Heading "Context Engineering" in bold dark sans-serif at the top. Centered illustration: a minimal semicircular gauge meter. The left portion of the arc is blue (the safe zone), the right portion fades to light red (the danger zone). A thin needle points firmly into the blue zone. Simple, flat, no detail. Below in smaller gray text: "Fresh 200k context per plan."

---

## Tile 6 — Design Mockups

**Aspect ratio:** 4:3 | **Resolution:** 2K

White card. Heading "Design Mockups" in bold dark sans-serif at the top. Centered illustration: two simplified browser window outlines overlapping slightly, offset like two playing cards fanned out. Thin blue line art, no fill. A small "A" label on one and "B" on the other. Below in smaller gray text: "Parallel variants with side-by-side comparison."

---

## Tile 7 — Browser Verification

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Browser Verification" in bold dark sans-serif at the top. Centered: a simplified browser window outline (rounded rectangle with three dots in the top-left corner) with a blue circular checkmark badge overlaid on the bottom-right corner. Flat single-color line art. Below in smaller gray text: "Screenshots. Console diagnostics."

---

## Tile 8 — Code Review

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Code Review" in bold dark sans-serif at the top. Centered: a simplified document icon showing a few horizontal lines (representing code) with a small magnifying glass overlaid on the corner. Flat indigo color. Below in smaller gray text: "Structural and clarity passes."

---

## Tile 9 — Codebase Mapping

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Codebase Mapping" in bold dark sans-serif at the top. Centered: four small circles connected by thin lines forming a simple network graph — one central node with three branches. Flat blue. Below in smaller gray text: "4 agents → 7 documents."

---

## Tile 10 — Dream Extraction

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Dream Extraction" in bold dark sans-serif at the top. Centered: a lightbulb shape with a small speech bubble emerging from it, both in flat warm blue. Represents ideas being drawn out through conversation. Below in smaller gray text: "Your product owner for requirements."

---

## Tile 11 — Verify Work (small)

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Verify Work" in bold dark sans-serif. Centered: a shield icon with a checkmark inside, in flat blue. Below in smaller gray text: "Your QA pipeline." Minimal, compact.

---

## Tile 12 — Adhoc Execution (small)

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Adhoc Execution" in bold dark sans-serif. Centered: a lightning bolt icon in flat indigo. Below in smaller gray text: "Full pipeline, one context." Minimal, compact.

---

## Tile 13 — Structured Debugging (small)

**Aspect ratio:** 1:1 | **Resolution:** 1K

White card. Heading "Structured Debugging" in bold dark sans-serif. Centered: a bug icon with a small magnifying glass, in flat teal. Below in smaller gray text: "Persists across /clear." Minimal, compact.

---

## Final Composition

**Aspect ratio:** 16:9 | **Resolution:** 4K | **Thinking:** ON

Once all tiles are generated, use this prompt with all 13 tile images attached:

> Arrange the attached 13 card images into a single 16:9 bento grid layout matching the composition style of Apple WWDC feature overview slides. Place the gradient "Mindsystem" hero tile in the center. Arrange the remaining cards around it in an asymmetric grid with varied tile sizes — some cards should be large, some medium, some small. Use a solid light gray (#F5F5F7) background with narrow gaps between cards. The final result should look like a polished Apple keynote slide. Do not modify the individual cards — only arrange and resize them.

---

## Tips

- Generate 2-3 variations of each tile and pick the cleanest one before moving to composition
- If a tile's text is mangled, regenerate just that tile — you only lose one piece, not the whole grid
- If the final composition distorts the tiles, try in Figma instead: place tiles manually on a #F5F5F7 canvas with 12-16px gaps and 16px corner radius
- The individual tiles also work standalone — e.g., as feature cards in docs or social posts
