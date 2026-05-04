---
aliases: [Quotation]
tags: [laravel, backend, auto-generated, model, quotation]
---

# Quotation Model

A vendor's response to an [[Rfq Model]]. It includes pricing, terms, and additional service charges.

## Current Architecture & Flow

- **Table**: `quotations`
- **Primary Relationships**:
	- `belongsTo` [[Rfq Model]]
	- `belongsTo` [[Vendor Model]]
	- `hasMany` [[QutationService Model]] (Note the typo in the model name)
	- `morphMany` [[Document Model]]
- **Financials**:
	- Stores `unit_price`, `tax_amount`, `shipping_amount`, `loading_charge`, and `services_charge`.
	- `total_amount` is a pre-calculated sum of all charges.

## Dependencies & Graph Links

- [[QuotationService]] - Core logic for submission and updates.
- [[QuotationController]] - API endpoints.
- [[BoqSheetEntryService]] - Links accepted quotations to the BOQ.

## Red Flags & Tech Debt

- **Typo in Model Name**: `QutationService` is missing the 'o'. This should be renamed to `QuotationService` (the model, not the service class).
- **Manual Total Calculation**: The `total_amount` is calculated in the service layer before saving. If any component price changes, the total might become stale if not updated correctly.
- **Base64 Document Handling**: [[QuotationService]] contains logic to decode Base64 files, which adds complexity to the service layer.

## Future Upgrades (Postgres & Scalability)

- **Computed Columns**: Use Postgres stored generated columns for `total_amount` to ensure mathematical integrity at the database level.
