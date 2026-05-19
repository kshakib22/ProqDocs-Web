---
name: quotation-model
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
- **Service breakdown**: Line items for complex quotes via [Quotation Service Model](/ProqDocs-Web/entities/quotation-service-model/)

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
| `services_charge` | decimal | Service fees | Total of QuotationService items |
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

**Note:** Uses [Quotation Service Model](/ProqDocs-Web/entities/quotation-service-model/) (note the typo `Qutation` in the class name).

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No check constraint on amounts | MEDIUM | Negative values possible | Add `CHECK (unit_price >= 0 AND total_amount >= 0)` |
| No unique constraint on quotation_number | MEDIUM | Duplicate numbers possible | Add unique index |
| No constraint on vendor-RFQ uniqueness | MEDIUM | Multiple quotes per vendor | Add unique index on (vendor_id, rfq_id) |
| Total calculation in service layer | MEDIUM | Inconsistency risk | Move to model or use computed column |
| `withTrashed()` on relationships | LOW | Orphaned data risk | Review and fix cascade behavior |
| No status transition validation | LOW | Invalid state transitions | Add validation rules |
| **Typo in Model Name** | **HIGH** | `QutationService` is missing the 'o'. | Rename to `QuotationServiceItem` (the model, not the service class). |

## Cross-References

- [Rfq Model](/ProqDocs-Web/entities/rfq-model/) - Parent RFQ for this quotation
- [Quotation Service Model](/ProqDocs-Web/entities/quotation-service-model/) - Line items/service breakdown
- [Quotation Service](/ProqDocs-Web/entities/quotation-service/) - Business logic for quotation operations
- [Quotation Controller](/ProqDocs-Web/entities/quotation-controller/) - HTTP endpoint handler
- [Quotation Resource](/ProqDocs-Web/entities/quotation-resource/) - API resource for serialization
- [Purchase List](/ProqDocs-Web/entities/purchase-list-domain/) - Downstream purchase order
