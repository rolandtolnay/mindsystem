<verification_deep>

<core_principle>
**Existence ≠ Implementation**

A file existing does not mean the feature works. Verification must check:
1. **Exists** - File is present at expected path
2. **Substantive** - Content is real implementation, not placeholder
3. **Wired** - Connected to the rest of the system
4. **Functional** - Actually works when invoked

Levels 1-3 can be checked programmatically. Level 4 often requires human verification.
</core_principle>

<goal_backward_planning>
## Goal-Backward Planning

**Forward planning asks:** "What should we build?"
**Goal-backward planning asks:** "What must be TRUE for the goal to be achieved?"

### The Process

**Step 1: State the Goal**
Take the phase goal from ROADMAP.md. This is the outcome, not the work.

- "Working chat interface" (not "build chat components")
- "Users can authenticate" (not "implement auth system")

**Step 2: Derive Observable Truths**
Ask: "What must be TRUE for this goal to be achieved?"

List 3-7 truths from the USER's perspective:
- User can see existing messages
- User can type and send a message
- Messages persist across refresh

**Step 3: Derive Required Artifacts**
For each truth, ask: "What must EXIST for this to be true?"

- Message list component
- API route for messages
- Message model in database

**Step 4: Derive Required Wiring**
For each artifact, ask: "What must be CONNECTED for this artifact to function?"

- Component fetches from API (not hardcoded)
- API queries database (not mock data)
- Database has correct schema

**Step 5: Identify Key Links**
Ask: "Where is this most likely to break?"

Key links are critical connections that, if missing, cause cascading failures:
- Input onSubmit → API call
- API save → database
- Component → real data

### Output Format

```yaml
must_haves:
  truths:
    - "User can see existing messages"
    - "User can send a message"
    - "Messages persist across refresh"
  artifacts:
    - path: "src/components/Chat.tsx"
      provides: "Message list rendering"
    - path: "src/app/api/chat/route.ts"
      provides: "Message CRUD operations"
  key_links:
    - from: "Chat.tsx"
      to: "api/chat"
      via: "fetch in useEffect"
```
</goal_backward_planning>

<stub_detection>
## Stub Detection Patterns

### Universal Stub Patterns

**Comment-based stubs:**
```bash
grep -E "(TODO|FIXME|XXX|HACK|PLACEHOLDER)" "$file"
grep -E "implement|add later|coming soon|will be" "$file" -i
```

**Placeholder text:**
```bash
grep -E "placeholder|lorem ipsum|coming soon|under construction" "$file" -i
grep -E "\[.*\]|<.*>|\{.*\}" "$file"  # Template brackets left in
```

**Empty/trivial implementations:**
```bash
grep -E "return null|return undefined|return \{\}|return \[\]" "$file"
grep -E "console\.(log|warn|error).*only" "$file"  # Log-only functions
```

### React Component Stubs

```javascript
// RED FLAGS:
return <div>Component</div>
return <div>Placeholder</div>
return null
return <></>

// Empty handlers:
onClick={() => {}}
onChange={() => console.log('clicked')}
onSubmit={(e) => e.preventDefault()}  // Only prevents default
```

**Substantive check:**
```bash
# Uses props or state (not static)
grep -E "props\.|useState|useEffect|useContext|\{.*\}" "$component_path"

# API calls exist (for data-fetching components)
grep -E "fetch\(|axios\.|useSWR|useQuery" "$component_path"
```

### API Route Stubs

```typescript
// RED FLAGS:
export async function POST() {
  return Response.json({ message: "Not implemented" })
}

export async function GET() {
  return Response.json([])  // Empty array with no DB query
}

// Console log only:
export async function POST(req) {
  console.log(await req.json())
  return Response.json({ ok: true })
}
```

**Substantive check:**
```bash
# Has actual logic (more than 10-15 lines)
wc -l "$route_path"

# Interacts with data source
grep -E "prisma\.|db\.|mongoose\.|sql|query" "$route_path" -i

# Has error handling
grep -E "try|catch|throw|error|Error" "$route_path"
```

### Database Schema Stubs

```prisma
// RED FLAGS:
model User {
  id String @id
  // TODO: add fields
}

model Message {
  id        String @id
  content   String  // Only one real field
}
```

**Substantive check:**
```bash
# Has expected fields (not just id)
grep -A 20 "model $model_name" "$schema_path" | grep -E "^\s+\w+\s+\w+"

# Has appropriate field types (not all String)
grep -A 20 "model $model_name" "$schema_path" | grep -E "Int|DateTime|Boolean|Float"
```

### Hook/Utility Stubs

```typescript
// RED FLAGS:
export function useAuth() {
  return { user: null, login: () => {}, logout: () => {} }
}

// Hardcoded return:
export function useUser() {
  return { name: "Test User", email: "test@example.com" }
}
```
</stub_detection>

<wiring_verification>
## Wiring Verification Patterns

Wiring verification checks that components actually communicate. This is where most stubs hide.

### Pattern: Component → API

**Check:** Does the component actually call the API?

```bash
# Find the fetch/axios call
grep -E "fetch\(['\"].*$api_path|axios\.(get|post).*$api_path" "$component_path"

# Check the response is used
grep -E "await.*fetch|\.then\(|setData|setState" "$component_path"
```

**Red flags:**
```typescript
// Fetch exists but response ignored:
fetch('/api/messages')  // No await, no .then

// Fetch in comment:
// fetch('/api/messages').then(...)

// Fetch to wrong endpoint:
fetch('/api/message')  // Typo
```

### Pattern: API → Database

**Check:** Does the API route actually query the database?

```bash
# Find the database call
grep -E "prisma\.$model|db\.query|Model\.find" "$route_path"

# Verify it's awaited
grep -E "await.*prisma|await.*db\." "$route_path"

# Check result is returned
grep -E "return.*json.*data|res\.json.*result" "$route_path"
```

**Red flags:**
```typescript
// Query exists but result not returned:
await prisma.message.findMany()
return Response.json({ ok: true })  // Returns static

// Query not awaited:
const messages = prisma.message.findMany()  // Missing await
return Response.json(messages)  // Returns Promise
```

### Pattern: Form → Handler

**Check:** Does form submission actually do something?

```bash
# Find onSubmit handler
grep -E "onSubmit=\{|handleSubmit" "$component_path"

# Check handler has content
grep -A 10 "onSubmit.*=" "$component_path" | grep -E "fetch|axios|mutate|dispatch"
```

**Red flags:**
```typescript
// Handler only prevents default:
onSubmit={(e) => e.preventDefault()}

// Handler only logs:
const handleSubmit = (data) => {
  console.log(data)
}
```

### Pattern: State → Render

**Check:** Does the component render state, not hardcoded content?

```bash
# Find state usage in JSX
grep -E "\{.*messages.*\}|\{.*data.*\}" "$component_path"

# Check map/render of state
grep -E "\.map\(|\.filter\(" "$component_path"
```

**Red flags:**
```tsx
// Hardcoded instead of state:
return <div>
  <p>Message 1</p>
  <p>Message 2</p>
</div>

// State exists but not rendered:
const [messages, setMessages] = useState([])
return <div>No messages</div>  // Always shows this
```
</wiring_verification>

<verification_checklist>
## Quick Verification Checklists

### Component Checklist
- [ ] File exists at expected path
- [ ] Exports a function/const component
- [ ] Returns JSX (not null/empty)
- [ ] No placeholder text in render
- [ ] Uses props or state (not static)
- [ ] Event handlers have real implementations
- [ ] Imports resolve correctly
- [ ] Used somewhere in the app

### API Route Checklist
- [ ] File exists at expected path
- [ ] Exports HTTP method handlers
- [ ] Handlers have more than 5 lines
- [ ] Queries database or service
- [ ] Returns meaningful response
- [ ] Has error handling
- [ ] Validates input
- [ ] Called from frontend

### Schema Checklist
- [ ] Model/table defined
- [ ] Has all expected fields
- [ ] Fields have appropriate types
- [ ] Relationships defined if needed
- [ ] Migrations exist and applied
- [ ] Client generated

### Wiring Checklist
- [ ] Component → API: fetch call exists and uses response
- [ ] API → Database: query exists and result returned
- [ ] Form → Handler: onSubmit calls API/mutation
- [ ] State → Render: state variables appear in JSX
</verification_checklist>

<human_verification_triggers>
## When to Require Human Verification

Some things can't be verified programmatically. Flag these for human testing:

**Always human:**
- Visual appearance (does it look right?)
- User flow completion (can you actually do the thing?)
- Real-time behavior (WebSocket, SSE)
- External service integration (Stripe, email)
- Error message clarity
- Performance feel

**Human if uncertain:**
- Complex wiring that grep can't trace
- Dynamic behavior depending on state
- Edge cases and error states
- Mobile responsiveness
- Accessibility

**Format for human verification:**
```markdown
## Human Verification Required

### 1. Chat message sending
**Test:** Type a message and click Send
**Expected:** Message appears in list, input clears
**Check:** Does message persist after refresh?

### 2. Error handling
**Test:** Disconnect network, try to send
**Expected:** Error message appears, message not lost
**Check:** Can retry after reconnect?
```
</human_verification_triggers>

<verification_status_routing>
## Verification Status Routing

| Status | Meaning | Action |
|--------|---------|--------|
| `passed` | All must-haves verified | Update roadmap, continue |
| `human_needed` | Automated passed, needs human | Present test scenarios |
| `gaps_found` | Missing functionality | Offer `/ms:plan-phase --gaps` |

**gaps_found flow:**
1. Verifier creates VERIFICATION.md with gaps
2. User runs `/ms:plan-phase {X} --gaps`
3. Planner reads gaps, creates fix plans
4. User runs `/ms:execute-phase {X}` again
5. Execute runs new plans
6. Verifier runs again
7. Repeat until passed
</verification_status_routing>

<common_failures>
## Common Verification Failures

**Truths too vague:**
- Bad: "User can use chat"
- Good: "User can see messages", "User can send message"

**Artifacts too abstract:**
- Bad: "Chat system", "Auth module"
- Good: "src/components/Chat.tsx", "src/app/api/auth/login/route.ts"

**Missing wiring:**
- Bad: Listing components without how they connect
- Good: "Chat.tsx fetches from /api/chat via useEffect on mount"

**Skipping key links:**
- Bad: Assuming "if files exist, it works"
- Good: Identifying 2-3 critical connections that make-or-break
</common_failures>

</verification_deep>
