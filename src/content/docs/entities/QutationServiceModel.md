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

```php
protected $casts = [
    'unit_price' => 'decimal:2',
    'quantity' => 'decimal:2',
    'total_price' => 'decimal:2',
];
```

All monetary and quantity fields are cast to decimal with 2 decimal places for consistent precision.

## Fillable Attributes

```php
protected $fillable = [
    'quotation_id',
    'name',
    'unit',
    'unit_price',
    'quantity',
    'total_price',
];
```

These fields can be mass-assigned.

## Auto-Calculation Logic

The model automatically calculates `total_price` on save:

```php
protected static function boot()
{
    parent::boot();

    static::saving(function ($service) {
        if ($service->unit_price && $service->quantity) {
            $service->total_price = $service->unit_price * $service->quantity;
        }
    });
}
```

**Behavior:**
1. Before saving, checks if both `unit_price` and `quantity` are set
2. Calculates `total_price = unit_price × quantity`
3. Saves the calculated value

**Tech Debt:**
- **Bypass Risk**: Direct database updates can bypass this calculation
- **No Validation**: No check that values are positive
- **No Rounding**: No explicit rounding (relies on decimal cast)

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

```
1. Vendor updates service item
2. Model boot hook recalculates total_price
3. Model saves to database
4. Quotation.services_charge updated
```

### Deletion Flow

```
1. Service item deleted
2. Quotation.services_charge recalculated
3. Quotation.total_amount updated
```

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

### Current State

```php
// Class name (TYPO)
class QutationService extends Model
{
    // ...
}

// Table name (TYPO)
// qutation_services

// Relationship in Quotation model
public function quotationServices(): HasMany
{
    return $this->hasMany(QutationService::class);
}
```

### Recommended Fix

```php
// New class name
class QuotationServiceItem extends Model
{
    protected $table = 'quotation_service_items';
    // ...
}

// Migration to rename table
Schema::rename('qutation_services', 'quotation_service_items');

// Update Quotation model
public function quotationServiceItems(): HasMany
{
    return $this->hasMany(QuotationServiceItem::class);
}
```

### Refactoring Plan

1. Create new `QuotationServiceItem` model
2. Create migration to rename table
3. Update all references in codebase
4. Deprecate old `QutationService` class
5. Add tests for new model
6. Update documentation

## Cross-References

- [Quotation-Model](Quotation-Model.md) - Parent quotation for this service
- [QuotationService](QuotationService.md) - Business logic for quotation operations
- [QuotationsServiceResource](QuotationsServiceResource.md) - API resource for serialization

## Usage Examples

### Creating a service item

```php
$service = QutationService::create([
    'quotation_id' => $quotation->id,
    'name' => 'Installation Service',
    'unit' => 'hour',
    'unit_price' => 50.00,
    'quantity' => 10,
    // total_price calculated automatically: 500.00
]);
```

### Creating multiple service items

```php
$quotation->quotationServices()->createMany([
    [
        'name' => 'Installation Service',
        'unit' => 'hour',
        'unit_price' => 50.00,
        'quantity' => 10,
    ],
    [
        'name' => 'Maintenance Service',
        'unit' => 'month',
        'unit_price' => 100.00,
        'quantity' => 6,
    ],
]);
```

### Updating a service item

```php
$service->update([
    'unit_price' => 60.00,
    'quantity' => 8,
    // total_price recalculated: 480.00
]);
```

### Getting all services for a quotation

```php
$services = $quotation->quotationServices;

$totalServicesCharge = $services->sum('total_price');
```

### Calculating services charge for quotation

```php
$servicesCharge = $quotation->quotationServices->sum('total_price');

$quotation->update([
    'services_charge' => $servicesCharge,
    'total_amount' => $quotation->sub_amount + $servicesCharge + $quotation->tax_amount + $quotation->shipping_amount + $quotation->loading_charge,
]);
```

## Architecture Notes

### Why This Model Exists

The `QutationService` model serves several critical purposes:

1. **Itemized Breakdown**: Enables detailed cost breakdown
2. **Flexible Quoting**: Supports mixed product/service quotes
3. **Automatic Calculation**: Reduces manual calculation errors
4. **Audit Trail**: Tracks individual line items
5. **Reusability**: Can be used across different quotation types

### Relationship to Other Models

```
Quotation (parent)
    │
    └──> QutationService (line items)
            └──> total_price (auto-calculated)
```

### Future Enhancements

Potential improvements to this model:

1. **Fix naming typo**: Rename to `QuotationServiceItem`
2. **Add validation rules**: Ensure positive values
3. **Add database constraints**: Enforce calculation at DB level
4. **Add computed column**: Use PostgreSQL generated columns
5. **Add event listeners**: Trigger actions on changes
6. **Add scopes**: Filter by price ranges, types

## Database Improvements (PostgreSQL)

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

-- Add check constraint for calculation
ALTER TABLE quotation_service_items
  ADD CONSTRAINT chk_total_calculation
  CHECK (total_price = unit_price * quantity);
```

## Best Practices

### Always Use Auto-Calculation

```php
// Good - let model calculate
$service->update([
    'unit_price' => 50.00,
    'quantity' => 10,
]);

// Bad - manual calculation
$service->update([
    'unit_price' => 50.00,
    'quantity' => 10,
    'total_price' => 500.00, // Redundant and error-prone
]);
```

### Validate Before Creation

```php
$validated = Validator::make($data, [
    'name' => 'required|string|max:255',
    'unit' => 'required|string|max:50',
    'unit_price' => 'required|numeric|min:0',
    'quantity' => 'required|numeric|min:0',
]);

if ($validated->fails()) {
    return response()->json(['errors' => $validated->errors()], 422);
}

$service = QutationService::create($data);
```

### Use Transactions for Bulk Operations

```php
DB::transaction(function () use ($quotation, $servicesData) {
    foreach ($servicesData as $serviceData) {
        $quotation->quotationServices()->create($serviceData);
    }

    // Update quotation totals
    $servicesCharge = $quotation->quotationServices->sum('total_price');
    $quotation->update(['services_charge' => $servicesCharge]);
});
```
