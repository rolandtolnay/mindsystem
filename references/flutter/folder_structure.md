# Folder Structure

1. **Organize by feature.** Each feature gets its own folder (e.g., `account/`, `games/`).

2. **Screens live at the feature root.** Put all screen files directly inside the feature folder (e.g., `account_screen.dart`, `edit_account_screen.dart`).

3. **Only create subfolders when there’s enough stuff to justify them.**
   * If the feature has **2+ reusable widgets**, create `widgets/` and move those widget files there.
   * If the feature has **2+ providers/state files**, create `providers/` and move those files there.
   
4. **Create a `domain/` folder (usually always).** Put **models** and **repositories** in `domain/`.

5. **If a feature is very large, split it into subfeatures.**
   Example: `games/` might become `games/library/`, `games/details/`, etc. Inside **each subfeature**, repeat the same rules: screens at that subfeature root, optional `widgets/` and `providers/`, and a `domain/` folder for models/repositories.

### Example structure

```text
lib/
  features/
    account/
      account_screen.dart
      edit_account_screen.dart
      widgets/
        account_avatar.dart
        account_form.dart
      providers/
        account_provider.dart
        edit_account_provider.dart
      domain/
        account.dart
        account_repository.dart

    games/
      library/
        games_library_screen.dart
        widgets/
        providers/
        domain/
      details/
        game_details_screen.dart
        widgets/
        providers/
        domain/
```

## One coherent paragraph for a coding LLM agent

I organize Flutter code by feature folders (for example, an `account` feature). Inside each feature folder, I keep all screen files at the top level (e.g., `account_screen.dart`, `edit_account_screen.dart`). If the feature ends up with two or more reusable widgets, I create a `widgets` subfolder and place those widget files there; likewise, if the feature has two or more providers/state-management files, I create a `providers` subfolder and move them there. I usually always create a `domain` folder inside the feature, and that `domain` folder contains the feature’s models and repositories. If a feature becomes very complex (for example, `games`) and it naturally splits into multiple subfeatures, I create subfeature folders under the main feature and apply the same structure inside each subfeature: screens at the subfeature root, plus `widgets/` and `providers/` only when there are multiple files, and a `domain/` folder for models and repositories.
