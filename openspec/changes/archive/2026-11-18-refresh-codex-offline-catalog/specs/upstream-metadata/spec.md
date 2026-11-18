## ADDED Requirements

### Requirement: Maintain model and price snapshots in the fork

The metadata updater SHALL obtain model metadata from the public OpenAI Codex release tag corresponding to the generated client version. It SHALL validate its inputs before replacing the snapshots. The fork's scheduled workflow SHALL target its configured default branch and publish changed snapshots on a review branch. A configured publishing token SHALL allow it to open a pull request.

#### Scenario: Upstream model catalog is unavailable

- **WHEN** price and version discovery succeed but the tagged model catalog is unusable
- **THEN** generation fails and the existing bundled metadata is preserved
