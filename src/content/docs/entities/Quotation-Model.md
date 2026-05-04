---
name: Quotation-Model
description: Laravel Eloquent model for Quotation - represents a vendor's response to an RFQ with pricing details and terms
type: entity
title: "Quotation Model"
---

# Quotation Model

## Architectural Purpose

`Quotation` represents a vendor's response to an RFQ (Request for Quotation). It contains pricing details, terms, and supporting documents, serving as the bridge between the RFQ and the final purchase order. This model is critical for:

- **Competitive bidding**: Multiple vendors can quote on the same RFQ
- **Price negotiation**: Detailed breakdown of costs
- **Vendor selection**: Buyer can compare and select the best quote
- **Purchase order generation**: Accepted quotations become purchase orders
- **Service breakdown**: Line items for complex quotes via [QutationService-Model](QutationService-Model.md)

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `quotation_number` | string | Unique identifier | Format: `QT-{rfq_id}-{random}` |
| `rfq_id` | bigint | Foreign key | Links to `rfqs` table |
| `vendor_id` | bigint | Foreign key | Links to `vendors` table |
| `buyer_id` | bigint | Foreign key | Links to `buyers` table |
| `user_id` | bigint | Foreign key | Links to `users` table |
| `project_id` | bigint | Foreign key | Links to `projects` table |
| `product_id` | bigint | Foreign key | Links to `products` table |
| `category_id` | bigint | Foreign key | Links to `categories` table |
| `status` | string | Quotation status | `in_review`, `accepted`, `rejected` |
| `unit_count` | decimal | Quantity being quoted | Number of units |
| `unit_price` | decimal | Price per unit | Base price |
| `sub_amount` | decimal | Subtotal | unit_count × unit_price |
| `services_charge` | decimal | Service fees | Total of QutationService items |
| `total_amount` | decimal | Final total | Sum of all charges |
| `vat_rate` | decimal | VAT percentage | Tax rate |
| `tax_amount` | decimal | Calculated tax | Based on vat_rate |
| `shipping_amount` | decimal | Shipping cost | Delivery charges |
| `loading_charge` | decimal | Loading fee | Handling charges |
| `validity_period` | integer | Days until expiry | Quotation validity |
| `quotation_date` | date | Issue date | Date quotation was created |
| `quotation_image` | string | Image path | Path to product image |
| `custom_name` | string | Custom product name | Override for product name |
| `deleted_at` | timestamp | Soft delete timestamp | Laravel managed |

## Model Relationships

### `rfq(): BelongsTo`

```php
public function rfq(): BelongsTo
{
    return $this->belongsTo(Rfq::class);
}
```

- **Purpose:** Links to the parent RFQ
- **Cardinality:** Many-to-one
- **Usage:** Access RFQ details and requirements

**Note:** Should use `withTrashed()` to handle soft-deleted RFQs.

### `vendor(): BelongsTo`

```php
public function vendor(): BelongsTo
{
    return $this->belongsTo(Vendor::class);
}
```

- **Purpose:** Links to the vendor submitting the quote
- **Cardinality:** Many-to-one
- **Usage:** Vendor identification and contact info

### `buyer(): BelongsTo`

```php
public function buyer(): BelongsTo
{
    return $this->belongsTo(Buyer::class);
}
```

- **Purpose:** Links to the buyer receiving the quote
- **Cardinality:** Many-to-one
- **Usage:** Buyer ownership and authorization

### `user(): BelongsTo`

```php
public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}
```

- **Purpose:** Links to the user who created the quote
- **Cardinality:** Many-to-one
- **Usage:** Audit trail and ownership

### `project(): BelongsTo`

```php
public function project(): BelongsTo
{
    return $this->belongsTo(Project::class);
}
```

- **Purpose:** Links to the parent project
- **Cardinality:** Many-to-one
- **Usage:** Project scoping and reporting

**Note:** Should use `withTrashed()` to handle soft-deleted projects.

### `product(): BelongsTo`

```php
public function product(): BelongsTo
{
    return $this->belongsTo(Product::class);
}
```

- **Purpose:** Links to the product being quoted
- **Cardinality:** Many-to-one
- **Usage:** Product specification and catalog data

**Note:** Should use `withTrashed()` to handle soft-deleted products.

### `category(): BelongsTo`

```php
public function category(): BelongsTo
{
    return $this->belongsTo(Category::class);
}
```

- **Purpose:** Links to the product category
- **Cardinality:** Many-to-one
- **Usage:** Categorization and filtering

**Note:** Should use `withTrashed()` to handle soft-deleted categories.

### `documents(): MorphMany`

```php
public function documents(): MorphMany
{
    return $this->morphMany(Document::class, 'documentable');
}
```

- **Purpose:** Links to supporting documents
- **Cardinality:** One-to-many
- **Usage:** Attach specifications, certificates, terms

### `quotationServices(): HasMany`

```php
public function quotationServices(): HasMany
{
    return $this->hasMany(QutationService::class);
}
```

- **Purpose:** Links to line items/service breakdown
- **Cardinality:** One-to-many
- **Usage:** Detailed cost breakdown for complex quotes

**Note:** Uses [QutationService-Model](QutationService-Model.md) (note the typo in class name).

## Total Calculation Formula

The `total_amount` is calculated as:

```
total_amount = sub_amount + services_charge + tax_amount + shipping_amount + loading_charge
```

**Where:**
- `sub_amount = unit_count × unit_price`
- `services_charge = sum of all QutationService.total_price`
- `tax_amount = calculated based on vat_rate`
- `shipping_amount = delivery charges`
- `loading_charge = handling charges`

**Tech Debt:** This calculation is performed in the service layer, not in the model, which can lead to inconsistency.

## Data Flow

### Creation Flow

```
1. Vendor views RFQ
2. Vendor submits quotation via UI
3. QuotationController validates input
4. QuotationService::create() instantiates model
5. Model saves to database
6. Returns Quotation instance with ID
7. Notification sent to buyer
```

### Acceptance Flow

```
1. Buyer reviews quotation
2. Buyer accepts quotation
3. Quotation status set to 'accepted'
4. Competing quotations set to 'rejected'
5. RFQ status set to 'accepted'
6. Purchase list created
7. Purchase order generated
```

### Rejection Flow

```
1. Buyer rejects quotation
2. Quotation status set to 'rejected'
3. No purchase order created
4. RFQ remains open for other quotes
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No check constraint on amounts | MEDIUM | Negative values possible | Add `CHECK (unit_price >= 0 AND total_amount >= 0)` |
| No unique constraint on quotation_number | MEDIUM | Duplicate numbers possible | Add unique index |
| No constraint on vendor-RFQ uniqueness | MEDIUM | Multiple quotes per vendor | Add unique index on (vendor_id, rfq_id) |
| Total calculation in service layer | MEDIUM | Inconsistency risk | Move to model or use computed column |
| `withTrashed()` on relationships | LOW | Orphaned data risk | Review and fix cascade behavior |
| No status transition validation | LOW | Invalid state transitions | Add validation rules |

## Cross-References

- [Rfq-Model](Rfq-Model.md) - Parent RFQ for this quotation
- [QutationService-Model](QutationService-Model.md) - Line items/service breakdown
- [QuotationService](QuotationService.md) - Business logic for quotation operations
- [QuotationController](QuotationController.md) - HTTP endpoint handler
- [QuotationResource](QuotationResource.md) - API resource for serialization
- [[PurchaseList]] - Downstream purchase order

## Usage Examples

### Creating a quotation

```php
$quotation = Quotation::create([
    'quotation_number' => 'QT-' . $rfq->id . '-' . Str::random(6),
    'rfq_id' => $rfq->id,
    'vendor_id' => $vendor->id,
    'buyer_id' => $buyer->id,
    'user_id' => $user->id,
    'project_id' => $project->id,
    'product_id' => $product->id,
    'category_id' => $category->id,
    'status' => 'in_review',
    'unit_count' => 100,
    'unit_price' => 150.00,
    'sub_amount' => 15000.00,
    'services_charge' => 500.00,
    'total_amount' => 15500.00,
    'vat_rate' => 15.00,
    'tax_amount' => 2325.00,
    'shipping_amount' => 0.00,
    'loading_charge' => 0.00,
    'validity_period' => 30,
    'quotation_date' => now(),
]);
```

### Getting RFQ with all quotations

```php
$rfq = Rfq::with('quotations.vendor')->find($rfqId);

foreach ($rfq->quotations as $quotation) {
    echo "Vendor: {$quotation->vendor->name}, Price: {$quotation->total_amount}";
}
```

### Adding service line items

```php
$quotation->quotationServices()->create([
    'name' => 'Installation Service',
    'unit' => 'hour',
    'unit_price' => 50.00,
    'quantity' => 10,
    // total_price calculated automatically
]);
```

### Accepting a quotation

```php
$quotation->update(['status' => 'accepted']);

// Reject competing quotations
$rfq->quotations()
    ->where('id', '!=', $quotation->id)
    ->update(['status' => 'rejected']);

// Update RFQ status
$rfq->update(['status' => 'accepted']);
```

### Checking quotation validity

```php
$expiryDate = $quotation->quotation_date->addDays($quotation->validity_period);

if (now()->gt($expiryDate)) {
    // Quotation has expired
}
```

## Architecture Notes

### Why This Model Exists

The `Quotation` model serves several critical purposes:

1. **Vendor Response**: Captures vendor pricing and terms
2. **Competitive Bidding**: Enables comparison of multiple quotes
3. **Purchase Order Foundation**: Accepted quotes become purchase orders
4. **Audit Trail**: Tracks vendor engagement history
5. **Service Breakdown**: Supports complex quotes with line items

### Relationship to Other Models

```
Rfq (parent)
    │
    └──> Quotation (vendor response)
            ├──> QutationService (line items)
            ├──> Vendor (submitting vendor)
            ├──> Product (quoted product)
            └──> PurchaseList (downstream order)
```

### Future Enhancements

Potential improvements to this model:

1. **Add `calculateTotal()` method**: Encapsulate pricing logic
2. **Add status transition validation**: Prevent invalid state changes
3. **Add `isExpired()` accessor**: Check if quotation is still valid
4. **Add event listeners**: Trigger actions on status changes
5. **Add computed column**: For total_amount calculation
6. **Fix `withTrashed()` usage**: Review and fix cascade behavior
