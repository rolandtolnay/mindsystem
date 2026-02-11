# Localization Codegen Script (easy_localization + dart format fix)

Wrapper script that runs `easy_localization:generate` and prepends `// dart format off` to generated files, preventing `dart format` from corrupting non-standard indentation in codegen output.

## The Problem

- `easy_localization:generate` produces `.g.dart` files with non-standard formatting (wrong indentation, missing spaces, double spaces in declarations)
- `dart format` has no file exclusion mechanism — `analysis_options.yaml` `exclude` only affects the analyzer, not the formatter
- Running `dart format .` after codegen silently corrupts the generated files

## The Solution

Dart 3.7+ supports `// dart format off` as the first line of a file — the formatter skips the entire file. The script automates prepending this pragma after generation.

## Script: `scripts/generate_localizations.dart`

```dart
/// Generate localization files from translation JSON assets.
///
/// Workaround: easy_localization's generator produces non-standard indentation
/// that conflicts with `dart format`. Since `dart format` has no file exclusion
/// mechanism, we prepend `// dart format off` (Dart 3.7+) to each generated
/// file so the formatter skips them entirely.
///
/// Usage: dart run scripts/generate_localizations.dart
library;

import 'dart:io';

const _source = 'assets/translations';
const _output = 'lib/generated/translations';
const _formatOffComment = '// dart format off';

Future<void> main() async {
  // Step 1: Generate codegen_loader.g.dart (embeds all translations)
  await _generate(['-S', _source, '-O', _output]);

  // Step 2: Generate locale_keys.g.dart (type-safe key constants)
  await _generate([
    '-S',
    _source,
    '-O',
    _output,
    '-f',
    'keys',
    '-o',
    'locale_keys.g.dart',
  ]);

  // Step 3: Prepend format-off pragma to all generated files
  final dir = Directory(_output);
  for (final file in dir.listSync().whereType<File>()) {
    if (!file.path.endsWith('.g.dart')) continue;
    final content = file.readAsStringSync();
    if (content.startsWith(_formatOffComment)) continue;
    file.writeAsStringSync('$_formatOffComment\n$content');
  }
}

Future<void> _generate(List<String> args) async {
  final result = await Process.run('dart', [
    'run',
    'easy_localization:generate',
    ...args,
  ]);
  stdout.write(result.stdout);
  stderr.write(result.stderr);
  if (result.exitCode != 0) exit(result.exitCode);
}
```

- `-S` = source directory, `-O` = output directory
- `-f keys` = generate key constants, `-o` = output filename
- Without `-f` flag, generates `codegen_loader.g.dart` by default
- Idempotent: checks if pragma already exists before prepending
- **If using FVM:** change `Process.run('dart', [` to `Process.run('fvm', ['dart',` and add `runInShell: true`

## Adapting to Your Project

### Files to Create or Modify

| File | Change |
|------|--------|
| `scripts/generate_localizations.dart` | Create script above; adjust `_source` and `_output` paths to match your project |
| `.vscode/tasks.json` | Add the generate localizations task (see [VSCode Integration](#vscode-integration)) |
| `.vscode/launch.json` | Add `"preLaunchTask": "Generate Localizations"` to every launch configuration |
| `.vscode/settings.json` | Point `dart.flutterSdkPath` to FVM version if using FVM |

## Usage Command

```bash
# Without FVM
dart run scripts/generate_localizations.dart

# With FVM
fvm dart run scripts/generate_localizations.dart
```

Run after modifying any JSON translation file in `assets/translations/`.

## VSCode Integration

Running the script from terminal works, but a VSCode task is superior: one keyboard shortcut, no need to remember the command, and it runs in the correct working directory automatically.

### `.vscode/tasks.json`

If the file doesn't exist, create it. If it exists, add the task to the `tasks` array.

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Localizations",
      "type": "shell",
      "command": "fvm dart run scripts/generate_localizations.dart",
      "problemMatcher": [],
      "group": "build"
    }
  ]
}
```

- `"problemMatcher": []` — empty array prevents VSCode from waiting for problem output (script finishes cleanly)
- `"group": "build"` — accessible via `Cmd+Shift+B` / `Ctrl+Shift+B`
- Remove the `fvm` prefix from `command` if not using FVM

### `.vscode/settings.json`

If using FVM, point the Dart extension to the FVM-managed SDK:

```json
{
  "dart.flutterSdkPath": ".fvm/versions/3.38.5"
}
```

- Adjust version number to match your FVM Flutter version; not required if not using FVM

### `.vscode/launch.json` (preLaunchTask)

The real payoff: wire `"preLaunchTask": "Generate Localizations"` into every launch configuration. Translations are always up-to-date when you hit F5 — no manual step, no stale keys.

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "myapp development",
      "request": "launch",
      "type": "dart",
      "preLaunchTask": "Generate Localizations",
      "program": "lib/main_dev.dart",
      "args": ["--flavor", "dev"]
    }
  ]
}
```

- `"preLaunchTask"` value must exactly match the `"label"` in `tasks.json`
- Add to **every** launch configuration (dev, prod, profile, release)
- If the task fails (e.g. malformed JSON), the launch aborts — catches translation bugs before runtime

### Running the Task Manually

- **Command Palette**: `Cmd+Shift+P` → "Tasks: Run Task" → "Generate Localizations"
- **Build shortcut**: `Cmd+Shift+B` → select "Generate Localizations"

## Dart Version Requirement

- `// dart format off` requires **Dart 3.7+** (shipped with Flutter 3.29+)
- For older Dart versions, this approach will not work — the pragma is ignored

## Checklist

- Script `_source` and `_output` paths match your project structure
- Using Dart 3.7+ / Flutter 3.29+ (required for `// dart format off` pragma)
- Generated `.g.dart` files start with `// dart format off` after running script
- `.vscode/tasks.json` has "Generate Localizations" task with correct command
- `.vscode/launch.json` has `"preLaunchTask"` on every configuration, label matches `tasks.json`
- Pressing F5 runs the script before launch (verify in terminal output)

## Anti-Patterns (flag these)

- Running `easy_localization:generate` directly without the wrapper script (generated files will be corrupted by next `dart format .` run)
- Adding generated translation files to `analysis_options.yaml` exclude and assuming that prevents formatting (it only prevents analysis)
- Using `// dart format width=80` instead of `// dart format off` (reformats with custom width instead of skipping)
