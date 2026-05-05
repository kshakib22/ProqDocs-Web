---
name: BoqSheetResource
description: Laravel API resource for BOQ (Bill of Quantities) sheet transformation - handles serialization of sheet data for API responses
type: entity
title: "BoqSheetResource"
---

# BoqSheetResource

## Architectural Purpose

`BoqSheetResource` is the API transformation layer for BOQ sheet data. This resource is responsible for:

- **Data serialization**: Converting BoqSheet models to API-ready JSON
- **Data transformation**: Converting internal data formats to frontend-friendly formats
- **Relationship loading**: Efficiently loading related data
- **Conditional inclusion**: Including data only when needed

This resource ensures that the API returns consistent, well-formatted data to the frontend, abstracting away database-specific details.

## Resource Dependencies

```php
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
```

- **JsonResource**: Base Laravel resource class
- **Request**: HTTP request for conditional data inclusion

## Resource Structure

### `toArray(Request $request): array`

**Purpose:** Transform the resource into an array for JSON response.

**Behavior:**
1. Converts comma-separated `extra_columns` string to array
2. Includes project data when loaded
3. Includes entries when loaded
4. Includes merge configurations when loaded
5. Calculates sum of entry totals
6. Returns formatted array

**Transformation Logic:**

```php
// Convert comma-separated extra_columns string to array
$extraColumnsArray = [];
if ($this->extra_columns) {
    $extraColumnsArray = array_map('trim', explode(',', $this->extra_columns));
}
```

**Response Structure:**
```json
{
  "id": 1,
  "sheet_name": "Foundation Works",
  "project_id": 1,
  "project": { /* ProjectResource */ },
  "extra_columns": ["item_code", "specification", "unit"],
  "extra_columns_string": "item_code,specification,unit",
  "cell_colors": {
    "header": {
      "rfq_code": "#ff0000"
    }
  },
  "entries_count": 10,
  "entries": [ /* BoqEntryResource collection */ ],
  "extra_field_merges": [ /* BoqSheetMergeResource collection */ ],
  "sheet_order": 1,
  "sum_total_amount": 15000.00,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Field Descriptions

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `id` | integer | Sheet identifier | Primary key |
| `sheet_name` | string | Sheet name | Human-readable identifier |
| `project_id` | integer | Project identifier | Foreign key |
| `project` | object | Project data | Included when loaded |
| `extra_columns` | array | Dynamic column names | Transformed from CSV |
| `extra_columns_string` | string | Original CSV format | For backward compatibility |
| `cell_colors` | object | Cell color mappings | JSON cast to array |
| `entries_count` | integer | Number of entries | Conditional inclusion |
| `entries` | array | Entry data | Included when loaded |
| `extra_field_merges` | array | Merge configurations | Included when loaded |
| `sheet_order` | integer | Display order | For UI sorting |
| `sum_total_amount` | decimal | Sum of entry totals | Calculated from entries |
| `created_at` | string | Creation timestamp | ISO 8601 format |
| `updated_at` | string | Update timestamp | ISO 8601 format |

## Data Transformations

### Extra Columns Transformation

The resource transforms the fragile CSV format to a more usable array format:

**Database Format:**
```
"item_code,specification,unit"
```

**API Response:**
```json
{
  "extra_columns": ["item_code", "specification", "unit"],
  "extra_columns_string": "item_code,specification,unit"
}
```

**Transformation Code:**
```php
$extraColumnsArray = [];
if ($this->extra_columns) {
    $extraColumnsArray = array_map('trim', explode(',', $this->extra_columns));
}
```

**Benefits:**
- Frontend can iterate over array
- No need to parse CSV on client
- Backward compatibility with `extra_columns_string`

### Sum Total Amount Calculation

The resource calculates the sum of all entry totals:

```php
'sum_total_amount' => $this->entries->sum('total_amount')
```

**Tech Debt:**
- **N+1 Query Risk**: If entries are not eager loaded, this will trigger N+1 queries
- **No Null Check**: Assumes entries are loaded, may throw error if not

**Recommended Fix:**
```php
'sum_total_amount' => $this->whenLoaded('entries', function () {
    return $this->entries->sum('total_amount');
}, 0)
```

## Conditional Inclusion

The resource uses Laravel's conditional inclusion to avoid unnecessary data loading:

### `whenLoaded()`

```php
'project' => new ProjectResource($this->whenLoaded('project')),
'entries' => BoqEntryResource::collection($this->whenLoaded('entries')),
'extra_field_merges' => BoqSheetMergeResource::collection($this->whenLoaded('boqSheetMerges')),
```

**Behavior:**
- Only includes data if the relationship was eager loaded
- Prevents N+1 query problems
- Reduces response size

### `when()`

```php
'entries_count' => $this->when(isset($this->entries_count), $this->entries_count),
```

**Behavior:**
- Only includes field if it's set
- Useful for aggregated data

## Usage Examples

### Basic Usage

```php
$sheet = BoqSheet::with('project', 'entries', 'boqSheetMerges')->find($id);
return new BoqSheetResource($sheet);
```

### Collection Usage

```php
$sheets = BoqSheet::with('project')->get();
return BoqSheetResource::collection($sheets);
```

### Minimal Usage

```php
$sheet = BoqSheet::find($id);
return new BoqSheetResource($sheet);
// Only includes basic fields, no relationships
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| N+1 query risk in `sum_total_amount` | MEDIUM | Performance issue | Add null check with `whenLoaded()` |
| No validation on `extra_columns` format | LOW | Potential data corruption | Add format validation |
| No pagination support | LOW | Performance at scale | Add pagination wrapper |

## Cross-References

- [BoqSheet-Model](./BoqSheet-Model.md) - Data model for sheets
- [BoqSheetController](./BoqSheetController.md) - Controller that uses this resource
- [BoqEntryResource](./BoqEntryResource.md) - Resource for entry data
- [BoqSheetMergeResource](./BoqSheetMergeResource.md) - Resource for merge data
- ProjectResource - Resource for project data

## Architecture Notes

### Why This Resource Exists

The `BoqSheetResource` serves several critical purposes:

1. **Data Abstraction**: Hides database-specific details from API
2. **Data Transformation**: Converts internal formats to API-friendly formats
3. **Performance Optimization**: Enables efficient eager loading
4. **Consistency**: Ensures consistent API responses
5. **Flexibility**: Supports conditional data inclusion

### Relationship to Other Resources

```
BoqSheetResource
    │
    ├──> ProjectResource (project relationship)
    ├──> BoqEntryResource (entries relationship)
    └──> BoqSheetMergeResource (merges relationship)
```

### Future Enhancements

Potential improvements to this resource:

1. **Pagination support**: Add pagination wrapper for collections
2. **Filtering support**: Add field filtering capabilities
3. **Sorting support**: Add custom sorting options
4. **Validation**: Add format validation for transformed data
5. **Caching**: Add response caching for frequently accessed sheets
6. **Versioning**: Support multiple API versions

## Best Practices

### Eager Loading

Always eager load relationships to avoid N+1 queries:

```php
// Good
$sheet = BoqSheet::with('project', 'entries', 'boqSheetMerges')->find($id);

// Bad - causes N+1 queries
$sheet = BoqSheet::find($id);
```

### Conditional Loading

Only load relationships when needed:

```php
// For list view - minimal data
$sheets = BoqSheet::with('project')->get();

// For detail view - full data
$sheet = BoqSheet::with('project', 'entries', 'boqSheetMerges')->find($id);
```

### Response Size

Be mindful of response size when including entries:

```php
// For list view - exclude entries
$sheets = BoqSheet::with('project')->get();

// For detail view - include entries
$sheet = BoqSheet::with('project', 'entries', 'boqSheetMerges')->find($id);
```
