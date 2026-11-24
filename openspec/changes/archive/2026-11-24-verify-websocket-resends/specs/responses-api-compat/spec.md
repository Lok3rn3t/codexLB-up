## ADDED Requirements

### Requirement: Use the client’s complete history on a new Codex WebSocket

When the Codex client supplies an unanchored request on a different physical upstream, the proxy SHALL preserve the original payload if it matches the completed input prefix, includes a fingerprint-verified copy of the completed output and new input, and passes the existing portability checks. A delta or an account-bound request SHALL retain its ownership requirements.

#### Scenario: A client reconnects with a portable full history

- **GIVEN** the recorded completion covers the entire input context and belongs to a different upstream connection
- **WHEN** the client resends that prefix, the prior assistant response, and a new user message without a parent ID
- **THEN** the proxy sends the supplied history without injecting the old response ID

#### Scenario: Preserve Codex sampled output metadata

- **WHEN** Codex resends an assistant output-text item with annotations or log probabilities
- **THEN** the proxy SHALL retain those arrays, including empty arrays
- **AND** empty arrays may be certified as portable while populated provider metadata retains the existing ownership requirement

#### Scenario: Transparent replay requires matched tool calls and outputs

- **WHEN** a proxy prepares an anchorless recovery using historical client-executed tool calls
- **THEN** every output SHALL follow its matching call with the same ID and type, with no duplicate calls, duplicate results, or missing results
- **AND** results for distinct parallel calls MAY arrive in either order
- **AND** an anchored delta may still return the result of an upstream-owned tool call
