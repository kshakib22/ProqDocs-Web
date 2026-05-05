---
name: BoqSheet-Model
description: Laravel Eloquent model for BOQ (Bill of Quantities) sheets - the primary container for construction project quantity data
type: entity
title: "BoqSheet Model"
---

# BoqSheet Model

## Architectural Purpose

`BoqSheet` is the root entity of the BOQ (Bill of Quantities) domain. It represents a complete quantity sheet for a construction project, serving as the container for all line items (entries) that define materials, labor, and equipment quantities. This model is the central hub that connects to:

- **[Projects](./Project-Domain.md)**: Each BOQ sheet belongs to a specific project
- **[BoqEntry](./BoqEntryModel.md)**: Contains the actual line items/rows of the quantity sheet
- **[BoqSheetMerge](./BoqSheetMergeModel.md)**: Tracks merge operations when sheets are combined

The BOQ sheet is the foundational document used throughout the procurement lifecycle, feeding into [PurchaseListService](./PurchaseListService.md) and RFQ generation workflows.

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `project_id` | bigint | Foreign key | Links to `projects` table |
| `name` | string | Sheet name | Human-readable identifier |
| `extra_columns` | string | Dynamic schema | **FRAGILE**: Comma-separated column names |
| `cell_colors` | json | Cell styling | Cast to array, stores color mappings |
| `created_at` | timestamp | Creation time | Laravel managed |
| `updated_at` | timestamp | Last update | Laravel managed |

### Critical Schema Vulnerability: `extra_columns`

The `extra_columns` field stores dynamic column definitions as a **comma-separated string**. This is a significant architectural debt:

```php
// Current implementation (FRAGILE)
public function getExtraColumnsArrayAttribute()
{
    if (empty($this->extra_columns)) {
        return [];
    }
    return array_map('trim', explode(',', $this->extra_columns));
}
```

**Problems:**
1. No schema validation - any string can be stored
2. No referential integrity - columns can be deleted from entries but not from the sheet
3. Query limitations - cannot efficiently query by specific extra columns
4. Migration risk - changing column names requires string manipulation
5. No type safety - all values are strings

**Recommended Fix:** Migrate to a JSON column or a dedicated `boq_sheet_columns` table with proper foreign key relationships.

## Model Relationships

### `project(): BelongsTo`

```php
public function project(): BelongsTo
{
    return $this->belongsTo(Project::class);
}
```

- **Purpose:** Links the BOQ sheet to its parent project
- **Cardinality:** Many-to-one (many sheets per project)
- **Usage:** Used to scope queries by project and access project metadata

### `entries(): HasMany`

```php
public function entries(): HasMany
{
    return $this->hasMany(BoqEntry::class);
}
```

- **Purpose:** Retrieves all line items belonging to this sheet
- **Cardinality:** One-to-many (one sheet has many entries)
- **Usage:** Primary access point for iterating through quantity data
- **Related:** [BoqEntry-Model](./BoqEntryModel.md)

### `boqSheetMerges(): HasMany`

```php
public function boqSheetMerges(): HasMany
{
    return $this->hasMany(BoqSheetMerge::class);
}
```

- **Purpose:** Tracks merge operations where this sheet was involved
- **Cardinality:** One-to-many
- **Usage:** Audit trail for sheet combination operations
- **Related**: BoqSheetMerge-Model

## Lifecycle Hooks

### `booted()` - Cascade Delete

```php
protected static function booted(): void
{
    static::deleting(function (BoqSheet $sheet) {
        $sheet->boqSheetMerges()->delete();
    });
}
```

**Behavior:** When a BoqSheet is deleted, all associated `BoqSheetMerge` records are also deleted.

**Critical Gap:** This hook does **NOT** delete the associated `BoqEntry` records. This is a **data integrity vulnerability**:

1. Orphaned entries will remain in the database
2. Foreign key constraints may fail if `boq_entries.boq_sheet_id` is not nullable
3. Storage bloat from unreferenced rows

**Recommended Fix:**
```php
static::deleting(function (BoqSheet $sheet) {
    $sheet->boqSheetMerges()->delete();
    $sheet->entries()->delete(); // MISSING - causes orphaned entries
});
```

## Attribute Casts

### `cell_colors` → Array

```php
protected $casts = [
    'cell_colors' => 'array',
];
```

Stores cell color mappings as JSON in the database, automatically cast to/from PHP arrays. Used for UI styling of the quantity sheet grid.

## Accessors & Mutators

### `getExtraColumnsArrayAttribute()`

Converts the comma-separated `extra_columns` string to a trimmed array.

**Input:** `"item_code,specification,unit"`
**Output:** `["item_code", "specification", "unit"]`

### `setExtraColumnsArrayAttribute($value)`

Converts an array of column names back to a comma-separated string for storage.

**Input:** `["item_code", "specification", "unit"]`
**Output:** `"item_code,specification,unit"`

## Data Flow

### Creation Flow

```
1. User creates new BOQ sheet via UI
2. BoqSheetController validates input
3. BoqSheetService::create() instantiates model
4. Model saves to database
5. Returns BoqSheet instance with ID
```

### Query Flow

```
1. Request to view BOQ sheet
2. BoqSheetService::find() retrieves model
3. Model eager loads entries() relationship
4. Returns complete sheet with all line items
```

### Deletion Flow

```
1. User deletes BOQ sheet
2. BoqSheetController calls delete()
3. Model's booted() hook triggers
4. boqSheetMerges() deleted (entries NOT deleted - BUG)
5. Transaction commits
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| `extra_columns` as CSV | HIGH | Schema fragility, no validation | Migrate to JSON or dedicated table |
| Missing cascade delete for entries | HIGH | Orphaned data, storage bloat | Add `$sheet->entries()->delete()` |
| No indexes on `extra_columns` | MEDIUM | Query performance | Add composite index if querying needed |
| No validation on `cell_colors` | LOW | Potential UI corruption | Add validation rules |

## Cross-References

- [BoqSheetService](./BoqSheetService.md) - Business logic for sheet operations
- [BoqEntry-Model](./BoqEntryModel.md) - Line items contained within sheets
- BoqSheetMerge-Model - Merge operations tracking
- [PurchaseListService](./PurchaseListService.md) - Downstream consumer of BOQ data
- [BoqSheetController](./BoqSheetController.md) - HTTP endpoint handler

## Usage Examples

### Creating a new sheet with extra columns

```php
$sheet = BoqSheet::create([
    'project_id' => $project->id,
    'name' => 'Foundation Works',
    'extra_columns' => 'item_code,specification,unit',
    'cell_colors' => ['A1' => '#FF0000', 'B2' => '#00FF00'],
]);

// Access extra columns as array
$columns = $sheet->extra_columns_array; // ['item_code', 'specification', 'unit']
```

### Loading sheet with entries

```php
$sheet = BoqSheet::with('entries')->find($id);

foreach ($sheet->entries as $entry) {
    // Process each line item
}
```

### Querying by project

```php
$sheets = BoqSheet::where('project_id', $projectId)
    ->with('entries')
    ->get();
```
