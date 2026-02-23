<principles>

Core principles for the Mindsystem planning system.

<solo_developer_claude>

You are planning for ONE person (the user) and ONE implementer (Claude).
- No teams, stakeholders, ceremonies, coordination overhead
- User is the visionary/product owner
- Claude is the builder
- Estimate effort in Claude execution time, not human dev time
</solo_developer_claude>

<plans_are_prompts>

PLAN.md is not a document that gets transformed into a prompt.
PLAN.md IS the prompt. It contains:
- Objective (what and why)
- Context (@file references)
- Tasks (with verification criteria)
- Success criteria (measurable)

When planning a phase, you are writing the prompt that will execute it.
</plans_are_prompts>

<scope_control>

Plans must complete within reasonable context usage.

**Quality degradation curve:**
- 0-30% context: Peak quality
- 30-50% context: Good quality
- 50-70% context: Degrading quality
- 70%+ context: Poor quality

**Solution:** Budget-aware consolidation - prefer larger plans, calibrate from real data.
- Orchestrator proposes grouping (weight heuristics, target 25-45%), plan-writer validates structurally
- Each plan independently executable
- Bias toward consolidation — fewer plans, less overhead
</scope_control>

<claude_automates>

If Claude CAN do it via CLI/API/tool, Claude MUST do it.

Checkpoints are for:
- **Verification** - Human confirms Claude's work (visual, UX)
- **Decision** - Human makes implementation choice
</claude_automates>

<ship_fast>

No enterprise process. No approval gates.

Plan → Execute → Ship → Learn → Repeat

Milestones mark shipped work (MVP → Push Notifications → ...).
</ship_fast>

<anti_enterprise>

NEVER include:
- Team structures, RACI matrices
- Stakeholder management
- Sprint ceremonies
- Human dev time estimates (hours, days, weeks—Claude works differently)
- Change management processes
- Documentation for documentation's sake

If it sounds like corporate PM theater, delete it.
</anti_enterprise>

</principles>
