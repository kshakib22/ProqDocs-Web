---
name: BoqSheet-Model
description: Laravel Eloquent model for BOQ (Bill of Quantities) sheets - the primary container for construction project quantity data
type: entity
title: "BoqSheet Model"
---

# BoqSheet Model

## Architectural Purpose

`BoqSheet` is the root entity of the BOQ (Bill of Quantities) domain. It represents a complete quantity sheet for a construction project, serving as the container for all line items (entries) that define materials, labor, and equipment quantities. This model is the central hub that connects to:

- **Projects**: Each BOQ sheet belongs to a specific project
- **BoqEntry**: Contains the actual line items/rows of the quantity sheet
- **BoqSheetMerge**: Tracks merge operations when sheets are combined

The BOQ sheet is the foundational document used throughout the procurement lifecycle, feeding into [PurchaseListService](/ProqDocs-Web/entities/purchase-list-domain/) and RFQ generation workflows.

## Database Schema

| Column | Type | Purpose | Notes |
|--------|------|---------|-------|
| `id` | bigint | Primary key | Auto-incrementing |
| `sheet_name` | string | Sheet name | Human-readable identifier |
| `project_id` | bigint | Foreign key | Links to `projects` table, cascade delete |
| `extra_columns` | text | Dynamic schema | **FRAGILE**: Comma-separated column names |
| `sheet_order` | tinyint | Display order | Default 0, for UI sorting |
| `cell_colors` | text | Cell styling | Cast to array, stores color mappings |
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
6. Whitespace sensitivity - requires `trim()` to handle user input

**Recommended Fix:** Migrate to a JSON column or a dedicated `boq_sheet_columns` table with proper foreign key relationships.

### Schema Inconsistency: `name` vs `sheet_name`

**CRITICAL BUG:** The model uses `name` in code but the migration defines `sheet_name`:

```php
// Migration (database)
$table->string('sheet_name');

// Model (assumes 'name' exists)
// No explicit fillable/guarded for 'name', but 'name' is not in migration
```

This will cause:
- `name` attribute to be stored in `$attributes` but not persisted to database
- Silent data loss when saving
- Potential confusion in codebase

**Recommended Fix:** Update migration to use `name` or update all code to use `sheet_name`.

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
- **Cascade:** Database-level `onDelete('cascade')` on foreign key
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
- **Cascade:** Database-level `onDelete('cascade')` on foreign key
- **Usage:** Primary access point for iterating through quantity data
- **Related**: [BoqEntry Model](/ProqDocs-Web/entities/boq-entry-model/)

### `boqSheetMerges(): HasMany`

```php
public function boqSheetMerges(): HasMany
{
    return $this->hasMany(BoqSheetMerge::class);
}
```

- **Purpose:** Tracks merge operations where this sheet was involved
- **Cardinality:** One-to-many
- **Cascade:** Application-level deletion via `booted()` hook
- **Usage:** Audit trail for sheet combination operations
- **Related:** [BoqSheetMerge Model](/ProqDocs-Web/entities/boq-sheet-merge-model/)

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

**Critical Gap:** This hook does **NOT** delete the associated `BoqEntry` records. However, this is **intentional** because the database has a cascade delete on the foreign key:

```php
// Migration
$table->foreignId('boq_sheet_id')->constrained()->onDelete('cascade');
```

**Analysis:**
- `boqSheetMerges()` has no database-level FK (see [BoqSheetMerge Model](/ProqDocs-Web/entities/boq-sheet-merge-model/)), so application-level cleanup is required
- `entries()` has database-level cascade, so no application-level cleanup needed
- This is actually correct architecture - the hook only handles what the database cannot

## Attribute Casts

### `cell_colors` → Array

```php
protected $casts = [
    'cell_colors' => 'array',
];
```

Stores cell color mappings as JSON in the database, automatically cast to/from PHP arrays. Used for UI styling of the quantity sheet grid.

**Expected Structure:**
```json
{
  "header": {
    "rfq_code": "#ff0000",
    "item_name": "#00ff00"
  },
  "rows": {
    "1": {
      "item_name": "#ffff00"
    }
  }
}
```

## Accessors & Mutators

### `getExtraColumnsArrayAttribute()`

Converts the comma-separated `extra_columns` string to a trimmed array.

**Input:** `"item_code, specification, unit"`
**Output:** `["item_code", "specification", "unit"]`

**Edge Cases:**
- Empty string → `[]`
- Whitespace → Trimmed via `array_map('trim', ...)`
- Trailing comma → Creates empty string element (BUG)

### `setExtraColumnsArrayAttribute($value)`

Converts an array of column names back to a comma-separated string for storage.

**Input:** `["item_code", "specification", "unit"]`
**Output:** `"item_code,specification,unit"`

**Edge Cases:**
- Non-array input → Stored as-is (potential bug)
- Empty array → Empty string

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
3. Database cascade deletes all entries (FK constraint)
4. Model's booted() hook deletes boqSheetMerges (app-level)
5. Transaction commits
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| `extra_columns` as CSV | HIGH | Schema fragility, no validation | Migrate to JSON or dedicated table |
| `name` vs `sheet_name` mismatch | HIGH | Silent data loss | Align migration and model |
| Trailing comma bug in accessor | MEDIUM | Empty string elements | Add `array_filter` |
| No indexes on `extra_columns` | MEDIUM | Query performance | Add composite index if querying needed |
| No validation on `cell_colors` | LOW | Potential UI corruption | Add validation rules |
| Missing `sheet_order` in model | LOW | No explicit handling | Add to fillable if needed |

## Cross-References

- [BoqSheetService](/ProqDocs-Web/entities/boq-sheet-service/) - Business logic for sheet operations
- [BoqEntry Model](/ProqDocs-Web/entities/boq-entry-model/) - Line items contained within sheets
- [BoqSheetMerge Model](/ProqDocs-Web/entities/boq-sheet-merge-model/) - Merge operations tracking
- [PurchaseList Domain](/ProqDocs-Web/entities/purchase-list-domain/) - Downstream consumer of BOQ data
- [BoqSheetController](/ProqDocs-Web/entities/boq-sheet-controller/) - HTTP endpoint handler
- [BoqEntry BoqSheet Domain](/ProqDocs-Web/entities/boq-entry-boq-sheet-domain/) - Domain overview

## Usage Examples

### Creating a new sheet with extra columns

```php
$sheet = BoqSheet::create([
    'project_id' => $project->id,
    'sheet_name' => 'Foundation Works',
    'extra_columns' => 'item_code,specification,unit',
    'cell_colors' => ['header' => ['rfq_code' => '#FF0000']],
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
    ->orderBy('sheet_order')
    ->get();
```

### Updating extra columns

```php
$sheet->extra_columns_array = ['new_column', 'another_column'];
$sheet->save();
```
