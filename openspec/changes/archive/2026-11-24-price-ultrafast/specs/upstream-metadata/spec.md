## ADDED Requirements

### Requirement: Ingest explicit Ultrafast price data

The pricing catalog SHALL accept validated Ultrafast token prices from models.dev and LiteLLM, including a declared long-context threshold and corresponding rates. A service mode without prices SHALL preserve usable base pricing. Cost estimates for a model with no explicit or documented Ultrafast price SHALL be unknown.

#### Scenario: A mode declares prices for a separate context window

- **WHEN** a model declares Ultrafast prices and an Ultrafast context threshold
- **THEN** snapshot round-trips preserve the tier and threshold
- **AND** Standard pricing keeps its own threshold

#### Scenario: A model variant inherits only a Standard price

- **WHEN** a broad model-name wildcard matches a variant with no published or cataloged Ultrafast rates
- **THEN** its Ultrafast estimate remains unknown
