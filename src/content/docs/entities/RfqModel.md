---
name: Rfq-Model
description: Laravel Eloquent model for RFQ (Request for Quotation) - the central entity in the procurement workflow
type: entity
title: "Rfq Model"
---

# Rfq Model

## Architectural Purpose

`Rfq` (Request for Quotation) is the central entity in the procurement workflow. It represents a buyer's request for product quotes from vendors, serving as the foundation for the entire quotation and purchasing process. This model is the starting point for:

- **Vendor engagement**: Public and private RFQs for soliciting quotes
- **Price discovery**: Establishing market rates through competitive bidding
- **Procurement tracking**: Managing the lifecycle from request to purchase
- **Budget management**: Setting price range expectations
- **Project coordination**: Linking RFQs to specific projects and categories

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `rfq_code` | string | Unique identifier | Format: `RFQ-{type}-{uuid}` |
| `rfq_title` | string | Human-readable title | RFQ name |
| `type` | string | RFQ type | `public` or `private` |
| `status` | string | RFQ status | `in_review`, `active`, `accepted`, `rejected`, `cancelled` |
| `dead_line_date` | date | Submission deadline | Cast to date |
| `budget_min` | decimal | Minimum budget | Optional price range |
| `budget_max` | decimal | Maximum budget | Optional price range |
| `estimated_quantity` | decimal | Expected quantity | For planning purposes |
| `urgency` | string | Urgency level | `low`, `medium`, `high` |
| `buyer_id` | bigint | Foreign key | Links to `buyers` table |
| `vendor_id` | bigint | Foreign key | Links to `vendors` (private RFQs only) |
| `product_id` | bigint | Foreign key | Links to `products` table |
| `project_id` | bigint | Foreign key | Links to `projects` table |
| `category_id` | bigint | Foreign key | Links to `categories` table |
| `product_image` | string | Image path | Path to product image |
| `deleted_at` | timestamp | Soft delete timestamp | Laravel managed |

## Model Relationships

### `vendor(): BelongsTo`

```php
public function vendor(): BelongsTo
{
    return $this->belongsTo(Vendor::class);
}
```

- **Purpose:** Links to the vendor (for private RFQs only)
- **Cardinality:** Many-to-one
- **Usage:** Private RFQs are sent to specific vendors

### `buyer(): BelongsTo`

```php
public function buyer(): BelongsTo
{
    return $this->belongsTo(Buyer::class);
}
```

- **Purpose:** Links to the buyer who created the RFQ
- **Cardinality:** Many-to-one
- **Usage:** Ownership tracking and authorization

### `product(): BelongsTo`

```php
public function product(): BelongsTo
{
    return $this->belongsTo(Product::class);
}
```

- **Purpose:** Links to the product being requested
- **Cardinality:** Many-to-one
- **Usage:** Product specification and catalog data

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

### `documents(): MorphMany`

```php
public function documents(): MorphMany
{
    return $this->morphMany(Document::class, 'documentable');
}
```

- **Purpose:** Links to supporting documents
- **Cardinality:** One-to-many
- **Usage:** Attach specifications, drawings, requirements

### `quotations(): HasMany`

```php
public function quotations(): HasMany
{
    return $this->hasMany(Quotation::class);
}
```

- **Purpose:** Retrieves all vendor quotations for this RFQ
- **Cardinality:** One-to-many
- **Usage:** Primary access point for competitive bidding

### `purchaseList(): HasOne`

```php
public function purchaseList(): HasOne
{
    return $this->hasOne(PurchaseList::class);
}
```

- **Purpose:** Links to the purchase list generated from this RFQ
- **Cardinality:** One-to-one (or zero)
- **Usage:** Track conversion to purchase order

## Attribute Casts

### `dead_line_date` → Date

```php
protected $casts = [
    'dead_line_date' => 'date',
];
```

Stores deadline as date, automatically cast to/from Carbon instance.

## Accessors & Mutators

### `isPrivate` → Attribute

```php
protected function isPrivate(): Attribute
{
    return Attribute::make(
        get: fn ($value) => $this->type === 'private',
    );
}
```

**Purpose:** Returns true if RFQ type is 'private'.

**Usage:**
```php
if ($rfq->is_private) {
    // Private RFQ logic
}
```

### `isPublic` → Attribute

```php
protected function isPublic(): Attribute
{
    return Attribute::make(
        get: fn ($value) => $this->type === 'public',
    );
}
```

**Purpose:** Returns true if RFQ type is 'public'.

**Usage:**
```php
if ($rfq->is_public) {
    // Public RFQ logic
}
```

## Query Scopes

### `scopePublic($query)`

```php
public function scopePublic($query)
{
    return $query->where('type', 'public');
}
```

**Purpose:** Filter to public RFQs only.

**Usage:**
```php
$publicRfqs = Rfq::public()->get();
```

### `scopePrivate($query)`

```php
public function scopePrivate($query)
{
    return $query->where('type', 'private');
}
```

**Purpose:** Filter to private RFQs only.

**Usage:**
```php
$privateRfqs = Rfq::private()->get();
```

### `scopeActive($query)`

```php
public function scopeActive($query)
{
    return $query->whereDate('dead_line_date', '>=', today());
}
```

**Purpose:** Filter to RFQs with future deadlines.

**Usage:**
```php
$activeRfqs = Rfq::active()->get();
```

## Appended Attributes

```php
protected $appends = ['is_private', 'is_public'];
```

These accessors are automatically included in JSON serialization.

## Data Flow

### Creation Flow

```
1. Buyer creates RFQ via UI
2. RfqController validates input
3. RfqService::create() instantiates model
4. Model saves to database
5. Returns Rfq instance with ID
```

### Quotation Flow

```
1. Vendor views RFQ
2. Vendor submits quotation
3. Quotation created with rfq_id
4. RFQ status may update based on quotation acceptance
5. RFQ.quotations() returns all quotes
```

### Deletion Flow

```
1. Buyer deletes RFQ
2. Soft delete triggered (deleted_at set)
3. Related quotations remain (withTrashed needed to access)
4. Purchase list may be affected
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No check constraint on `dead_line_date` | MEDIUM | Invalid dates possible | Add `CHECK (dead_line_date >= created_at)` |
| No unique constraint on `rfq_code` | MEDIUM | Duplicate codes possible | Add unique index |
| No FK cascade for soft-deleted records | MEDIUM | Orphaned data | Add cascade handling |
| No status transition validation | LOW | Invalid state transitions | Add validation rules |
| Naming inconsistency with quantity | LOW | Confusion | Standardize on `quantity` |

## Cross-References

- [Quotation-Model](./Quotation-Model.md) - Vendor responses to this RFQ
- [RfqService](./RfqService.md) - Business logic for RFQ operations
- [RfqController](./RfqController.md) - HTTP endpoint handler
- [RfqResource](./RfqResource.md) - API resource for serialization
- PurchaseList - Downstream purchase order

## Usage Examples

### Creating a public RFQ

```php
$rfq = Rfq::create([
    'rfq_code' => 'RFQ-PUB-' . Str::uuid(),
    'rfq_title' => 'Steel Rebar for Foundation',
    'type' => 'public',
    'status' => 'active',
    'dead_line_date' => now()->addDays(7),
    'budget_min' => 10000,
    'budget_max' => 15000,
    'estimated_quantity' => 100,
    'urgency' => 'high',
    'buyer_id' => $buyer->id,
    'product_id' => $product->id,
    'project_id' => $project->id,
    'category_id' => $category->id,
]);
```

### Querying active public RFQs

```php
$activeRfqs = Rfq::public()
    ->active()
    ->with(['product', 'category', 'quotations'])
    ->get();
```

### Getting RFQ with all quotations

```php
$rfq = Rfq::with('quotations.vendor')->find($rfqId);

foreach ($rfq->quotations as $quotation) {
    // Process each vendor's quote
}
```

### Checking if RFQ is private

```php
if ($rfq->is_private) {
    // Private RFQ - only assigned vendor can see
}
```

### Soft deleting an RFQ

```php
$rfq->delete(); // Sets deleted_at timestamp

// Restore later
$rfq->restore();
```
