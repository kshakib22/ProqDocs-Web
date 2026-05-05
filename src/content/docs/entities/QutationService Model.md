---
aliases: [QutationService]
tags: [laravel, backend, auto-generated, model, quotation]
title: "Qutationservice Model"
---

# QutationService Model

**Note: This model name contains a typo and should be QuotationService.**

Represents additional services (e.g., installation, labor) associated with a [Quotation Model](./Quotation Model.md).

## Current Architecture & Flow

- **Table**: `qutation_services`
- **Fields**: `name`, `unit`, `unit_price`, `quantity`, `total_price`.
- **Relationship**: `belongsTo` [Quotation Model](./Quotation Model.md).

## Dependencies & Graph Links

- [Quotation Model](./Quotation Model.md)
- [QuotationService](./QuotationService.md) (the business logic class)

## Red Flags & Tech Debt

- **Naming**: The typo `Qutation` makes the codebase harder to search and maintain.
- **Precision**: Uses `unit_price * quantity` in PHP. Should use `bcmath` for financial precision.

## Future Upgrades (Postgres & Scalability)

- **Rename**: Refactor to `QuotationServiceItem` or similar to avoid confusion with the service class and fix the typo.
