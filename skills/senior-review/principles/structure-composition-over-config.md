---
title: Composition Over Configuration
category: structure
impact: MEDIUM
impactDescription: Simplifies component APIs
tags: composition, god-component, flags, single-responsibility
---

## Composition Over Configuration

Build focused components that compose together instead of god components with many boolean flags.

**Detection signals:**
- Component has more than 6-8 parameters/props
- Boolean parameters that are mutually exclusive
- Component is really 3 different components pretending to be 1
- Adding a new variant would require another boolean flag
- Conditionals inside the component that render entirely different structures

**Why it matters:**
- Each component has one job and is easy to understand
- New variants don't bloat existing components
- Easier to test: focused inputs and outputs
- Flexible: compose for custom needs, use shortcuts for common ones

**Senior pattern:** Split the god component into focused units, each handling one variant or concern. Provide composition points (children/slots/render props) for flexibility. For common combinations, offer convenience wrappers that compose the focused units — but the building blocks remain available for custom needs.

**Detection questions:**
- Does this component have more than 6-8 parameters?
- Are there boolean parameters that are mutually exclusive?
- Is this component really multiple components pretending to be one?
- Would adding a new variant require another boolean flag?
