# Folder Structure

## Organization

- Organize by feature: `lib/features/account/`, `lib/features/games/`
- Screens at feature root: `account/account_screen.dart`, `account/edit_account_screen.dart`
- `widgets/` subfolder when 2+ reusable widgets exist in the feature
- `providers/` subfolder when 2+ provider/state files exist in the feature
- `domain/` subfolder for models and repositories — almost always create this

## Subfeatures

- Split large features into subfeatures: `games/library/`, `games/details/`
- Each subfeature repeats the same structure: screens at root, optional `widgets/`, `providers/`, and `domain/`

## Example

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

## Anti-Patterns (flag these)

- Deep nesting: `lib/features/home/presentation/screens/` → `lib/features/home/home_screen.dart`
- Single widget in `widgets/` (keep at feature root until 2+)
- Single provider in `providers/` (keep at feature root until 2+)
- Missing `domain/` folder with models scattered at feature root
- Barrel files that only re-export
