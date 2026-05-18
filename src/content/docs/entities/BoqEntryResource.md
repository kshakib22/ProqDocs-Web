---
name: BoqEntryResource
description: Laravel API resource for BOQ (Bill of Quantities) entry transformation - handles serialization of entry data for API responses
type: entity
title: "BoqEntryResource"
---

# BoqEntryResource

## Architectural Purpose

`BoqEntryResource` is the API transformation layer for BOQ entry data. This resource is responsible for:

- **Data serialization**: Converting BoqEntry models to API-ready JSON
- **Data transformation**: Converting internal data formats to frontend-friendly formats
- **Image handling**: Processing and formatting image URLs
- **Relationship loading**: Efficiently loading related data
- **Merge integration**: Including merge configuration data
- **Dynamic column handling**: Transforming extra columns for frontend consumption

This resource ensures that the API returns consistent, well-formatted entry data to the frontend, abstracting away database-specific details.

## Resource Dependencies

```php
use App\Models\BoqSheetMerge;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Support\Facades\Storage;
```

- **JsonResource**: Base Laravel resource class
- **Request**: HTTP request for conditional data inclusion
- **Storage**: File storage for image handling
- **BoqSheetMerge**: Model for merge configuration queries

## Resource Structure

### `toArray(Request $request): array`

**Purpose:** Transform the resource into an array for JSON response.

**Behavior:**
1. Gets extra columns from parent sheet
2. Processes image URL (handles both URLs and storage paths)
3. Rounds all monetary values to 2 decimal places
4. Includes dynamic values and cell colors
5. Calculates merged field names from merge configurations
6. Includes related data when loaded
7. Returns formatted array

**Response Structure:**
```json
{
  "id": 1,
  "boq_sheet_id": 1,
  "rfq_code": "RFQ-001",
  "item_name": "Portland Cement",
  "vendor_name": "ABC Corp",
  "vat_rate": 15.00,
  "image": "https://example.com/storage/products/cement.jpg",
  "unit": "kg",
  "unit_price": 15.50,
  "quantity": 1000.00,
  "amount": 15500.00,
  "vat_tax": 2325.00,
  "total": 17825.00,
  "tax_amount": 0.00,
  "shipping_amount": 0.00,
  "loading_charge": 0.00,
  "services_charge": 0.00,
  "total_amount": 17825.00,
  "discount_amount": 0.00,
  "dynamic_values": {
    "item_code": "MAT-001",
    "specification": "Grade 42.5"
  },
  "cell_colors": {
    "item_code": "#FF0000",
    "specification": "#00FF00"
  },
  "merged_cells": ["item_code", "specification"],
  "extra_columns": ["item_code", "specification", "unit"],
  "project_id": 1,
  "product_id": 10,
  "quotation_id": 5,
  "quotation": { /* QuotationResource */ },
  "rfq_id": 3,
  "rfq": { /* RfqResource */ },
  "vendor_id": 2,
  "vendor": { /* VendorResource */ },
  "buyer_id": 1,
  "buyer": { /* BuyerResource */ },
  "user_id": 1,
  "entry_order": 1
}
```

## Field Descriptions

### Fixed Columns

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `id` | integer | Entry identifier | Primary key |
| `boq_sheet_id` | integer | Sheet identifier | Foreign key |
| `rfq_code` | string | RFQ identifier | Optional |
| `item_name` | string | Item description | Human-readable name |
| `vendor_name` | string | Vendor name | Derived from vendor relationship |
| `vat_rate` | decimal | VAT rate percentage | Derived from product |
| `image` | string | Image URL | Processed URL or placeholder |
| `unit` | string | Unit of measure | Max 20 chars |
| `unit_price` | decimal | Price per unit | Rounded to 2 decimals |
| `quantity` | decimal | Quantity needed | Rounded to 2 decimals |
| `amount` | decimal | Line amount | Rounded to 2 decimals |
| `vat_tax` | decimal | VAT amount | Rounded to 2 decimals |
| `total` | decimal | Line total | Rounded to 2 decimals |

### Additional Pricing Fields

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `tax_amount` | decimal | Additional tax | Rounded to 2 decimals |
| `shipping_amount` | decimal | Shipping cost | Rounded to 2 decimals |
| `loading_charge` | decimal | Loading fee | Rounded to 2 decimals |
| `services_charge` | decimal | Services fee | Rounded to 2 decimals |
| `total_amount` | decimal | Grand total | Rounded to 2 decimals |
| `discount_amount` | decimal | Discount | Rounded to 2 decimals |

### Dynamic Columns

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `dynamic_values` | object | Custom field values | Keyed by column names |
| `cell_colors` | object | Cell color mappings | Keyed by column names |
| `merged_cells` | array | Merged field names | Calculated from merges |
| `extra_columns` | array | Available columns | From parent sheet |

### Relationships

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `project_id` | integer | Project identifier | Foreign key |
| `product_id` | integer | Product identifier | Foreign key |
| `quotation_id` | integer | Quotation identifier | Foreign key |
| `quotation` | object | Quotation data | Included when loaded |
| `rfq_id` | integer | RFQ identifier | Foreign key |
| `rfq` | object | RFQ data | Included when loaded |
| `vendor_id` | integer | Vendor identifier | Foreign key |
| `vendor` | object | Vendor data | Included when loaded |
| `buyer_id` | integer | Buyer identifier | Foreign key |
| `buyer` | object | Buyer data | Included when loaded |
| `user_id` | integer | User identifier | Foreign key |
| `entry_order` | integer | Display order | For UI sorting |

## Data Transformations

### Extra Columns Transformation

The resource transforms the fragile CSV format from the parent sheet to a more usable array format:

**Database Format:**
```
"item_code,specification,unit"
```

**API Response:**
```json
{
  "extra_columns": ["item_code", "specification", "unit"]
}
```

**Transformation Code:**
```php
$extraColumnsArray = [];
if ($this->boqSheet && $this->boqSheet->extra_columns) {
    $extraColumnsArray = array_map('trim', explode(',', $this->boqSheet->extra_columns));
}
```

### Image URL Processing

The resource handles multiple image source formats:

**Priority Order:**
1. Full URL (if valid)
2. Storage path (converted to URL)
3. Product placeholder

**Transformation Code:**
```php
$image = null;
if($this->image && filter_var($this->image, FILTER_VALIDATE_URL)){
    $image = $this->image;
}
else if($this->image && Storage::disk('public')->exists($this->image)){
    $image = url('storage/'.$this->image);
}
else{
    $image = url('image/product-placeholder.jpg');
}
```

**Tech Debt:**
- **N+1 Query Risk**: Accessing `$this->boqSheet` without eager loading triggers N+1 queries
- **No Null Check**: Assumes `boqSheet` relationship exists

### Monetary Value Rounding

All monetary values are rounded to 2 decimal places:

```php
'unit_price' => $this->unit_price ? round((float) $this->unit_price, 2) : null,
'quantity' => $this->quantity ? round((float) $this->quantity, 2) : null,
'amount' => $this->amount ? round((float) $this->amount, 2) : null,
// ... etc
```

### Merge Field Names Calculation

The resource calculates which fields are merged for this entry:

**Method:**
```php
private function mergedFieldNamesFromBoqSheetMerges(): array
{
    $entryId = (int) $this->id;
    if (! $entryId || ! $this->boq_sheet_id) {
        return [];
    }

    if ($this->relationLoaded('boqSheet') && $this->boqSheet && $this->boqSheet->relationLoaded('boqSheetMerges')) {
        $merges = $this->boqSheet->boqSheetMerges;
    } else {
        $merges = BoqSheetMerge::query()->where('boq_sheet_id', $this->boq_sheet_id)->get();
    }

    $names = [];
    foreach ($merges as $merge) {
        $ids = array_map('intval', $merge->boq_sheet_entry_ids ?? []);
        if (! in_array($entryId, $ids, true)) {
            continue;
        }
        foreach ($merge->extra_fields ?? [] as $f) {
            $names[trim((string) $f)] = true;
        }
    }
    ksort($names);

    return array_keys($names);
}
```

**Behavior:**
1. Checks if merges are already loaded (optimization)
2. If not loaded, queries database for all merges for the sheet
3. Filters merges to find those that include this entry
4. Extracts field names from matching merges
5. Returns sorted array of field names

**Tech Debt:**
- **N+1 Query Risk**: If merges are not eager loaded, triggers additional query per entry
- **No Caching**: Recalculates for each entry even if same sheet

## Conditional Inclusion

The resource uses Laravel's conditional inclusion to avoid unnecessary data loading:

### `whenLoaded()`

```php
'quotation' => new QuotationResource($this->whenLoaded('quotation')),
'rfq' => new RfqResource($this->whenLoaded('rfq')),
'vendor' => new VendorResource($this->whenLoaded('vendor')),
'buyer' => new BuyerResource($this->whenLoaded('buyer')),
```

**Behavior:**
- Only includes data if the relationship was eager loaded
- Prevents N+1 query problems
- Reduces response size

### Commented Relationships

Several relationships are commented out to reduce response size:

```php
// 'boq_sheet' => new BoqSheetResource($this->whenLoaded('boqSheet')),
// 'project' => new ProjectResource($this->whenLoaded('project')),
// 'product' => new ProductResource($this->whenLoaded('product')),
// 'user' => new UserResource($this->whenLoaded('user')),
```

**Note:** These can be uncommented if needed for specific use cases.

## N+1 Query Risks

### Critical N+1 Risks

1. **Extra Columns Access**:
   ```php
   if ($this->boqSheet && $this->boqSheet->extra_columns) {
       $extraColumnsArray = array_map('trim', explode(',', $this->boqSheet->extra_columns));
   }
   ```
   **Risk**: Accessing `boqSheet` without eager loading triggers N+1 queries
   **Fix**: Always eager load `boqSheet` relationship

2. **Merge Field Names**:
   ```php
   if ($this->relationLoaded('boqSheet') && $this->boqSheet && $this->boqSheet->relationLoaded('boqSheetMerges')) {
       $merges = $this->boqSheet->boqSheetMerges;
   } else {
       $merges = BoqSheetMerge::query()->where('boq_sheet_id', $this->boq_sheet_id)->get();
   }
   ```
   **Risk**: If merges are not eager loaded, triggers additional query per entry
   **Fix**: Always eager load `boqSheet.boqSheetMerges` relationship

3. **Vendor Name**:
   ```php
   'vendor_name' => $this->vendor ? $this->vendor->name : null,
   ```
   **Risk**: Accessing `vendor` without eager loading triggers N+1 queries
   **Fix**: Always eager load `vendor` relationship

4. **VAT Rate**:
   ```php
   'vat_rate' => $this->product ? $this->product->vat_rate : null,
   ```
   **Risk**: Accessing `product` without eager loading triggers N+1 queries
   **Fix**: Always eager load `product` relationship

### Recommended Eager Loading

```php
// For list view - minimal data
$entries = BoqEntry::with('vendor', 'product')->get();

// For detail view - full data
$entry = BoqEntry::with([
    'boqSheet.boqSheetMerges',
    'vendor',
    'product',
    'quotation',
    'rfq',
    'buyer'
])->find($id);
```

## Usage Examples

### Basic Usage

```php
$entry = BoqEntry::find($id);
return new BoqEntryResource($entry);
```

### Collection Usage

```php
$entries = BoqEntry::with('vendor', 'product')->get();
return BoqEntryResource::collection($entries);
```

### With Relationships

```php
$entry = BoqEntry::with([
    'boqSheet.boqSheetMerges',
    'vendor',
    'product',
    'quotation',
    'rfq',
    'buyer'
])->find($id);
return new BoqEntryResource($entry);
```

### For Sheet View

```php
$sheet = BoqSheet::with([
    'entries' => function ($query) {
        $query->with('vendor', 'product');
    },
    'boqSheetMerges'
])->find($sheetId);

return new BoqSheetResource($sheet);
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| N+1 query on `boqSheet` access | HIGH | Performance issue | Always eager load `boqSheet` |
| N+1 query on merge calculation | HIGH | Performance issue | Always eager load `boqSheet.boqSheetMerges` |
| N+1 query on `vendor` access | MEDIUM | Performance issue | Always eager load `vendor` |
| N+1 query on `product` access | MEDIUM | Performance issue | Always eager load `product` |
| No image validation | LOW | Potential broken images | Add image existence check |
| No null check on `boqSheet` | LOW | Potential errors | Add null check |

## Cross-References

- BoqEntry-Model - Data model for entries
- [BoqSheet-Model](/entities/boqsheet-model) - Parent sheet for entries
- BoqSheetMerge-Model - Merge configurations
- [BoqEntryController](/entities/boqentrycontroller) - Controller that uses this resource
- [QuotationResource](/entities/quotationresource) - Resource for quotation data
- [RfqResource](/entities/rfqresource) - Resource for RFQ data
- VendorResource - Resource for vendor data
- BuyerResource - Resource for buyer data

## Architecture Notes

### Why This Resource Exists

The `BoqEntryResource` serves several critical purposes:

1. **Data Abstraction**: Hides database-specific details from API
2. **Data Transformation**: Converts internal formats to API-friendly formats
3. **Image Handling**: Processes and formats image URLs
4. **Performance Optimization**: Enables efficient eager loading
5. **Consistency**: Ensures consistent API responses
6. **Flexibility**: Supports conditional data inclusion

### Relationship to Other Resources

```
BoqSheetResource
    │
    └──> BoqEntryResource (entries relationship)
            ├──> QuotationResource (quotation relationship)
            ├──> RfqResource (rfq relationship)
            ├──> VendorResource (vendor relationship)
            └──> BuyerResource (buyer relationship)
```

### Future Enhancements

Potential improvements to this resource:

1. **Caching**: Cache merge field names calculation
2. **Validation**: Add format validation for transformed data
3. **Image optimization**: Add image optimization and CDN support
4. **Pagination support**: Add pagination wrapper for collections
5. **Filtering support**: Add field filtering capabilities
6. **Versioning**: Support multiple API versions

## Best Practices

### Eager Loading

Always eager load relationships to avoid N+1 queries:

```php
// Good - prevents N+1 queries
$entries = BoqEntry::with([
    'boqSheet.boqSheetMerges',
    'vendor',
    'product',
    'quotation',
    'rfq',
    'buyer'
])->get();

// Bad - causes N+1 queries
$entries = BoqEntry::get();
```

### Conditional Loading

Only load relationships when needed:

```php
// For list view - minimal data
$entries = BoqEntry::with('vendor', 'product')->get();

// For detail view - full data
$entry = BoqEntry::with([
    'boqSheet.boqSheetMerges',
    'vendor',
    'product',
    'quotation',
    'rfq',
    'buyer'
])->find($id);
```

### Response Size

Be mindful of response size when including relationships:

```php
// For list view - exclude heavy relationships
$entries = BoqEntry::with('vendor', 'product')->get();

// For detail view - include all relationships
$entry = BoqEntry::with([
    'boqSheet.boqSheetMerges',
    'vendor',
    'product',
    'quotation',
    'rfq',
    'buyer'
])->find($id);
```
