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

...

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

...

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

...

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

...

---

## See Also

- [QuotationService](/ProqDocs-Web/entities/quotation-service/) - Service line items
- Document Model: Supporting documents
- [RfqResource](/ProqDocs-Web/entities/rfq-resource/): Related RFQ API resource
- VendorResource: Related vendor API resource
