---
name: BoqSheetMerge-Model
description: Laravel Eloquent model for BOQ sheet merge operations - tracks when multiple BOQ sheets are combined
type: entity
title: "BoqSheetMerge Model"
---

# BoqSheetMerge Model

## Architectural Purpose

`BoqSheetMerge` represents a merge operation where multiple BOQ sheets are combined into a single consolidated view. This model serves as an audit trail and metadata container for sheet combination operations, storing:

- **Source sheet reference**: Which sheet the merge was performed on
- **Extra field definitions**: Custom fields added during the merge
- **Entry ID tracking**: Which entries were included in the merge

This model is critical for tracking the history of BOQ sheet manipulations and enabling undo/redo operations on merged sheets.

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `boq_sheet_id` | bigint | Foreign key | Links to `boq_sheets`, **no DB FK** |
| `extra_fields` | json | Custom fields | Additional fields added during merge |
| `boq_sheet_entry_ids` | json | Entry tracking | IDs of entries included in merge |
| `created_at` | timestamp | Creation time | Laravel managed |
| `updated_at` | timestamp | Last update | Laravel managed |

### Critical Architecture Decision: No Database Foreign Key

**IMPORTANT:** The `boq_sheet_id` column has **no database-level foreign key constraint**:

```php
// Migration
$table->unsignedBigInteger('boq_sheet_id');
$table->index('boq_sheet_id');
// NO ->constrained() or ->foreign() call
```

**Rationale (from migration comment):**
```php
// No DB-level FK: avoids MySQL 1824 when the server cannot resolve `boq_sheets`
// (wrong schema, legacy table, or engine quirks). Integrity is enforced in app code;
// merges are removed when a sheet is deleted via BoqSheet::booted.
```

**Implications:**
1. **Application-level integrity**: Referential integrity must be enforced in code
2. **No cascade delete**: Database won't auto-delete merges when sheet is deleted
3. **Manual cleanup required**: `BoqSheet::booted()` hook handles deletion
4. **Potential orphaned records**: If app code fails, orphaned merges may exist

**Trade-off Analysis:**
- **Pro**: Avoids MySQL 1824 errors in complex environments
- **Pro**: Allows more flexible merge operations
- **Con**: No database-level data integrity guarantees
- **Con**: Requires careful application-level cleanup

## Model Relationships

### `boqSheet(): BelongsTo`

```php
public function boqSheet(): BelongsTo
{
    return $this->belongsTo(BoqSheet::class);
}
```

- **Purpose:** Links the merge record to its source BOQ sheet
- **Cardinality:** Many-to-one (many merges per sheet)
- **Cascade:** Application-level via `BoqSheet::booted()` hook
- **Usage:** Access parent sheet metadata and entries

**Note:** This relationship works despite no database FK because Laravel's Eloquent uses the column name convention (`boq_sheet_id`) to establish the relationship.

## Attribute Casts

### `extra_fields` → Array

```php
protected $casts = [
    'extra_fields' => 'array',
];
```

Stores additional field definitions added during the merge operation.

**Expected Structure:**
```json
{
  "merged_from": ["sheet_1", "sheet_2"],
  "merge_timestamp": "2024-01-15T10:30:00Z",
  "merge_type": "consolidate"
}
```

**Purpose:** Allows storing arbitrary metadata about the merge operation without schema changes.

### `boq_sheet_entry_ids` → Array

```php
protected $casts = [
    'boq_sheet_entry_ids' => 'array',
];
```

Stores the IDs of entries that were included in this merge operation.

**Expected Structure:**
```json
[1, 2, 3, 5, 8, 13, 21]
```

**Purpose:** Enables tracking which specific entries were merged, allowing for:
- Undo operations (restore original entries)
- Audit trails (what was merged when)
- Conflict resolution (identify duplicate entries)

## Lifecycle Hooks

**NONE**: This model has no lifecycle hooks defined.

**Implication:** All cleanup must be handled by the parent `BoqSheet` model's `booted()` hook:

```php
// In BoqSheet model
protected static function booted(): void
{
    static::deleting(function (BoqSheet $sheet) {
        $sheet->boqSheetMerges()->delete();
    });
}
```

## Data Flow

### Merge Creation Flow

```
1. User initiates merge operation via UI
2. BoqSheetMergeService validates merge request
3. Service creates BoqSheetMerge record
4. Service populates extra_fields with merge metadata
5. Service populates boq_sheet_entry_ids with affected entries
6. Service performs actual merge on entries
7. Returns BoqSheetMerge instance
```

### Merge Deletion Flow

```
1. User deletes parent BoqSheet
2. BoqSheet::booted() hook triggers
3. Hook calls $sheet->boqSheetMerges()->delete()
4. All merge records for this sheet are deleted
5. Transaction commits
```

### Merge Query Flow

```
1. Request to view merge history
2. BoqSheetMergeService::findBySheet() retrieves records
3. Service eager loads boqSheet() relationship
4. Returns merge records with metadata
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No database FK | MEDIUM | No DB-level integrity | Consider adding with proper error handling |
| No validation on JSON fields | LOW | Potential corruption | Add validation rules |
| No indexes on JSON fields | LOW | Query performance | Add generated columns if querying needed |
| No undo/redo logic | LOW | Limited functionality | Implement service methods |

## Cross-References

- [BoqSheet-Model](/entities/boqsheet-model) - Parent sheet that owns this merge
- [BoqSheetMergeService](/entities/boqsheetmergeservice) - Business logic for merge operations
- BoqEntry-Model - Entries affected by merge
- [BoqSheetController](/entities/boqsheetcontroller) - HTTP endpoint handler

## Usage Examples

### Creating a merge record

```php
$merge = BoqSheetMerge::create([
    'boq_sheet_id' => $sheet->id,
    'extra_fields' => [
        'merged_from' => ['Foundation', 'Structural'],
        'merge_type' => 'consolidate',
        'user_id' => auth()->id()
    ],
    'boq_sheet_entry_ids' => [1, 2, 3, 5, 8]
]);
```

### Loading merge with sheet

```php
$merge = BoqSheetMerge::with('boqSheet')->find($mergeId);

$sheetName = $merge->boqSheet->sheet_name;
$affectedEntries = $merge->boq_sheet_entry_ids;
```

### Querying merges by sheet

```php
$merges = BoqSheetMerge::where('boq_sheet_id', $sheetId)
    ->orderBy('created_at', 'desc')
    ->get();
```

### Checking if entries were merged

```php
$merge = BoqSheetMerge::where('boq_sheet_id', $sheetId)
    ->whereJsonContains('boq_sheet_entry_ids', $entryId)
    ->first();

if ($merge) {
    // Entry was part of a merge
    $mergeMetadata = $merge->extra_fields;
}
```

### Updating merge metadata

```php
$merge->extra_fields = array_merge($merge->extra_fields, [
    'status' => 'completed',
    'completed_at' => now()->toISOString()
]);
$merge->save();
```

## Architecture Notes

...