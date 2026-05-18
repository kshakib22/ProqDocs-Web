---
name: BoqSheetMergeResource
description: Laravel API resource for BOQ sheet merge transformation - handles serialization of merge configurations for API responses
type: entity
title: "BoqSheetMergeResource"
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

- BoqSheetMerge-Model - Data model for merges
- [BoqSheet-Model](/entities/boqsheet-model) - Parent sheet for merges
- [BoqEntry-Model](/entities/boqentrymodel) - Entries included in merges
- [BoqSheetMergeService](/entities/boqsheetmergeservice) - Service that creates merges

## Architecture Notes

...