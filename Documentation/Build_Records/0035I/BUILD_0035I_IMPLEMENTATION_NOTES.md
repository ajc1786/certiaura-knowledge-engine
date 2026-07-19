# Build 0035I Implementation Notes

## Import targets

- Standard, schema, templates, matrices and operational registers: existing `08_Product_Passports` structure.
- Supplier evidence-expiry register: existing `06_Evidence` structure.
- Marketplace eligibility register: existing `10_Marketplace` structure.
- Assessment, scheduler, dashboard and validator: existing `13_Project_Genesis` structure.

## Integration rules

1. Allocate permanent Universal Asset Identifiers during controlled import.
2. Preserve Builds 0035D–0035H unchanged.
3. Map supplier records to existing Product Passport™ and Marketplace records through the established relationship model.
4. Do not create a new top-level knowledge system.
5. Review all proposed register entries before merge.
6. Run repository validation after import.

## Operational note

A supplier may be organisationally qualified while a particular product, batch or claim is rejected. Conversely, no product or marketplace approval may be inferred merely from supplier qualification.
