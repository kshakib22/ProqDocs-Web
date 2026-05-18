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
  - `quotation_id`: FK to [Quotation Model](/entities/quotation-model)
  - `name`: Service/item name
  - `unit`: Unit of measurement
  - `unit_price`: Price per unit
  - `quantity`: Quantity
  - `total_price`: Calculated total (unit_price × quantity)

### Relationships
- `quotation()`: BelongsTo [Quotation Model](/entities/quotation-model)

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

- Created by [QuotationService](/entities/quotationservice) when building quotations
- Referenced by [Quotation Model](/entities/quotation-model) via `quotationServices()` relationship
- Included in [QuotationResource](/entities/quotationresource) transformation

## Red Flags & Tech Debt

...
