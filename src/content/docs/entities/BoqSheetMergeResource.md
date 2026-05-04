---
name: BoqSheetMergeResource
description: Laravel API resource for BOQ sheet merge transformation - handles serialization of merge configurations for API responses
type: entity
---

# BoqSheetMergeResource

## Architectural Purpose

`BoqSheetMergeResource` is the API transformation layer for BOQ sheet merge configurations. This resource is responsible for:

- **Data serialization**: Converting BoqSheetMerge models to API-ready JSON
- **Data transformation**: Converting internal data formats to frontend-friendly formats
- **Relationship loading**: Efficiently loading related data
- **Conditional inclusion**: Including data only when needed

This resource ensures that the API returns consistent, well-formatted merge data to the frontend, abstracting away database-specific details.

## Resource Dependencies

```php
use App\Models\BoqSheetMerge;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
```

- **JsonResource**: Base Laravel resource class
- **Request**: HTTP request for conditional data inclusion

## Resource Structure

### `toArray(Request $request): array`

**Purpose:** Transform the resource into an array for JSON response.

**Behavior:**
1. Returns merge configuration data
2. Includes all merge fields
3. Returns formatted array

**Response Structure:**
```json
{
  "id": 1,
  "boq_sheet_id": 1,
  "extra_fields": ["item_code", "specification"],
  "boq_sheet_entry_ids": [1, 2, 3],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Field Descriptions

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `id` | integer | Merge identifier | Primary key |
| `boq_sheet_id` | integer | Sheet identifier | Foreign key |
| `extra_fields` | array | Dynamic column names | Fields involved in merge |
| `boq_sheet_entry_ids` | array | Entry identifiers | Entries involved in merge |
| `created_at` | string | Creation timestamp | ISO 8601 format |
| `updated_at` | string | Update timestamp | ISO 8601 format |

## Data Transformations

### JSON Cast Handling

The resource relies on Laravel's JSON casts for array fields:

**Database Format:**
```json
{
  "extra_fields": ["item_code", "specification"],
  "boq_sheet_entry_ids": [1, 2, 3]
}
```

**API Response:**
```json
{
  "extra_fields": ["item_code", "specification"],
  "boq_sheet_entry_ids": [1, 2, 3]
}
```

## Usage Examples

### Basic Usage

```php
$merge = BoqSheetMerge::find($id);
return new BoqSheetMergeResource($merge);
```

### Collection Usage

```php
$merges = BoqSheetMerge::where('boq_sheet_id', $sheetId)->get();
return BoqSheetMergeResource::collection($merges);
```

### With Parent Sheet

```php
$merge = BoqSheetMerge::with('boqSheet')->find($id);
return new BoqSheetMergeResource($merge);
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No conditional inclusion | LOW | Always returns all fields | Add `whenLoaded()` for relationships |
| No validation on data format | LOW | Potential data corruption | Add format validation |

## Cross-References

- [[BoqSheetMerge-Model]] - Data model for merges
- [[BoqSheet-Model]] - Parent sheet for merges
- [[BoqEntry-Model]] - Entries included in merges
- [[BoqSheetMergeService]] - Service that creates merges

## Architecture Notes

### Why This Resource Exists

The `BoqSheetMergeResource` serves several critical purposes:

1. **Data Abstraction**: Hides database-specific details from API
2. **Data Transformation**: Converts internal formats to API-friendly formats
3. **Consistency**: Ensures consistent API responses
4. **Flexibility**: Supports conditional data inclusion

### Relationship to Other Resources

```
BoqSheetResource
    │
    └──> BoqSheetMergeResource (merges relationship)
```

### Future Enhancements

Potential improvements to this resource:

1. **Conditional inclusion**: Add `whenLoaded()` for relationships
2. **Validation**: Add format validation for transformed data
3. **Caching**: Add response caching for frequently accessed merges
4. **Versioning**: Support multiple API versions

## Best Practices

### Eager Loading

Always eager load relationships to avoid N+1 queries:

```php
// Good
$merge = BoqSheetMerge::with('boqSheet')->find($id);

// Bad - causes N+1 queries
$merge = BoqSheetMerge::find($id);
```

### Collection Usage

Use collection for multiple merges:

```php
$merges = BoqSheetMerge::where('boq_sheet_id', $sheetId)->get();
return BoqSheetMergeResource::collection($merges);
```

## N+1 Query Risks

### Current Implementation

The resource does not have any N+1 query risks because:

1. **No nested relationships**: The resource only returns flat data
2. **No conditional queries**: All data is available on the model
3. **No lazy loading**: No relationships are accessed without eager loading

### Potential Risks

If relationships are added in the future, ensure they are eager loaded:

```php
// If adding boqSheet relationship
$merge = BoqSheetMerge::with('boqSheet')->find($id);
```
