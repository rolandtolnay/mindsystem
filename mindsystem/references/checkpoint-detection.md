<checkpoint_detection>
Lite reference for identifying checkpoint types during task breakdown. Full checkpoint templates and examples are in the ms-plan-writer subagent.

<checkpoint_types>

| Type | Use When | Frequency |
|------|----------|-----------|
| `checkpoint:human-verify` | Claude automated work, human confirms visual/functional correctness | 90% |
| `checkpoint:decision` | Human must choose between options affecting implementation | 9% |
| `checkpoint:human-action` | Truly unavoidable manual step with no CLI/API (rare) | 1% |

</checkpoint_types>

<detection_rules>

**Mark as `checkpoint:human-verify` when:**
- Visual UI checks needed (layout, styling, responsiveness)
- Interactive flows require human testing (click through wizard, test user flows)
- Functional verification beyond automated tests (feature works as expected)
- Audio/video playback, animation smoothness, accessibility

**Mark as `checkpoint:decision` when:**
- Technology selection (auth provider, database, library)
- Architecture choices (monorepo vs separate, API patterns)
- Design decisions (color scheme, layout approach)
- Feature prioritization between variants

**Mark as `checkpoint:human-action` when (rare):**
- Email verification links (account creation)
- SMS 2FA codes (phone verification)
- Manual account approvals
- Credit card 3D Secure flows
- OAuth app approvals requiring browser

</detection_rules>

<automation_first_principle>
**If it has CLI/API, Claude automates it. No exceptions.**

Never create `checkpoint:human-action` for:
- Deployments (use `vercel`, `railway`, `fly` CLI)
- Database operations (use provider CLI)
- Webhook setup (use APIs)
- Environment files (use Write tool)
- Running builds/tests (use Bash tool)

The rule: Claude does everything automatable. Checkpoints verify AFTER automation, not replace it.
</automation_first_principle>

</checkpoint_detection>
