---
title: "QuotationResource"
---
# QuotationResource

**File**: `app/Http/Resources/QuotationResource.php`
**Type**: Laravel API Resource (JsonResource)
**Purpose**: Transforms Quotation model instances into API response format for buyers and vendors

---

## Overview

`QuotationResource` is the API transformation layer for the Quotation domain. It serializes vendor bid data for consumption by both buyers (who receive quotations) and vendors (who submit them). The resource implements conditional relationship loading, computed fields, and data visibility controls.

---

## OpenAPI Schema

The resource includes comprehensive Swagger/OpenAPI documentation (lines 10-112) defining the complete API contract:

### Core Properties

| Property | Type | Nullable | Description |
|----------|------|----------|-------------|
| `id` | integer | No | Primary key |
| `quotation_number` | string | No | Unique identifier (e.g., "QT-0001") |
| `quotation_date` | string (date) | No | Date quotation was created |
| `status` | string | No | Current status (e.g., "in_review") |
| `unit_price` | float | Yes | Price per unit |
| `total_amount` | float | Yes | Total including all charges |
| `tax_amount` | float | Yes | VAT/tax amount |
| `shipping_amount` | float | Yes | Shipping cost |
| `validity_period` | integer | Yes | Days until quotation expires |
| `created_at` | datetime | No | Timestamp created |
| `updated_at` | datetime | No | Timestamp last modified |

### Computed Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_valid` | boolean | Whether quotation is still within validity period |
| `days_until_expiry` | integer | Days remaining until expiry (0 if expired) |
| `subtotal` | float | Subtotal amount |

---

## Transformation Logic

### Direct Field Mapping (Lines 124-155)

```php
return [
    'id' => $this->id,
    'quotation_image' => $this->quotation_image ? url('storage/'.$this->quotation_image) : null,
    'is_custom' => $this->custom_name? true : false,
    'custom_name' => $this->custom_name,
    'category_id' => $this->category_id,
    // ... more fields
];
```

**Key behaviors**:
- **Image URLs**: Transforms storage paths to full URLs using `url('storage/...')`
- **Custom flag**: Derived from presence of `custom_name`
- **Date formatting**: All dates formatted as `Y-m-d H:i:s` or `Y-m-d`
- **Monetary rounding**: All currency values rounded to 2 decimal places using `round((float) $value, 2)`
- **Null safety**: Uses null coalescing and conditional checks throughout

### Duplicate `quotation_image` Handling

**Lines 125 and 141**: The resource defines `quotation_image` twice:
- Line 125: Simple URL transformation without existence check
- Line 141: URL transformation with `Storage::disk('public')->exists()` check

The second definition (line 141) takes precedence in the array, providing safer file existence validation.

---

## Relationship Serialization

### Conditional Loading Pattern

All relationships use `whenLoaded()` to prevent N+1 queries:

```php
'relationship' => $this->whenLoaded('relationship', function () {
    // Only included if relationship was eager-loaded
});
```

**Benefits**:
- Prevents N+1 query performance issues
- Allows controllers to selectively include relationships
- Returns `null` when relationship not loaded

### RFQ Relationship (Lines 158-175)

```php
'rfq' => $this->whenLoaded('rfq', function () {
    if (!$this->rfq) {
        return null;
    }
    return [
        'id' => $this->rfq->id,
        'rfq_code' => $this->rfq->rfq_code,
        'rfq_title' => $this->rfq->rfq_title,
        'description' => $this->rfq->description,
        'status' => $this->rfq->status,
        'type' => $this->rfq->type,
        'dead_line_date' => $this->rfq->dead_line_date,
        'estimated_quantity' => $this->rfq->estimated_quantity ? round((float) $this->rfq->estimated_quantity, 2) : null,
        'budget_min' => $this->rfq->budget_min ? round((float) $this->rfq->budget_min, 2) : null,
        'budget_max' => $this->rfq->budget_max ? round((float) $this->rfq->budget_max, 2) : null,
        'is_deleted' => $this->rfq->trashed(),
    ];
});
```

**Fields exposed**:
- RFQ identification (id, code, title)
- RFQ metadata (description, status, type, deadline)
- Budget information (min, max)
- Soft-delete status via `trashed()`

### Vendor Relationship (Lines 177-196)

```php
'vendor' => $this->whenLoaded('vendor', function () {
    if (!$this->vendor) {
        return null;
    }
    return [
        'id' => $this->vendor->id,
        'company_name' => $this->vendor->name,
        'user_id' => $this->vendor->user_id,
        'user' => $this->whenLoaded('vendor.user', function () {
            if (!$this->vendor->user) {
                return null;
            }
            return [
                'id' => $this->vendor->user->id,
                'name' => $this->vendor->user->name,
                'email' => $this->vendor->user->email,
            ];
        }),
    ];
});
```

**Nested relationship**: Includes `vendor.user` when loaded
**Fields exposed**: Company name, user ID, and user contact details

### Buyer Relationship (Lines 198-217)

```php
'buyer' => $this->whenLoaded('buyer', function () {
    if (!$this->buyer) {
        return null;
    }
    return [
        'id' => $this->buyer->id,
        'name' => $this->buyer->name,
        'user_id' => $this->buyer->user_id,
        'user' => $this->whenLoaded('buyer.user', function () {
            if (!$this->buyer->user) {
                return null;
            }
            return [
                'id' => $this->buyer->user->id,
                'name' => $this->buyer->user->name,
                'email' => $this->buyer->user->email,
            ];
        }),
    ];
});
```

**Nested relationship**: Includes `buyer.user` when loaded
**Fields exposed**: Buyer name, user ID, and user contact details

### Project Relationship (Lines 219-231)

```php
'project' => $this->whenLoaded('project', function () {
    if (!$this->project) {
        return null;
    }
    return [
        'id' => $this->project->id,
        'name' => $this->project->name,
        'description' => $this->project->description,
        'main_image' => $this->project->main_image && Storage::disk('public')->exists($this->project->main_image) ? url('storage/' . $this->project->main_image) : null,
        'status' => $this->project->status,
        'is_deleted' => $this->project->trashed(),
    ];
});
```

**Image handling**: Checks file existence before generating URL
**Soft-delete tracking**: Includes `is_deleted` flag

### Product Relationship (Lines 233-247)

```php
'product' => $this->whenLoaded('product', function () {
    if (!$this->product) {
        return null;
    }
    return [
        'id' => $this->product->id,
        'name' => $this->product->name,
        'unit' => $this->product->unit,
        'description' => $this->product->description,
        'unit_price' => $this->product->unit_price ? round((float) $this->product->unit_price, 2) : null,
        'base_price' => $this->product->base_price ? round((float) $this->product->base_price, 2) : null,
        'product_code' => $this->product->product_code,
        'is_deleted' => $this->product->trashed(),
    ];
});
```

**Pricing data**: Exposes both `unit_price` and `base_price` for comparison

### Documents Collection (Lines 249-263)

```php
'documents' => $this->whenLoaded('documents', function () {
    return $this->documents->map(function ($document) {
        return [
            'id' => $document->id,
            'name' => $document->name,
            'file_path' => $document->file_path && Storage::disk('public')->exists($document->file_path) ? url('storage/'.$document->file_path) : null,
            'file_size' => $document->file_size,
            'mime_type' => $document->mime_type,
            'created_at' => $document->created_at?->format('Y-m-d H:i:s'),
        ];
    });
}),
'documents_count' => $this->whenLoaded('documents', function () {
    return $this->documents->count();
}),
```

**N+1 Risk**: ⚠️ **HIGH** - The `map()` function iterates over all documents without eager-loading nested data. Each document's `created_at` is formatted, but no additional queries are triggered.

**File existence check**: Each document's file path is validated before URL generation

### Quotation Services Collection (Lines 265-276)

```php
'quotation_services' => $this->whenLoaded('quotationServices', function () {
    return $this->quotationServices->map(function ($service) {
        return [
            'id' => $service->id,
            'name' => $service->name,
            'unit' => $service->unit,
            'unit_price' => $service->unit_price ? round((float) $service->unit_price, 2) : null,
            'quantity' => $service->quantity ? round((float) $service->quantity, 2) : null,
            'total_price' => $service->total_price ? round((float) $service->total_price, 2) : null,
        ];
    });
}),
```

**N+1 Risk**: ⚠️ **LOW** - No nested relationships accessed, only direct property access

**Note**: The relationship name in the model is `quotationServices` (camelCase) but the API property is `quotation_services` (snake_case).

---

## Computed Fields

### Services Charge (Line 147)

```php
'services_charge' => $this->quotationServices?->sum('total_price') ? round((float) $this->quotationServices->sum('total_price'), 2) : 0,
```

**N+1 Risk**: ⚠️ **HIGH** - Accesses `quotationServices` relationship without `whenLoaded()` check. This will trigger a lazy load if the relationship is not eager-loaded.

**Behavior**: Sums all service total prices and rounds to 2 decimal places

### Validity Check (Lines 279-282)

```php
'is_valid' => $this->when($this->validity_period && $this->quotation_date, function () {
    $expiryDate = \Carbon\Carbon::parse($this->quotation_date)->addDays($this->validity_period);
    return \Carbon\Carbon::now()->isBefore($expiryDate);
}),
```

**Logic**: Only included when both `validity_period` and `quotation_date` exist. Returns `true` if current date is before expiry date.

### Days Until Expiry (Lines 284-288)

```php
'days_until_expiry' => $this->when($this->validity_period && $this->quotation_date, function () {
    $expiryDate = \Carbon\Carbon::parse($this->quotation_date)->addDays($this->validity_period);
    $now = \Carbon\Carbon::now();
    return $expiryDate->isFuture() ? $now->diffInDays($expiryDate) : 0;
}),
```

**Logic**: Returns days remaining until expiry, or `0` if already expired.

---

## Data Visibility Rules

### Vendor Price Privacy

**Current Implementation**: ⚠️ **NO EXPLICIT VENDOR ISOLATION**

The resource does NOT implement vendor-specific data visibility rules. All quotations returned include full pricing data regardless of which vendor is viewing the response.

**Expected Behavior** (not implemented):
- Vendors should only see their own quotations
- Vendors should NOT see other vendors' prices
- Buyers should see all quotations for comparison

**Current Risk**: If a vendor endpoint returns a collection of quotations, they could potentially see competitors' pricing.

### Soft-Delete Visibility

The resource tracks soft-deleted related entities using `trashed()`:
- `category.is_deleted` (line 136)
- `rfq.is_deleted` (line 173)
- `project.is_deleted` (line 229)
- `product.is_deleted` (line 245)

This allows frontend to display deleted status while maintaining referential integrity.

---

## N+1 Query Analysis

### High Risk Areas

| Location | Risk | Mitigation |
|----------|------|------------|
| Line 147 (`services_charge`) | HIGH | Accesses `quotationServices` without `whenLoaded()` check |
| Lines 249-260 (`documents`) | MEDIUM | Uses `map()` but no nested relationships accessed |

### Safe Areas

All relationship serializations use `whenLoaded()`:
- `rfq` (line 158)
- `vendor` (line 177)
- `buyer` (line 198)
- `project` (line 219)
- `product` (line 233)
- `documents` (line 249)
- `quotationServices` (line 265)

### Recommended Controller Eager-Loading

```php
// For full quotation details
Quotation::with([
    'rfq',
    'vendor.user',
    'buyer.user',
    'project',
    'product',
    'documents',
    'quotationServices',
    'category'
])->find($id);

// For listing (minimal)
Quotation::with(['vendor', 'rfq'])->get();
```

---

## File Storage Handling

### Storage Disk

All file operations use `Storage::disk('public')`:
- Quotation images (lines 125, 141)
- Project images (line 227)
- Document files (line 254)

### URL Generation Pattern

```php
url('storage/' . $file_path)
```

This assumes the public disk is symlinked to `public/storage` via:
```bash
php artisan storage:link
```

### Existence Validation

Before generating URLs, the resource checks file existence:
```php
Storage::disk('public')->exists($file_path)
```

This prevents broken links when files are deleted or moved.

---

## Monetary Value Handling

### Rounding Strategy

All monetary values are rounded to 2 decimal places:
```php
round((float) $value, 2)
```

**Fields rounded**:
- `unit_price` (line 145)
- `sub_amount` (line 146)
- `services_charge` (line 147)
- `total_amount` (line 148)
- `vat_rate` (line 149)
- `tax_amount` (line 150)
- `shipping_amount` (line 151)
- `loading_charge` (line 152)
- `subtotal` (line 290)

### Null Handling

Monetary fields default to `0` when null:
```php
$this->unit_price ? round((float) $this->unit_price, 2) : 0
```

---

## Category Handling (Lines 129-138)

```php
'category' => $this->whenLoaded('category', function () {
    if (!$this->category) {
        return null;
    }
    return [
        'id' => $this->category->id,
        'name' => $this->category->name,
        'is_deleted' => $this->category->trashed(),
    ];
}),
```

**Note**: The `category_id` is always exposed (line 128), but the full category object is only included when loaded.

---

## Unit Handling (Line 144)

```php
'unit' => $this->unit ?? $this->product?->unit ?? null,
```

**Fallback chain**:
1. Use quotation's `unit` if present
2. Fall back to product's `unit` if quotation has no unit
3. Return `null` if neither exists

---

## Dependencies

### Laravel Framework

- `Illuminate\Http\Request`
- `Illuminate\Http\Resources\Json\JsonResource`
- `Illuminate\Support\Facades\Storage`

### Carbon

Used for date calculations in computed fields:
- `\Carbon\Carbon::parse()`
- `\Carbon\Carbon::now()`
- `isBefore()`, `isFuture()`, `diffInDays()`

---

## Usage Examples

### Controller Usage

```php
// Single quotation with all relationships
$quotation = Quotation::with([
    'rfq',
    'vendor.user',
    'buyer.user',
    'project',
    'product',
    'documents',
    'quotationServices',
    'category'
])->findOrFail($id);

return new QuotationResource($quotation);

// Collection of quotations
$quotations = Quotation::with(['vendor', 'rfq'])->get();
return QuotationResource::collection($quotations);
```

### API Response Structure

```json
{
  "data": {
    "id": 1,
    "quotation_number": "QT-0001",
    "quotation_date": "2025-01-15",
    "status": "in_review",
    "unit_price": 1200.50,
    "total_amount": 15000.75,
    "tax_amount": 500.00,
    "shipping_amount": 150.00,
    "validity_period": 30,
    "is_valid": true,
    "days_until_expiry": 12,
    "subtotal": 24000.00,
    "rfq": {
      "id": 5,
      "rfq_code": "RFQ-2025-0005",
      "rfq_title": "Office workstation purchase",
      "is_deleted": false
    },
    "vendor": {
      "id": 3,
      "company_name": "ABC Supplies Ltd.",
      "user_id": 15
    },
    "documents": [...],
    "quotation_services": [...]
  }
}
```

---

## Security Considerations

### Data Exposure

1. **Vendor Pricing**: No vendor isolation - all pricing visible to all users
2. **User Emails**: Vendor and buyer user emails are exposed (lines 192, 213)
3. **Budget Information**: RFQ budget ranges are exposed (lines 171-172)

### Recommendations

1. Implement vendor-specific filtering in controllers
2. Consider redacting sensitive fields based on user role
3. Add authorization checks before returning quotations

---

## Related Entities

| Entity | Relationship | Purpose |
|--------|--------------|---------|
| `Quotation` | Self | The model being transformed |
| `Rfq` | BelongsTo | The RFQ this quotation responds to |
| `Vendor` | BelongsTo | The vendor who submitted the quotation |
| `Buyer` | BelongsTo | The buyer who receives the quotation |
| `Project` | BelongsTo | The project associated with the quotation |
| `Product` | BelongsTo | The product being quoted |
| `Category` | BelongsTo | The category of the quotation |
| `Document` | HasMany | Supporting documents |
| `QuotationService` | HasMany | Additional services quoted |

---

## OpenAPI Compliance

The resource includes comprehensive OpenAPI 3.0 schema documentation (lines 10-112) covering:
- All direct properties
- All relationship objects
- Array types for collections
- Nullable fields
- Example values for all properties

This enables automatic API documentation generation via tools like Swagger UI or Postman.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Initial | Initial implementation with full relationship support |

---

## See Also

- [QuotationService](./QuotationService.md) - Service line items
- Document Model: Supporting documents
- [RfqResource](./RfqResource.md): Related RFQ API resource
- VendorResource: Related vendor API resource
