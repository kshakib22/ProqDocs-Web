---
title: "RfqResource - RFQ API Transformation Layer"
---
# RfqResource - RFQ API Transformation Layer

**Entity**: `App\Http\Resources\RfqResource`
**Purpose**: Laravel JsonResource for serializing RFQ (Request for Quotation) models into API responses
**Version**: 1.0
**Last Updated**: 2026-05-04

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Field Mappings](#field-mappings)
4. [Relationship Serialization](#relationship-serialization)
5. [Computed Fields](#computed-fields)
6. [N+1 Query Risks](#n1-query-risks)
7. [Frontend Integration](#frontend-integration)
8. [Performance Considerations](#performance-considerations)
9. [Security Considerations](#security-considerations)
10. [Usage Patterns](#usage-patterns)
11. [Extension Points](#extension-points)
12. [Related Resources](#related-resources)

---

## Overview

`RfqResource` is a Laravel API Resource class that transforms `Rfq` model instances into JSON representations suitable for API responses. It serves as the primary serialization layer for all RFQ-related API endpoints, ensuring consistent data formatting across the application.

### Key Responsibilities

- **Data Transformation**: Converts database field names and types to frontend-friendly formats
- **Conditional Loading**: Uses `whenLoaded()` to prevent N+1 queries on relationships
- **Computed Properties**: Calculates derived values (days remaining, expiration status, totals)
- **URL Generation**: Converts storage paths to full URLs for assets
- **Type Coercion**: Ensures numeric fields are properly typed (floats for prices)

### Design Philosophy

The resource follows Laravel's API Resource conventions with emphasis on:
- Lazy relationship loading via `whenLoaded()`
- Conditional field inclusion via `when()`
- Minimal payload by excluding null relationships
- Consistent datetime formatting

---

## Architecture

### Class Hierarchy

```
JsonResource (Laravel Framework)
    └── RfqResource
```

### Dependencies

- `Illuminate\Http\Request` - For request context
- `Illuminate\Http\Resources\Json\JsonResource` - Base resource class
- `App\Http\Resources\ShortQuotationResource` - For nested quotation serialization
- `Carbon\Carbon` - For date calculations (imported inline)

### Data Flow

```
Rfq Model (Database)
    ↓
RfqResource (Transformation)
    ↓
JSON Response (API)
    ↓
Frontend (Consumption)
```

---

## Field Mappings

### Core RFQ Fields

| Database Field | API Field | Type | Notes |
|----------------|-----------|------|-------|
| `id` | `id` | integer | Primary key |
| `rfq_code` | `rfq_code` | string | Unique RFQ identifier |
| `rfq_title` | `rfq_title` | string | Human-readable title |
| `description` | `description` | string | Long-form description |
| `status` | `status` | string | RFQ status (draft, active, closed, etc.) |
| `type` | `type` | string | RFQ type classification |
| `is_private` | `is_private` | boolean | Privacy flag |
| `is_public` | `is_public` | boolean | Public visibility flag |
| `dead_line_date` | `dead_line_date` | string | Deadline (ISO format) |
| `urgency` | `urgency` | string | Urgency level |
| `budget_min` | `budget_min` | decimal | Minimum budget |
| `budget_max` | `budget_max` | decimal | Maximum budget |
| `unit` | `unit` | string | Unit of measurement |
| `unit_price` | `unit_price` | float/null | Price per unit (coerced to float) |
| `estimated_quantity` | `quantity` | integer | Field name remapped for frontend |
| `product_image` | `product_image` | string/null | Full URL to product image |
| `created_at` | `created_at` | string/null | ISO 8601 datetime |
| `updated_at` | `updated_at` | string/null | ISO 8601 datetime |

### Field Transformation Details

#### URL Generation for Assets

```php
// Product image URL generation
'product_image' => $this->product_image ? url('storage/'.$this->product_image) : null
```

- Converts relative storage paths to absolute URLs
- Returns `null` if no image exists
- Uses Laravel's `url()` helper for scheme-aware URL generation

#### Type Coercion

```php
'unit_price' => $this->unit_price ? (float) $this->unit_price : null
```

- Explicitly casts decimal values to float for JSON serialization
- Preserves null values when no price is set

#### DateTime Formatting

```php
'created_at' => $this->created_at?->format('Y-m-d H:i:s'),
'updated_at' => $this->updated_at?->format('Y-m-d H:i:s'),
```

- Uses null-safe operator (`?->`) to handle null timestamps
- Formats to `YYYY-MM-DD HH:MM:SS` format
- Consistent with frontend expectations

---

## Relationship Serialization

### Buyer Relationship

**Condition**: `whenLoaded('buyer')`

**Fields**:
- `id` - Buyer profile ID
- `user_id` - Associated user ID
- `name` - Buyer name
- `user` (nested) - User details when `buyer.user` is loaded

**Nested User Fields**:
- `id` - User ID
- `name` - User name
- `email` - User email

**N+1 Risk**: HIGH - Requires `buyer` and `buyer.user` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with(['buyer.user'])->get();
```

---

### Vendor Relationship

**Condition**: `whenLoaded('vendor')`

**Fields**:
- `id` - Vendor profile ID
- `company_name` - Vendor company name
- `user_id` - Associated user ID
- `user` (nested) - User details when `vendor.user` is loaded

**Nested User Fields**:
- `id` - User ID
- `name` - User name
- `email` - User email

**N+1 Risk**: HIGH - Requires `vendor` and `vendor.user` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with(['vendor.user'])->get();
```

---

### Project Relationship

**Condition**: `whenLoaded('project')`

**Fields**:
- `id` - Project ID
- `name` - Project name (mapped from `project_name`)
- `location` - Concatenated city and country
- `description` - Project description
- `status` - Project status (mapped from `boq_status`)

**Field Remapping**:
- `project_name` → `name`
- `boq_status` → `status`

**N+1 Risk**: MEDIUM - Requires `project` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('project')->get();
```

---

### Product Relationship

**Condition**: `whenLoaded('product')`

**Fields**:
- `id` - Product ID
- `name` - Product name
- `description` - Product description
- `unit` - Unit of measurement
- `base_price` - Base price (coerced to float)
- `product_code` - Product code
- `product_image` - Full URL to product image

**URL Generation**:
```php
$productImage = $this->product->product_image ? url('storage/'.$this->product->product_image) : null;
```

**N+1 Risk**: MEDIUM - Requires `product` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('product')->get();
```

---

### Category Relationship

**Condition**: `whenLoaded('category')`

**Fields**:
- `id` - Category ID
- `name` - Category name
- `slug` - URL-friendly slug

**N+1 Risk**: LOW - Simple relationship, minimal data

**Eager Load Pattern**:
```php
Rfq::with('category')->get();
```

---

### Documents Relationship

**Condition**: `whenLoaded('documents')`

**Fields** (per document):
- `id` - Document ID
- `name` - Document name
- `file_path` - File path
- `file_size` - File size in bytes
- `mime_type` - MIME type
- `created_at` - Upload timestamp

**Collection Handling**:
```php
return $this->documents->map(function ($document) {
    // Inline transformation
});
```

**N+1 Risk**: MEDIUM - Requires `documents` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('documents')->get();
```

---

### Quotations Relationship

**Condition**: `whenLoaded('quotations')`

**Fields**: Delegated to `ShortQuotationResource`

**N+1 Risk**: HIGH - Requires `quotations` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('quotations')->get();
```

---

## Computed Fields

### days_remaining

**Condition**: `when($this->dead_line_date)`

**Logic**:
```php
$deadline = \Carbon\Carbon::parse($this->dead_line_date);
$now = \Carbon\Carbon::now();
return $deadline->isFuture() ? $now->diffInDays($deadline) : 0;
```

**Behavior**:
- Only included when `dead_line_date` is set
- Returns positive integer for future deadlines
- Returns `0` for past or current deadlines
- Uses Carbon's `diffInDays()` for calculation

**Use Case**: Frontend countdown timers, urgency indicators

---

### is_expired

**Condition**: `when($this->dead_line_date)`

**Logic**:
```php
return \Carbon\Carbon::parse($this->dead_line_date)->isPast();
```

**Behavior**:
- Only included when `dead_line_date` is set
- Returns `true` if deadline has passed
- Returns `false` if deadline is in the future

**Use Case**: Status badges, filtering active RFQs

---

### total_value

**Condition**: `when($this->unit_price && $this->quantity)`

**Logic**:
```php
return (float) ($this->unit_price * $this->quantity);
```

**Behavior**:
- Only included when both `unit_price` and `quantity` are set
- Returns calculated total as float
- Coerced to float for JSON serialization

**Use Case**: Budget summaries, cost calculations

---

## N+1 Query Risks

### Critical Risk Areas

#### 1. Nested User Relationships (HIGH RISK)

**Problem**: Accessing `buyer.user` and `vendor.user` without eager loading

**Symptoms**:
- One query for RFQs
- Additional query for each RFQ's buyer
- Additional query for each buyer's user
- Same pattern for vendor

**Impact**: O(n) queries where n = number of RFQs

**Solution**:
```php
// Correct
Rfq::with(['buyer.user', 'vendor.user'])->get();

// Incorrect
Rfq::all(); // Triggers N+1 on buyer and user
```

---

#### 2. Documents Collection (MEDIUM RISK)

**Problem**: Loading documents without eager loading

**Symptoms**:
- One query for RFQs
- Additional query for each RFQ's documents

**Impact**: O(n) queries where n = number of RFQs

**Solution**:
```php
// Correct
Rfq::with('documents')->get();

// Incorrect
Rfq::all(); // Triggers N+1 on documents
```

---

#### 3. Quotations Collection (HIGH RISK)

**Problem**: Loading quotations without eager loading

**Symptoms**:
- One query for RFQs
- Additional query for each RFQ's quotations

**Impact**: O(n) queries where n = number of RFQs

**Solution**:
```php
// Correct
Rfq::with('quotations')->get();

// Incorrect
Rfq::all(); // Triggers N+1 on quotations
```

---

### Recommended Eager Load Patterns

#### Full Load (All Relationships)

```php
Rfq::with([
    'buyer.user',
    'vendor.user',
    'project',
    'product',
    'category',
    'documents',
    'quotations'
])->get();
```

#### Minimal Load (Core Fields Only)

```php
Rfq::with([
    'buyer',
    'vendor',
    'project'
])->get();
```

#### Conditional Load (Based on Request)

```php
$query = Rfq::query();

if ($request->has('include')) {
    $includes = explode(',', $request->include);
    foreach ($includes as $include) {
        $query->with($include);
    }
}

return RfqResource::collection($query->get());
```

---

## Frontend Integration

### Expected Response Structure

```json
{
  "id": 1,
  "rfq_code": "RFQ-2024-001",
  "rfq_title": "Steel Beams for Construction",
  "description": "Need 500 tons of steel beams...",
  "status": "active",
  "type": "material",
  "is_private": false,
  "is_public": true,
  "dead_line_date": "2024-06-30",
  "urgency": "high",
  "budget_min": 50000.00,
  "budget_max": 75000.00,
  "unit": "tons",
  "unit_price": 150.00,
  "quantity": 500,
  "product_image": "https://example.com/storage/products/steel-beams.jpg",
  "created_at": "2024-05-01 10:00:00",
  "updated_at": "2024-05-02 14:30:00",
  "buyer": {
    "id": 10,
    "user_id": 5,
    "name": "Acme Construction",
    "user": {
      "id": 5,
      "name": "John Doe",
      "email": "john@acme.com"
    }
  },
  "vendor": {
    "id": 20,
    "company_name": "Steel Suppliers Inc",
    "user_id": 15,
    "user": {
      "id": 15,
      "name": "Jane Smith",
      "email": "jane@steelsuppliers.com"
    }
  },
  "project": {
    "id": 100,
    "name": "Downtown Tower",
    "location": "New York, USA",
    "description": "50-story commercial building",
    "status": "in_progress"
  },
  "product": {
    "id": 50,
    "name": "Steel Beam H-Section",
    "description": "Structural steel beam",
    "unit": "tons",
    "base_price": 140.00,
    "product_code": "STL-BEAM-H001",
    "product_image": "https://example.com/storage/products/steel-beams.jpg"
  },
  "category": {
    "id": 5,
    "name": "Construction Materials",
    "slug": "construction-materials"
  },
  "documents": [
    {
      "id": 1,
      "name": "specifications.pdf",
      "file_path": "storage/documents/specifications.pdf",
      "file_size": 2048576,
      "mime_type": "application/pdf",
      "created_at": "2024-05-01 10:05:00"
    }
  ],
  "days_remaining": 57,
  "is_expired": false,
  "total_value": 75000.00,
  "quotations": []
}
```

### Frontend Usage Patterns

#### Display RFQ List

```javascript
// Fetch with minimal relationships
const rfqs = await api.get('/rfqs?include=buyer,project');

// Display
rfqs.data.map(rfq => ({
  id: rfq.id,
  code: rfq.rfq_code,
  title: rfq.rfq_title,
  buyer: rfq.buyer?.name,
  project: rfq.project?.name,
  deadline: rfq.days_remaining,
  expired: rfq.is_expired
}));
```

#### Display RFQ Detail

```javascript
// Fetch with all relationships
const rfq = await api.get(`/rfqs/${id}?include=buyer.user,vendor.user,project,product,category,documents,quotations`);

// Display full details
console.log(rfq);
```

#### Filter by Status

```javascript
const activeRfqs = rfqs.filter(rfq => !rfq.is_expired && rfq.status === 'active');
```

---

## Performance Considerations

### Memory Usage

- **Single RFQ**: ~2-5 KB (depending on loaded relationships)
- **Collection of 100 RFQs**: ~200-500 KB
- **Full Load with All Relationships**: ~500-1000 KB per 100 RFQs

### Query Optimization Tips

1. **Select Only Needed Fields**:
```php
Rfq::with(['buyer:id,name,user_id', 'buyer.user:id,name,email'])
    ->select(['id', 'rfq_code', 'rfq_title', 'buyer_id'])
    ->get();
```

2. **Use Pagination**:
```php
Rfq::with(['buyer.user', 'vendor.user'])
    ->paginate(20);
```

3. **Cache Computed Fields**:
```php
// Consider adding cached columns to model
protected $appends = ['days_remaining', 'is_expired', 'total_value'];
```

4. **Use Resource Collections**:
```php
return RfqResource::collection(Rfq::with('buyer')->get());
```

### Response Time Benchmarks

| Scenario | Expected Time | Notes |
|----------|---------------|-------|
| Single RFQ (no relations) | 10-20ms | Minimal payload |
| Single RFQ (all relations) | 50-100ms | Full payload |
| Collection of 20 (minimal) | 30-50ms | With eager loading |
| Collection of 20 (full) | 100-200ms | With all relations |
| Collection of 100 (minimal) | 100-200ms | With pagination |
| Collection of 100 (full) | 500-1000ms | With pagination |

---

## Security Considerations

### Data Exposure

#### Sensitive Fields

The following fields may contain sensitive information:
- `budget_min` / `budget_max` - Financial information
- `buyer.user.email` - Contact information
- `vendor.user.email` - Contact information
- `documents.file_path` - Internal file paths

**Recommendation**: Implement role-based access control to restrict sensitive fields based on user permissions.

#### Access Control

```php
// In controller
public function show(Rfq $rfq)
{
    $this->authorize('view', $rfq);

    return new RfqResource($rfq);
}
```

### URL Generation

The resource uses `url('storage/...')` which:
- Generates absolute URLs
- Exposes the domain name
- May expose internal structure if not properly configured

**Recommendation**: Ensure storage is properly configured and use signed URLs for sensitive documents.

---

## Usage Patterns

### Controller Integration

#### Single Resource

```php
use App\Http\Resources\RfqResource;

public function show($id)
{
    $rfq = Rfq::with([
        'buyer.user',
        'vendor.user',
        'project',
        'product',
        'category',
        'documents',
        'quotations'
    ])->findOrFail($id);

    return new RfqResource($rfq);
}
```

#### Collection

```php
use App\Http\Resources\RfqResource;

public function index(Request $request)
{
    $query = Rfq::query();

    // Eager load based on request
    if ($request->has('include')) {
        $includes = explode(',', $request->include);
        $validIncludes = ['buyer', 'vendor', 'project', 'product', 'category', 'documents', 'quotations'];
        $query->with(array_intersect($validIncludes, $includes));
    }

    $rfqs = $query->paginate(20);

    return RfqResource::collection($rfqs);
}
```

#### With Additional Meta

```php
use App\Http\Resources\RfqResource;

public function show($id)
{
    $rfq = Rfq::with('buyer')->findOrFail($id);

    return RfqResource::make($rfq)->additional([
        'meta' => [
            'can_edit' => auth()->user()->can('update', $rfq),
            'can_delete' => auth()->user()->can('delete', $rfq),
        ]
    ]);
}
```

---

## Extension Points

### Adding New Fields

To add a new field to the resource:

```php
public function toArray(Request $request): array
{
    return [
        // ... existing fields
        'new_field' => $this->new_field,
    ];
}
```

### Adding Conditional Fields

```php
'admin_only' => $this->when(auth()->user()?->isAdmin(), function () {
    return $this->admin_data;
}),
```

### Custom Relationship Serialization

```php
'custom_relation' => $this->whenLoaded('customRelation', function () {
    return CustomResource::make($this->customRelation);
}),
```

### Adding Computed Properties

```php
'computed_field' => $this->when($this->someCondition, function () {
    return $this->calculateSomething();
}),
```

---

## Related Resources

### Direct Dependencies

- `ShortQuotationResource` - Used for nested quotation serialization

### Related Models

- `App\Models\Rfq` - The underlying model
- `App\Models\Buyer` - Buyer profile
- `App\Models\Vendor` - Vendor profile
- `App\Models\Project` - Project details
- `App\Models\Product` - Product details
- `App\Models\Category` - Category details
- `App\Models\Document` - Document attachments
- `App\Models\Quotation` - Quotation submissions

### Related Controllers

- `App\Http\Controllers\RfqController` - Primary controller
- `App\Http\Controllers\Api\RfqController` - API controller

### Related Resources

- `App\Http\Resources\ShortQuotationResource` - Quotation summary
- `App\Http\Resources\QuotationResource` - Full quotation details

---

## Changelog

### Version 1.0 (2026-05-04)
- Initial documentation
- Complete field mapping
- N+1 query analysis
- Performance considerations documented

---

## Notes

1. **Field Naming**: Some fields are remapped from database names (e.g., `estimated_quantity` → `quantity`)
2. **URL Generation**: All asset URLs are generated using Laravel's `url()` helper
3. **Null Handling**: Extensive use of null-safe operators and conditional inclusion
4. **Type Safety**: Numeric fields are explicitly cast to appropriate types
5. **Relationship Loading**: All relationships use `whenLoaded()` to prevent N+1 queries

---

## Future Improvements

1. **API Versioning**: Consider versioning the resource for backward compatibility
2. **Field Selection**: Implement sparse fieldsets (`?fields=id,rfq_code,status`)
3. **Included Resources**: Standardize relationship inclusion via query parameters
4. **Caching**: Add caching layer for computed fields
5. **Validation**: Add validation for required fields before serialization
6. **Testing**: Add comprehensive unit tests for all transformations

---

**End of Documentation**
