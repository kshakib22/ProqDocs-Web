---
aliases: []
tags: [laravel, backend, auto-generated]
title: "QutationService Model"
---
# QutationService Model

**⚠️ CRITICAL: This class has a typo in its name - "Qutation" instead of "Quotation". This is a breaking change waiting to happen.**

The QutationService model represents line items within a quotation, allowing vendors to break down their quote into multiple service/product components.

## Current Architecture & Flow

### Model Structure
- **Table**: `qutation_services` (note: typo in table name too)
- **Key Attributes**:
  - `quotation_id`: FK to [Quotation Model](Quotation Model.md)
  - `name`: Service/item name
  - `unit`: Unit of measurement
  - `unit_price`: Price per unit
  - `quantity`: Quantity
  - `total_price`: Calculated total (unit_price × quantity)

### Relationships
- `quotation()`: BelongsTo [Quotation Model](Quotation Model.md)

### Auto-Calculation
The model automatically calculates `total_price` on save:
```php
static::saving(function ($service) {
    if ($service->unit_price && $service->quantity) {
        $service->total_price = $service->unit_price * $service->quantity;
    }
});
```

## Dependencies & Graph Links

- Created by [QuotationService](QuotationService.md) when building quotations
- Referenced by [Quotation Model](Quotation Model.md) via `quotationServices()` relationship
- Included in [QuotationResource](QuotationResource.md) transformation

## Red Flags & Tech Debt

### Critical Naming Issue
- **Class name typo**: `QutationService` instead of `QuotationServiceItem`
- **Table name typo**: `qutation_services` instead of `quotation_service_items`
- This typo is propagated throughout the codebase
- Will require database migration and code refactoring to fix

### Missing Database Constraints
- No check constraint ensuring `total_price = unit_price * quantity`
- No check constraint ensuring positive values
- No foreign key cascade for soft-deleted quotations

### Business Logic
- Auto-calculation in model boot could be bypassed with direct DB updates
- No validation on unit_price or quantity being positive

## Future Upgrades (Postgres & Scalability)

### Database Improvements
```sql
-- Rename table (requires migration)
ALTER TABLE qutation_services RENAME TO quotation_service_items;

-- Add check constraints
ALTER TABLE quotation_service_items ADD CONSTRAINT chk_positive_prices
  CHECK (unit_price >= 0 AND quantity >= 0 AND total_price >= 0);

-- Add computed column for total_price (PostgreSQL 12+)
ALTER TABLE quotation_service_items
  ADD COLUMN calculated_total NUMERIC GENERATED ALWAYS AS
  (unit_price * quantity) STORED;

-- Add index for common queries
CREATE INDEX idx_quotation_services_quotation
  ON quotation_service_items(quotation_id);
```

### Refactoring Plan
1. Create new `QuotationServiceItem` model
2. Create migration to rename table
3. Update all references in codebase
4. Deprecate old `QutationService` class
5. Add tests for new model

### Model Enhancements
1. Add validation rules
2. Consider using Laravel's `Casts\AsArrayObject` for complex pricing
3. Add scope for filtering by price ranges
