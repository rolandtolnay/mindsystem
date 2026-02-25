---
title: Isolate Feature Responsibility
category: structure
impact: HIGH
impactDescription: Features become removable
tags: wrapper, decorator, feature-isolation, composition
---

## Isolate Feature Responsibility

Extract optional feature logic into wrapper/decorator components. The wrapper owns all feature-specific state; the core component doesn't know the feature exists.

**Detection signals:**
- More than 30% of a component's code dedicated to one optional feature
- Removing a feature requires deleting scattered lines throughout the file
- Multiple `if (featureEnabled)` checks spread across the component
- State variables only used by one feature mixed with core state
- Feature-specific imports polluting the core module

**Why it matters:**
- Feature can be disabled/removed by removing one wrapper
- Core component remains focused and testable
- Feature logic is cohesive and isolated in one place
- Multiple features compose without polluting each other

**Senior pattern:** Move all feature-specific state, effects, and rendering into a wrapper/decorator component that wraps the core. The wrapper provides feature context to the core through a render prop, slot, or composition pattern. The core component has zero awareness of the feature — it renders its own concern and accepts optional enhancement points.

**Detection questions:**
- Is more than 30% of a component's code dedicated to one optional feature?
- Would removing a feature require deleting scattered lines throughout the file?
- Are there multiple `if (featureEnabled)` checks spread across the component?
- Does the component have state variables only used by one feature?
