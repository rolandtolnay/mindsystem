---
description: Extract backend patterns from current project into reusable CDN-ready module
allowed-tools: Task(Explore), AskUserQuestion, Glob, Read, Write, Bash, Skill(taches-cc-resources:create-agent-skills)
---

<objective>
Extract reusable backend patterns from the current Flutter project into CDN-ready modules.
Analyzes the codebase for API infrastructure, error handling, and DTOs, then generates
generalized, documented modules in `.claude/extraction/backends/`.
</objective>

<command_workflow>

# Phase 1: Intake

<critical>
BEFORE doing anything else, use AskUserQuestion to present this menu to the user.
Do NOT proceed to analysis until user responds.
</critical>

<intake_question>
Present using AskUserQuestion with these options:

Question: "What would you like to extract from this project?"
Header: "Scope"
Options:
1. "Full backend module" - API client + patterns + error handling + DTOs
2. "Specific components" - Choose which parts to include
3. "Review existing extraction" - Continue from previous session

If user selects "Specific components", follow up asking which categories:
- API Infrastructure (HTTP client, API classes, composition)
- Error Handling (exceptions, mapping, recovery)
- DTO/Entity (serialization, parsing, validation)
</intake_question>

---

# Phase 2: Analysis (Parallel Explore Agents)

<parallel_analysis>
Launch 3 Explore agents IN A SINGLE MESSAGE for true parallel execution.
Each agent analyzes one category and returns structured JSON findings.

<critical>
You MUST send ONE message containing THREE Task tool calls to achieve parallel execution.
Do NOT launch agents sequentially - this defeats the purpose of parallel analysis.
</critical>

<agent_1 name="API Infrastructure Analyzer">
```
Task(
  description: "Analyze API infrastructure patterns",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for API infrastructure patterns. Be very thorough.

SEARCH LOCATIONS:
- Look for Dio setup, http package configuration in: **/http*.dart, **/api_client*.dart, **/dio*.dart
- Check **/core/network/**, **/data/remote/**, **/config/** for base URL definitions
- Find API classes with Repository, Service, Api suffixes in: **/data/repositories/**, **/api/**, **/services/**
- Find composition patterns in: **/core/contracts/**, **/domain/repositories/**

FOCUS AREAS:
1. HTTP Client: Library (Dio/http/retrofit), base config, interceptors, timeout, retry logic
2. API Classes: Organization pattern (repository/service/api), method signatures, pagination, caching
3. Composition: Abstract interfaces, mixins, DI patterns (Riverpod/GetIt/Provider)

OUTPUT FORMAT (JSON):
{
  \"http_client\": {
    \"library\": \"dio|http|retrofit|custom\",
    \"patterns\": [{\"name\": \"...\", \"description\": \"...\", \"location\": \"...\", \"code_snippet\": \"GENERALIZED with {Entity}, {basePath} placeholders\", \"rationale\": \"...\"}]
  },
  \"api_classes\": {
    \"organization\": \"repository|service|api|mixed\",
    \"patterns\": [{\"name\": \"...\", \"description\": \"...\", \"location\": \"...\", \"code_snippet\": \"GENERALIZED\", \"rationale\": \"...\"}]
  },
  \"composition\": {
    \"patterns\": [{\"name\": \"...\", \"type\": \"abstract_class|mixin|interface\", \"description\": \"...\", \"location\": \"...\", \"code_snippet\": \"GENERALIZED\", \"rationale\": \"...\"}]
  },
  \"dependencies\": [\"package:dio/dio.dart\", ...],
  \"recommendations\": \"summary of what to include\"
}

GENERALIZATION RULES:
- Replace entity names with {Entity} (PascalCase) or {entity} (camelCase)
- Replace API endpoints with {basePath}/{entities}
- Replace app-specific prefixes with {App}
- Keep library names (dio, riverpod) as-is
- Keep standard method names (fromJson, toJson) as-is"
)
```
</agent_1>

<agent_2 name="DTO/Entity Analyzer">
```
Task(
  description: "Analyze DTO/entity patterns",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for DTO and entity patterns. Be very thorough.

SEARCH LOCATIONS:
- Files: **/*_model.dart, **/*_dto.dart, **/*_entity.dart
- Directories: **/models/**, **/entities/**, **/data/models/**
- Look for classes with fromJson/toJson methods
- Check for freezed/json_serializable annotations

FOCUS AREAS:
1. Serialization Approach: json_serializable, freezed, manual, or mixed
2. fromJson/toJson: Factory constructors vs static methods, null safety
3. Nullable Handling: Required vs optional, default values
4. Nested Objects: List/Map parsing, recursive deserialization
5. Date/Time: ISO 8601, Unix timestamps, timezone handling
6. Enums: String-to-enum, unknown value handling, defaults
7. Validation: Constructor assertions, validation methods

OUTPUT FORMAT (JSON):
{
  \"serialization_approach\": \"json_serializable|freezed|manual|mixed\",
  \"patterns\": [
    {
      \"name\": \"pattern name\",
      \"description\": \"what it does\",
      \"location\": \"file path\",
      \"code_snippet\": \"GENERALIZED with {Entity}, {field} placeholders\",
      \"rationale\": \"why this pattern\"
    }
  ],
  \"dependencies\": [\"package:freezed_annotation/freezed_annotation.dart\", ...],
  \"recommendations\": \"what to include in module\"
}

GENERALIZATION RULES:
- Replace class names with {Entity}
- Replace field names with {field} where pattern matters
- Keep serialization annotations as-is
- Show nullable handling, date parsing, enum patterns"
)
```
</agent_2>

<agent_3 name="Error Handling Analyzer">
```
Task(
  description: "Analyze error handling patterns",
  subagent_type: "Explore",
  prompt: "Analyze this Flutter codebase for error handling patterns. Be very thorough.

SEARCH LOCATIONS:
- Files: **/*exception*.dart, **/*error*.dart, **/*failure*.dart
- Directories: **/core/error/**, **/utils/error/**
- Search for: try/catch patterns, throw statements, sealed class Exception
- Look in interceptors for error handling logic

FOCUS AREAS:
1. Error Types: Custom exception classes, sealed classes, error enums
2. Error Mapping: HTTP status code to domain error, server response parsing
3. Try/Catch: Catch specificity, propagation vs handling, rethrow patterns
4. Recovery: Automatic retry, fallback values, offline fallback
5. Logging: Debug vs production logging, crash reporting
6. User-Facing: Error message formatting, localized messages

OUTPUT FORMAT (JSON):
{
  \"error_types\": [\"NetworkException\", \"ServerException\", ...],
  \"patterns\": [
    {
      \"name\": \"pattern name\",
      \"description\": \"what it does\",
      \"location\": \"file path\",
      \"code_snippet\": \"GENERALIZED with {App}, {Service}, {errorMessage} placeholders\",
      \"rationale\": \"why this pattern\"
    }
  ],
  \"dependencies\": [\"package:dio/dio.dart\", ...],
  \"recommendations\": \"what to include in module\"
}

GENERALIZATION RULES:
- Replace app-specific exception names with {App}Exception
- Replace error messages with {errorMessage}
- Replace service names with {Service}
- Keep exception hierarchy structure"
)
```
</agent_3>

Wait for all 3 agents to complete before proceeding to Phase 3.
</parallel_analysis>

---

# Phase 3: Synthesize and Review

<synthesis>
After all agents complete, combine their findings into a unified analysis:

1. **Parse Agent Outputs**: Extract JSON from each agent's response
2. **Merge Findings**: Combine into single analysis object
3. **Identify Inconsistencies**: Note conflicting patterns or missing pieces
4. **Save Analysis**: Write to `.claude/extraction/analysis.json` using Write tool
</synthesis>

<present_findings>
Present findings to user in this format:

---

**API Infrastructure**

Found: [library] with [key features]
Location: [primary files]

HTTP Client Patterns:
- [Pattern with description]

API Class Patterns:
- [Pattern with description]

Composition Patterns:
- [Pattern with description]

Recommendation: [Include/Exclude] - [reasoning]

---

**DTO/Entity**

Found: [serialization approach]
Location: [primary files]

Patterns detected:
- [Pattern 1 with brief description]
- [Pattern 2 with brief description]

Recommendation: [Include/Exclude] - [reasoning]

---

**Error Handling**

Found: [error types summary]
Location: [primary files]

Patterns detected:
- [Pattern 1 with brief description]
- [Pattern 2 with brief description]

Recommendation: [Include/Exclude] - [reasoning]

---
</present_findings>

<confirm_inconsistencies>
If any inconsistencies or gaps were found during analysis, present them to the user:

"I found some areas that may need clarification:
- [Inconsistency 1: e.g., 'Mixed serialization approaches - both freezed and manual']
- [Gap 1: e.g., 'No error recovery patterns found']

Would you like me to:
1. Proceed with current findings
2. Investigate further with additional analysis"

Use AskUserQuestion to gather their decision.
</confirm_inconsistencies>

<additional_research>
If user requests further research on specific areas:

Use AskUserQuestion to ask:
"Which areas need deeper investigation?"
Options:
- HTTP client configuration details
- API method patterns and pagination
- Error recovery and retry logic
- DTO validation patterns
- Other (specify)

For each selected area, use the Task tool to launch an additional Explore agent with focused prompt:
```
Task(
  description: "Deep dive on [area]",
  subagent_type: "Explore",
  prompt: "Investigate [specific area] in more detail. Look for: [specific patterns]. Return additional patterns found in same JSON format."
)
```

Use the Write tool to merge new findings into the existing analysis.json file.
</additional_research>

---

# Phase 4: Gather User Decisions

<critical>
Use AskUserQuestion to confirm user decisions. Do NOT assume or auto-select.
</critical>

<decision_questions>
Use AskUserQuestion with multiSelect where appropriate:

Question 1: "Which components should be included in the module?"
Header: "Components"
Options: [Based on what was found - e.g., "API Infrastructure", "Error Handling", "DTO/Entity", "All"]
multiSelect: true

Question 2: "What should the module be called?"
Header: "Name"
Options: ["rest", "backend", "api", "Other"]

Question 3: "Any patterns to exclude or modify?"
Header: "Customize"
Options: ["No customizations", "Exclude some patterns", "Modify placeholders"]
</decision_questions>

<save_decisions>
Use the Write tool to save decisions to `.claude/extraction/decisions.json`:

```json
{
  "module_name": "rest",
  "components": {
    "api_infrastructure": {"include": true, "customizations": []},
    "dto_entity": {"include": true, "customizations": []},
    "error_handling": {"include": true, "customizations": []}
  },
  "additional_context": "",
  "confirmed_at": "timestamp"
}
```
</save_decisions>

---

# Phase 5: Generate Output

<setup_directories>
Use Bash to create the output directory structure:
```bash
mkdir -p .claude/extraction/backends/{module-name}
mkdir -p .claude/extraction/backends/{module-name}/references
```
</setup_directories>

<generate_skill_md>
<critical>
Before generating SKILL.md, invoke the `taches-cc-resources:create-agent-skills` skill using the Skill tool.
This ensures the generated skill follows Claude Code best practices for structure, XML formatting, and content organization.

Pass the extracted patterns and user decisions as context to the skill.
</critical>

Generate SKILL.md following this structure:

```markdown
---
name: {module-name}
description: {one-line description}
---

<overview>
{High-level description}

<patterns_included>
- {Category 1}: {brief description}
- {Category 2}: {brief description}
</patterns_included>

<dependencies>
- {package}: ^{version} ({purpose})
</dependencies>
</overview>

<patterns>
<pattern name="{Category Name}">
<description>{What this pattern does}</description>

<implementation language="dart">
{GENERALIZED code with placeholders}
</implementation>

<rationale>{Why this pattern exists}</rationale>
</pattern>
</patterns>

<examples>
<example name="{Use Case}">
<scenario>{Real-world usage scenario}</scenario>

<usage language="dart">
{Example code}
</usage>

<notes>
- {Key points}
</notes>
</example>
</examples>

<references>
<reference file="references/api-infrastructure.md">{description}</reference>
</references>
```

Use the Write tool to save to: `.claude/extraction/backends/{module-name}/SKILL.md`
</generate_skill_md>

<generate_references>
For each included component, generate a reference file:

**api-infrastructure.md** (if included):
- HTTP client configuration patterns
- Interceptor implementations
- API class structure and method signatures
- Response handling patterns
- Interface definitions and mixins

**error-handling.md** (if included):
- Error type definitions
- Error mapping strategies
- Recovery patterns

**dto-entity.md** (if included):
- Serialization patterns
- Parsing implementations
- Validation approaches

Use the Write tool to save each reference file to: `.claude/extraction/backends/{module-name}/references/{name}.md`
</generate_references>

<generate_manifest_entry>
Use the Read tool to get the project name from `pubspec.yaml`, then generate the manifest entry:

```json
{
  "backends/{module-name}": {
    "version": "0.1.0",
    "description": "{description}",
    "status": "extracted",
    "files": ["SKILL.md", "references/api-infrastructure.md", ...],
    "extracted_from": "{project_name from pubspec.yaml}",
    "extraction_date": "{YYYY-MM-DD}"
  }
}
```

Use the Write tool to save to: `.claude/extraction/backends/{module-name}/manifest-entry.json`
</generate_manifest_entry>

---

# Phase 6: Verification and Report

<verification>
Verify the generated output using these tools:

1. Use the Read tool to check SKILL.md has valid YAML frontmatter
2. Use Glob to verify all referenced files exist in extraction directory
3. Use Grep to scan for project-specific values (hardcoded strings, URLs, entity names)
4. Use the Read tool to verify manifest-entry.json is valid JSON

If project-specific values found, warn:
"WARNING: Found potential project-specific value in {file}:
  Line {n}: {content}
Consider generalizing before merging to CDN."
</verification>

<final_report>
Present the staging directory contents:

```
Extraction complete! Generated files:

.claude/extraction/backends/{module-name}/
  SKILL.md                    - Main skill definition
  references/
    api-infrastructure.md     - HTTP client, API classes, composition patterns
    dto-entity.md             - DTO/entity patterns
    error-handling.md         - Error handling patterns
  manifest-entry.json         - Manifest entry for CDN

Next steps:
1. Review the generated files in .claude/extraction/backends/
2. Check for any remaining project-specific values
3. When satisfied, copy to flutter-launchpad/content/backends/{module-name}/
4. Merge manifest-entry.json into content/manifest.json
```
</final_report>

</command_workflow>

<generalization_reference>
<placeholder_conventions>
| Placeholder | Usage | Example |
|-------------|-------|---------|
| `{Entity}` | Class/type name (PascalCase) | `class {Entity}Api` |
| `{entity}` | Variable name (camelCase) | `final {entity} = ...` |
| `{entities}` | Plural (URL path) | `/api/{entities}` |
| `{basePath}` | API base path | `{basePath}/{entities}` |
| `{baseUrl}` | API base URL | `baseUrl: '{baseUrl}'` |
| `{App}` | App name prefix (PascalCase) | `class {App}Exception` |
| `{timeout}` | Timeout duration | `Duration(seconds: {timeout})` |
</placeholder_conventions>

<what_not_to_generalize>
- Library imports (package:dio/dio.dart)
- Standard method names (fromJson, toJson)
- HTTP method names (get, post, put, delete)
- Common annotations (@override, @required)
- try/catch structure
</what_not_to_generalize>
</generalization_reference>

<success_criteria>
- User confirmed extraction scope via AskUserQuestion
- 3 Explore agents analyzed the codebase in parallel
- Findings presented and inconsistencies confirmed with user
- Additional research performed if requested
- User decisions gathered for components and module name
- All files written to staging using Write tool
- Final verification completed
- Next steps presented to user
</success_criteria>
