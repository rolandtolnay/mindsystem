---
title: API Boundary Design
category: dependencies
impact: HIGH
impactDescription: Prevents invalid data from propagating
tags: api-contracts, validation, boundaries, request-response
---

## API Boundary Design

Define typed request/response contracts with validation at system boundaries. Trust internal code; verify external input.

**Detection signals:**
- API handlers that accept `any` or untyped request bodies
- Validation logic scattered across business logic instead of at the boundary
- No shared type between client and server for the same endpoint
- Error responses that leak internal details (stack traces, database errors)
- Different endpoints handling the same entity with inconsistent field names

**Why it matters:**
- Invalid data is caught at the boundary before it reaches business logic
- Internal code operates on validated, typed data — no defensive checks everywhere
- Client and server stay in sync through shared types or generated contracts
- Error responses are consistent and safe for consumers

**Senior pattern:** Validate and parse at the boundary: incoming data is unknown until validated, then flows as typed objects through internal layers. Define request/response types explicitly (schema validation, codegen, or shared type packages). Internal functions receive validated types and trust them — they don't re-validate. Error responses follow a consistent shape with safe, user-facing messages.

**Detection questions:**
- Do API handlers accept untyped or `any` request bodies?
- Is validation scattered across business logic instead of concentrated at boundaries?
- Is there a shared type contract between client and server?
- Do error responses leak internal details like stack traces?
