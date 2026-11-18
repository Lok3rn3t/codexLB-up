## Why

Cold starts currently list a hand-maintained set of models which predates GPT-6. The daily metadata job skips this fork and assumes its default branch is main.

## What changes

- Generate the public offline model metadata from the same tagged OpenAI Codex release as the bundled client version.
- Preserve existing compatibility entries, per-account live discovery and historical cost lookup. Refresh the independent pricing bundle with its existing generator.
- Run the maintenance workflow against the fork's default branch and make generated updates available for review.
