---
name: BoqEntry-Model
description: Laravel Eloquent model for BOQ (Bill of Quantities) entries - individual line items within a BOQ sheet
type: entity
title: "BoqEntry Model"
---

# BoqEntry Model

## Architectural Purpose

`BoqEntry` represents a single line item within a BOQ (Bill of Quantities) sheet. Each entry contains the detailed information for a specific material, labor, or equipment item, including:

- **Product identification**: Links to Product, RFQ, and Quotation
- **Pricing data**: Unit price, quantity, taxes, shipping, and totals
- **Dynamic values**: Custom fields defined by the parent sheet's `extra_columns`
- **Styling metadata**: Cell colors and merged cell configurations

This model is the atomic unit of the BOQ domain, serving as the bridge between static quantity sheets and dynamic procurement workflows (RFQs, quotations, purchase lists).

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `boq_sheet_id` | bigint | Foreign key | Links to `boq_sheets`, cascade delete |
| `product_id` | bigint | Foreign key | Links to `products`, set null on delete |
| `quotation_id` | bigint | Foreign key | Links to `quotations`, set null on delete |
| `rfq_id` | bigint | Foreign key | Links to `rfqs`, set null on delete |
| `vendor_id` | bigint | Foreign key | Links to `vendors`, set null on delete |
| `buyer_id` | bigint | Foreign key | Links to `buyers`, cascade delete |
| `project_id` | bigint | Foreign key | Links to `projects`, cascade delete |
| `user_id` | bigint | Foreign key | Links to `users`, cascade delete |
| `rfq_code` | string | RFQ identifier | Optional, for tracking |
| `item_name` | string | Item description | Human-readable name |
| `image` | string | Image path | Path to product image |
| `unit` | string | Unit of measure | Max 20 chars (e.g., "kg", "m", "pcs") |
| `unit_price` | decimal | Price per unit | 10,2 precision, default 0 |
| `quantity` | decimal | Quantity needed | 10,2 precision, default 0 |
| `amount` | decimal | Line amount | quantity × unit_price, 10,2 |
| `vat_tax` | decimal | VAT amount | 10,2 precision, default 0 |
| `total` | decimal | Line total | amount + vat_tax, 10,2 |
| `tax_amount` | decimal | Additional tax | 10,2 precision, default 0 |
| `shipping_amount` | decimal | Shipping cost | 10,2 precision, default 0 |
| `loading_charge` | decimal | Loading fee | 10,2 precision, default 0 |
| `services_charge` | decimal | Services fee | 10,2 precision, default 0 |
| `total_amount` | decimal | Grand total | Sum of all charges, 10,2 |
| `discount_amount` | decimal | Discount | 10,2 precision, default 0 |
| `dynamic_values` | json | Custom fields | Keyed by sheet's extra_columns |
| `cell_colors` | json | Cell styling | Color mappings for dynamic columns |
| `merged_cells` | json | Cell merge config | Merged cell definitions |
| `entry_order` | int | Display order | Default 1, for UI sorting |
| `created_at` | timestamp | Creation time | Laravel managed |
| `updated_at` | timestamp | Last update | Laravel managed |

### Schema Bug: `unsigendInteger` Typo

**CRITICAL BUG:** The migration contains a typo:

```php
// Migration (line 52)
$table->unsigendInteger('entry_order')->default(1);
// Should be: unsignedInteger
```

**Impact:**
- This will cause a migration failure
- The `entry_order` column will not be created
- All entries will default to order 1

**Recommended Fix:** Create a new migration to fix the typo:
```php
$table->unsignedInteger('entry_order')->default(1)->change();
```

## Model Relationships

### `boqSheet(): BelongsTo`

```php
public function boqSheet(): BelongsTo
{
    return $this->belongsTo(BoqSheet::class);
}
```

- **Purpose:** Links the entry to its parent BOQ sheet
- **Cardinality:** Many-to-one (many entries per sheet)
- **Cascade:** Database-level `onDelete('cascade')`
- **Usage:** Primary navigation to access sheet metadata and `extra_columns`

### `product(): BelongsTo`

```php
public function product(): BelongsTo
{
    return $this->belongsTo(Product::class);
}
```

- **Purpose:** Links to the product catalog
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('set null')` - entry persists if product deleted
- **Usage:** Access product specifications, images, and inventory data

### `quotation(): BelongsTo`

```php
public function quotation(): BelongsTo
{
    return $this->belongsTo(Quotation::class);
}
```

- **Purpose:** Links to vendor quotation for this item
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('set null')`
- **Usage:** Track quoted prices and vendor responses

### `rfq(): BelongsTo`

```php
public function rfq(): BelongsTo
{
    return $this->belongsTo(Rfq::class);
}
```

- **Purpose:** Links to the Request for Quotation
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('set null')`
- **Usage:** Track which RFQ this entry originated from

### `vendor(): BelongsTo`

```php
public function vendor(): BelongsTo
{
    return $this->belongsTo(Vendor::class);
}
```

- **Purpose:** Links to the preferred vendor
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('set null')`
- **Usage:** Track vendor assignment and contact info

### `user(): BelongsTo`

```php
public function user(): BelongsTo
{
    return $this->belongsTo(User::class);
}
```

- **Purpose:** Links to the user who created/modified the entry
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('cascade')`
- **Usage:** Audit trail and ownership tracking

### `buyer(): BelongsTo`

```php
public function buyer(): BelongsTo
{
    return $this->belongsTo(Buyer::class);
}
```

- **Purpose:** Links to the buyer responsible for this entry
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('cascade')`
- **Usage:** Track buyer assignment and responsibility

### `project(): BelongsTo`

```php
public function project(): BelongsTo
{
    return $this->belongsTo(Project::class);
}
```

- **Purpose:** Links to the parent project
- **Cardinality:** Many-to-one
- **Cascade:** `onDelete('cascade')`
- **Usage:** Project scoping and reporting

### `purchaseList(): HasOne`

```php
public function purchaseList(): HasOne
{
    return $this->hasOne(PurchaseList::class);
}
```

- **Purpose:** Links to the purchase list item generated from this entry
- **Cardinality:** One-to-one (or zero)
- **Usage:** Track conversion from BOQ to purchase order

## Attribute Casts

### Decimal Casts

All monetary and quantity fields are cast to decimal with 2 decimal places:

```php
protected $casts = [
    'quantity' => 'decimal:2',
    'unit_price' => 'decimal:2',
    'amount' => 'decimal:2',
    'vat_tax' => 'decimal:2',
    'total' => 'decimal:2',
    'tax_amount' => 'decimal:2',
    'shipping_amount' => 'decimal:2',
    'loading_charge' => 'decimal:2',
    'services_charge' => 'decimal:2',
    'total_amount' => 'decimal:2',
    'discount_amount' => 'decimal:2',
];
```

**Purpose:** Ensures consistent precision for financial calculations.

### JSON Casts

```php
protected $casts = [
    'dynamic_values' => 'array',
    'cell_colors' => 'array',
    'merged_cells' => 'array',
];
```

#### `dynamic_values` → Array

Stores values for dynamic columns defined in the parent sheet's `extra_columns`.

**Expected Structure:**
```json
{
  "item_code": "CON-001",
  "specification": "Grade A concrete",
  "manufacturer": "ABC Corp"
}
```

**Relationship to Parent Sheet:**
- Keys must match `boqSheet.extra_columns_array`
- Values are stored as strings (no type safety)
- Missing keys are treated as null

#### `cell_colors` → Array

Stores color mappings for dynamic columns only.

**Expected Structure:**
```json
{
  "item_code": "#FF0000",
  "specification": "#00FF00"
}
```

**Note:** Only applies to dynamic columns, not fixed columns like `item_name` or `unit_price`.

#### `merged_cells` → Array

Stores merged cell configurations for dynamic columns.

**Expected Structure (Simple):**
```json
["column1", "column2"]
```

**Expected Structure (Advanced):**
```json
[
  {
    "column": "column1",
    "rowspan": 2,
    "colspan": 1
  }
]
```

## Pricing Calculation Logic

The model stores multiple pricing fields that represent different stages of the procurement lifecycle:

### Base Calculation

```
amount = quantity × unit_price
total = amount + vat_tax
```

### Extended Calculation

```
total_amount = total + tax_amount + shipping_amount + loading_charge + services_charge - discount_amount
```

**Note:** These calculations are **not** performed in the model. They must be handled in the service layer or controller.

## Data Flow

### Creation Flow

```
1. User adds new entry to BOQ sheet
2. BoqEntryController validates input
3. BoqEntryService::create() instantiates model
4. Model saves to database
5. Returns BoqEntry instance with ID
```

### Dynamic Value Flow

```
1. BoqSheet defines extra_columns: ["item_code", "specification"]
2. User creates entry with dynamic_values: {"item_code": "CON-001", "specification": "Grade A"}
3. Model stores as JSON in database
4. On retrieval, JSON cast returns array
5. UI renders dynamic columns using parent sheet's extra_columns as keys
```

### Deletion Flow

```
1. User deletes entry (or parent sheet)
2. Database cascade deletes entry (if sheet deleted)
3. Related records (product, quotation, etc.) set to null or cascade
4. Transaction commits
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| `unsigendInteger` typo | HIGH | Migration failure, no ordering | Create fix migration |
| No calculation logic in model | MEDIUM | Inconsistent totals | Add computed properties or service |
| `dynamic_values` no type safety | MEDIUM | Data quality issues | Add validation or schema |
| No indexes on foreign keys | LOW | Query performance | Add composite indexes |
| No validation on JSON fields | LOW | Potential corruption | Add validation rules |

## Cross-References

- [BoqSheet-Model](/entities/boqsheet-model) - Parent sheet containing this entry
- [BoqSheetService](/entities/boqsheetservice) - Business logic for entry operations
- [BoqEntryController](/entities/boqentrycontroller) - HTTP endpoint handler
- PurchaseList - Downstream purchase order item
- [BoqEntry-BoqSheet-Domain](/entities/boqentry-boqsheet-domain) - Domain overview

## Usage Examples

### Creating a new entry

```php
$entry = BoqEntry::create([
    'boq_sheet_id' => $sheet->id,
    'product_id' => $product->id,
    'rfq_code' => 'RFQ-2024-001',
    'item_name' => 'Portland Cement',
    'unit' => 'kg',
    'unit_price' => 15.50,
    'quantity' => 1000,
    'dynamic_values' => [
        'item_code' => 'MAT-001',
        'specification' => 'Grade 42.5'
    ],
    'cell_colors' => [
        'item_code' => '#FF0000'
    ]
]);
```

### Loading entry with relationships

```php
$entry = BoqEntry::with(['boqSheet', 'product', 'quotation', 'vendor'])
    ->find($id);
```

### Calculating totals

```php
$entry->amount = $entry->quantity * $entry->unit_price;
$entry->total = $entry->amount + $entry->vat_tax;
$entry->total_amount = $entry->total + $entry->shipping_amount + $entry->loading_charge;
$entry->save();
```

### Querying by sheet with dynamic values

```php
$entries = BoqEntry::where('boq_sheet_id', $sheetId)
    ->orderBy('entry_order')
    ->get();

foreach ($entries as $entry) {
    $dynamicValue = $entry->dynamic_values['item_code'] ?? null;
}
```

### Updating cell colors

```php
$entry->cell_colors = [
    'specification' => '#FFFF00',
    'manufacturer' => '#00FFFF'
];
$entry->save();
```
