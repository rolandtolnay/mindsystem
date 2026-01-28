---
title: Extract Shared Visual Patterns
category: structure
impact: MEDIUM-HIGH
impactDescription: Guarantees visual consistency
tags: widget-extraction, style-variants, ui-deduplication, decoration
---

## Extract Shared Visual Patterns

Deduplicate UI with style variants. When similar visual patterns appear 2+ times, extract a shared widget with an enum or sealed class for variants.

**Detection signals:**
- Similar Container/decoration patterns across multiple widgets
- Visual elements (colors, padding, borders) vary based on state
- Design change would require updating multiple files
- Subtle inconsistencies between similar UI elements

**Incorrect (duplicated patterns):**

```dart
// In QuestClaimButton
Container(
  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  decoration: BoxDecoration(
    color: isExpired ? AppColors.gray400 : AppColors.forge,
    borderRadius: BorderRadius.circular(20),
  ),
  child: Row(children: [Text('grape'), Text('$reward')]),
)

// In QuestListTile (slightly different)
Container(
  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(20),
    border: Border.all(color: ...),
  ),
  child: Row(children: [Text('grape'), Text('$reward')]),
)
```

**Correct (shared widget with variants):**

```dart
enum QuestRewardStyle { filled, outlined, disabled }

class QuestRewardDisplay extends StatelessWidget {
  final int reward;
  final QuestRewardStyle style;

  const QuestRewardDisplay({
    super.key,
    required this.reward,
    this.style = QuestRewardStyle.filled,
  });

  Widget build(context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: style.buildDecoration(context),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('grape'),
          const SizedBox(width: 4),
          Text('$reward', style: style.buildTextStyle(context)),
        ],
      ),
    );
  }
}

extension on QuestRewardStyle {
  BoxDecoration buildDecoration(BuildContext context) => switch (this) {
    QuestRewardStyle.filled => BoxDecoration(
      color: AppColors.forge,
      borderRadius: BorderRadius.circular(20),
    ),
    QuestRewardStyle.outlined => BoxDecoration(
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: AppColors.forge),
    ),
    QuestRewardStyle.disabled => BoxDecoration(
      color: AppColors.gray400,
      borderRadius: BorderRadius.circular(20),
    ),
  };

  TextStyle buildTextStyle(BuildContext context) => switch (this) {
    QuestRewardStyle.disabled => context.textTheme.bodyMedium!.copyWith(color: AppColors.gray600),
    _ => context.textTheme.bodyMedium!,
  };
}
```

**Why it matters:**
- Visual consistency is guaranteed
- Style changes propagate automatically
- New variants are added in one place
- Reduces widget file sizes significantly

**Detection questions:**
- Are there similar Container/decoration patterns across multiple widgets?
- Do visual elements (colors, padding, borders) vary based on state?
- Would a design change require updating multiple files?
- Are there subtle inconsistencies between similar UI elements?
