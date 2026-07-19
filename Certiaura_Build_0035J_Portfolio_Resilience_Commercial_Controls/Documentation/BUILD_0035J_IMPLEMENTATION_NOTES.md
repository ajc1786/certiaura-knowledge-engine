# Build 0035J Implementation Notes

## Import targets

- Portfolio, panel, sourcing and Marketplace controls: existing `10_Marketplace` structure.
- Total-cost standards and registers: existing `09_Cost_Intelligence` structure.
- Automation, validators, tests and dashboards: existing `13_Project_Genesis` structure.

## Integration rules

1. Allocate permanent Universal Asset Identifiers during controlled import.
2. Preserve Builds 0035D–0035I unchanged.
3. Link portfolio and sourcing records to existing supplier, Product Passport, evidence, Cost Intelligence and Marketplace records.
4. Do not create a new top-level knowledge system.
5. Review proposed register structures against the canonical repository before merge.
6. Never convert an automated ranking into an award or approval.
7. Run full repository validation after import.
