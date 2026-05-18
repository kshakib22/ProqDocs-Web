---
name: QutationService-Model
description: Laravel Eloquent model for Quotation Service line items - represents service/product breakdown within a quotation
type: entity
title: "QutationService Model"
---

# QutationService Model

## Architectural Purpose

**⚠️ CRITICAL: This class has a typo in its name - "Qutation" instead of "Quotation". This is a breaking change waiting to happen.**

`QutationService` represents line items within a quotation, allowing vendors to break down their quote into multiple service/product components. This model enables detailed cost breakdowns for complex quotations, supporting:

- **Service breakdown**: Multiple line items per quotation
- **Itemized pricing**: Individual pricing for each component
- **Automatic calculation**: Total price computed from unit price × quantity
- **Flexible quoting**: Support for mixed product/service quotes

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `quotation_id` | bigint | Foreign key | Links to `quotations` table |
| `name` | string | Service/item name | Human-readable description |
| `unit` | string | Unit of measurement | e.g., "hour", "kg", "piece" |
| `unit_price` | decimal | Price per unit | Cast to decimal:2 |
| `quantity` | decimal | Quantity | Cast to decimal:2 |
| `total_price` | decimal | Calculated total | Cast to decimal:2 |
| `created_at` | timestamp | Creation time | Laravel managed |
| `updated_at` | timestamp | Last update | Laravel managed |

**⚠️ CRITICAL TYPO:** The table name is also `qutation_services` (note the typo), which propagates the naming issue throughout the database.

## Model Relationships

### `quotation(): BelongsTo`

```php
public function quotation(): BelongsTo
{
    return $this->belongsTo(Quotation::class);
}
```

- **Purpose:** Links to the parent quotation
- **Cardinality:** Many-to-one
- **Usage:** Access quotation details and totals

## Attribute Casts

...

## Data Flow

### Creation Flow

```
1. Vendor creates quotation with service items
2. QuotationService::create() instantiates QutationService models
3. Model boot hook calculates total_price
4. Models save to database
5. Quotation.services_charge updated with sum of totals
```

### Update Flow

...

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| **Class name typo** | **CRITICAL** | Breaking change risk | Rename to `QuotationServiceItem` |
| **Table name typo** | **CRITICAL** | Breaking change risk | Rename to `quotation_service_items` |
| No check constraint on totals | MEDIUM | Inconsistent data | Add `CHECK (total_price = unit_price * quantity)` |
| No positive value validation | MEDIUM | Negative values possible | Add validation rules |
| No FK cascade for soft-deleted quotations | MEDIUM | Orphaned data | Add cascade handling |
| Auto-calculation bypassable | LOW | Data inconsistency | Use database triggers or computed columns |

## Naming Issue Details

...

## Cross-References

- [Quotation-Model](/entities/quotation-model) - Parent quotation for this service
- [QuotationService](/entities/quotationservice) - Business logic for quotation operations
- [QuotationsServiceResource](/entities/quotationsserviceresource) - API resource for serialization

## Usage Examples

...
