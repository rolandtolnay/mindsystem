# Flutter Localization with Parallel Sub-Agents

Translate all hard-coded strings in Dart files using Flutter's easy_localization package with parallel sub-agent execution for maximum efficiency.

## Command Arguments

This command accepts `$ARGUMENTS` to specify which files to process:

- **Commit SHA**: Process all `.dart` files changed in that commit (e.g., `abc123f`)
- **File paths**: Process specific files or directories (e.g., `lib/invoice/`)
- **No arguments**: Search entire `lib/` directory for files containing `// TODO(TRANSLATE)` comments

## Execution Phases

### Phase 1: Discover Files to Process

**Determine target files based on `$ARGUMENTS`:**

1. **If commit SHA provided**:
   ```bash
   git diff-tree --no-commit-id --name-only -r <commit-sha> | grep '\.dart$'
   ```
   This gets all `.dart` files changed in the specified commit.

2. **If file paths provided**:
   Use Glob to find all `.dart` files in the specified paths.

3. **If no arguments (default)**:
   Search the entire `lib/` directory for files containing `// TODO(TRANSLATE)`:
   ```bash
   grep -rl "// TODO(TRANSLATE)" lib/ --include="*.dart"
   ```

Store the complete list of target files for distribution across extractors.

### Phase 2: Distribute Files and Launch Parallel String Extraction

**CRITICAL: Launch ALL extraction agents SIMULTANEOUSLY in a single message with multiple Task tool calls.**

**File Distribution Strategy**:
- Group files by feature/directory for better context (e.g., all `lib/invoice/*` files together)
- Assign 3-5 files per agent
- Maximum of 10 agents running in parallel
- Optimize distribution: if you have 23 files, create 5 agents with 4-5 files each

**Launch Pattern**:
```
Deploy N dart-string-extractor agents in parallel RIGHT NOW:
- Agent 1: Extract from lib/invoice/invoice_screen.dart, lib/invoice/invoice_detail_screen.dart, lib/invoice/widgets/invoice_card.dart
- Agent 2: Extract from lib/payment_link/payment_link_screen.dart, lib/payment_link/widgets/...
- Agent 3: Extract from lib/customer/...
...

Launch all agents in a SINGLE message NOW. Wait for ALL to complete before proceeding.
```

Each sub-agent will:
- Analyze assigned Dart files
- Identify user-facing hardcoded strings
- Ignore technical strings (API endpoints, log messages, etc.)
- Ignore already-localized strings (LocaleKeys.*)
- Return structured output: `[Line X] "string", Context: Widget.method, Usage: Button label, Suggested Key: feature_section_purpose`

### Phase 3: Consolidate and Deduplicate (Main Agent)

After ALL extractor agents complete:

1. **Collect all extracted strings** from agent reports into a master list

2. **Read existing translations**:
   - Read `lib/generated/translations/locale_keys.g.dart` to get all existing keys and their paths
   - Read `assets/translations/en.json` to get existing English translations

3. **Deduplicate and map strings**:
   For each extracted string:
   - **Check for exact match**: If the string already exists in en.json, map to the existing LocaleKeys path
   - **Check for similar match**: If a very similar string exists (e.g., "Cancel" vs "Cancel "), use AskUserQuestion to confirm reuse
   - **Create new key**: If truly new, generate key using hybrid approach:
     - Start with file path prefix (e.g., `lib/invoice/...` → `invoice_*`)
     - Refine using context (widget name, usage) and suggested key from extractor
     - Follow pattern: `feature_section_purpose` in snake_case
     - Use standard suffixes: `_title`, `_subtitle`, `_description`, `_label`, `_hint`, `_error`, `_success`, `_toast`, `_button`

4. **Build mapping structure**:
   ```json
   {
     "lib/invoice/invoice_screen.dart": {
       "Mark as Paid": "invoice_mark_as_paid_button",
       "Processing...": "invoice_processing_status"
     },
     "lib/payment_link/payment_link_screen.dart": {
       "Cancel": "common_cancel"  // Reused existing key
     }
   }
   ```

### Phase 4: Update Translation JSON (Main Agent)

Update `assets/translations/en.json`:

1. **Add new keys only** (skip keys that were mapped to existing ones)
2. **Preserve structure**: Maintain nested feature organization
3. **Sort alphabetically**: Add new keys alphabetically within their feature section
4. **Validate JSON**: Ensure valid JSON syntax after updates

Example addition:
```json
"invoice": {
  "existing_key": "Existing Value",
  "mark_as_paid_button": "Mark as Paid",
  "processing_status": "Processing..."
}
```

### Phase 5: Generate LocaleKeys (Main Agent)

Run code generation commands sequentially:

```bash
fvm dart run easy_localization:generate -S assets/translations -O lib/generated/translations && \
fvm dart run easy_localization:generate -S assets/translations -O lib/generated/translations -f keys -o locale_keys.g.dart
```

Wait for both commands to complete successfully.

### Phase 6: Verify Generated Keys (Main Agent)

Read `lib/generated/translations/locale_keys.g.dart` to:
- Confirm all new keys were generated correctly
- Get the exact LocaleKeys property paths for the next phase
- Update the mapping structure with verified paths (e.g., `invoice_mark_as_paid_button` → `LocaleKeys.invoice_mark_as_paid_button`)

### Phase 7: Launch Parallel Code Updates

**CRITICAL: Launch ALL localization-replacer agents SIMULTANEOUSLY in a single message.**

**Distribution Strategy**:
- Group files by feature/directory
- 3-5 files per agent
- Maximum 10 agents in parallel

**Launch Pattern**:
```
Deploy N localization-replacer agents in parallel RIGHT NOW:
- Agent 1: Update lib/invoice/invoice_screen.dart with mapping {"Mark as Paid": "LocaleKeys.invoice_mark_as_paid_button", ...}
- Agent 2: Update lib/payment_link/payment_link_screen.dart with mapping {...}
- Agent 3: Update lib/customer/... with mapping {...}
...

Launch all agents in a SINGLE message NOW. Wait for ALL to complete.
```

Each sub-agent will:
1. Read the specified Dart file
2. Replace hardcoded strings with `LocaleKeys.xxx.tr()` calls
3. Add required imports:
   - `import 'package:easy_localization/easy_localization.dart';`
   - `import 'package:merchant_app/generated/translations/locale_keys.g.dart';`
4. Handle string interpolations: `'Total: $amount'` → `LocaleKeys.payment_total.tr(args: [amount.toString()])`
5. Remove `// TODO(TRANSLATE)` comments
6. Preserve code structure and formatting

### Phase 8: Verification (Main Agent)

After all replacer agents complete:

```bash
fvm flutter analyze
```

Check for:
- No compilation errors
- No analyzer warnings related to the changes
- All imports are correct

## Quality Checklist

- [ ] All target files were processed
- [ ] Duplicate strings mapped to existing keys
- [ ] New keys follow naming conventions (feature_section_purpose)
- [ ] Valid JSON in assets/translations/en.json
- [ ] Code generation successful
- [ ] All TODO(TRANSLATE) comments removed
- [ ] No hardcoded strings remain in processed files
- [ ] Flutter analyze shows no new errors
- [ ] Proper imports added to all modified files

## Agent Coordination Rules

- **File Distribution**: Even distribution considering file size and feature grouping
- **Error Recovery**: If an agent fails, reassign its files to another agent or retry
- **Context Isolation**: Each sub-agent works independently on its assigned files
- **Synchronization**: Main agent waits for ALL agents in a phase before proceeding to next phase
- **Parallel Launch**: ALWAYS use a SINGLE message with MULTIPLE Task tool calls for parallel execution

## Summary Output

After completion, provide:
1. Total files processed
2. Total strings extracted
3. New keys added to en.json (count)
4. Existing keys reused (count)
5. Files modified with LocaleKeys replacements
6. Any errors or warnings encountered
7. Analyzer results

## Usage Examples

```bash
# Process all files with TODO(TRANSLATE)
/translate

# Process files changed in a specific commit
/translate abc123f

# Process specific directory
/translate lib/invoice/

# Process multiple files
/translate lib/invoice/invoice_screen.dart lib/customer/customer_screen.dart
```

---

**Remember**: This command leverages Claude Code's ability to run up to 10 sub-agents concurrently. Always launch agents in parallel batches using explicit parallel language in a SINGLE message with MULTIPLE tool calls. Never process files sequentially unless absolutely necessary.
