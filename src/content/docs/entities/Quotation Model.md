---
aliases: [Quotation]
tags: [laravel, backend, auto-generated, model, quotation]
title: "Quotation Model"
---

# Quotation Model

A vendor's response to an [Rfq Model](/entities/rfq-model). It includes pricing, terms, and additional service charges.

## Current Architecture & Flow

- **Table**: `quotations`
- **Primary Relationships**:
	- `belongsTo` [Rfq Model](/entities/rfq-model)
	- `belongsTo` Vendor Model
	- `hasMany` [QutationService Model](/entities/qutationservice-model) (Note the typo in the model name)
	- `morphMany` Document Model
- **Financials**:
	- Stores `unit_price`, `tax_amount`, `shipping_amount`, `loading_charge`, and `services_charge`.
	- `total_amount` is a pre-calculated sum of all charges.

## Dependencies & Graph Links

- [QuotationService](/entities/quotationservice) - Core logic for submission and updates.
- [QuotationController](/entities/quotationcontroller) - API endpoints.
- [BoqSheetEntryService](/entities/boqsheetentryservice) - Links accepted quotations to the BOQ.

## Red Flags & Tech Debt

- **Typo in Model Name**: `QutationService` is missing the 'o'. This should be renamed to `QuotationService` (the model, not the service class).
- **Manual Total Calculation**: The `total_amount` is calculated in the service layer before saving. If any component price changes, the total might become stale if not updated correctly.
- **Base64 Document Handling**: [QuotationService](/entities/quotationservice) contains logic to decode Base64 files, which adds complexity to the service layer.

## Future Upgrades (Postgres & Scalability)

- **Computed Columns**: Use Postgres stored generated columns for `total_amount` to ensure mathematical integrity at the database level.
