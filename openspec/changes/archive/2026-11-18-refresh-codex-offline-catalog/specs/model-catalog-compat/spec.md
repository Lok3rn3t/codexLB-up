## ADDED Requirements

### Requirement: Public Codex release models are available at cold start

The offline model registry SHALL supplement its existing compatibility entries with public, API-supported shell models from the bundled stable Codex release. It SHALL omit hidden and restricted release entries from this supplement. It SHALL preserve the supplied model capabilities, context limits and available plans. An authoritative live account catalog SHALL take precedence. Pricing records alone MUST NOT add a model to discovery.

#### Scenario: A new public model appears in a release

- **WHEN** the bundled Codex release lists a new public model and the proxy has no live or persisted catalog
- **THEN** both model-list endpoints include it with its release metadata
- **AND** it disappears from discovery if the subsequent authoritative account catalog omits it
