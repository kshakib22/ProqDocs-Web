---
name: BoqSheetMergeService
description: Laravel service class for BOQ sheet merge operations - handles Excel-style cell merging for dynamic columns
type: entity
title: "BoqSheetMergeService"
---

# BoqSheetMergeService

## Architectural Purpose

`BoqSheetMergeService` is the business logic layer for BOQ sheet merge operations. This service encapsulates all operations related to Excel-style cell merging for dynamic columns:

- **Merge creation**: Creating new merge configurations
- **Merge updates**: Modifying existing merge configurations
- **Merge deletion**: Removing merge configurations
- **Merge listing**: Retrieving all merges for a sheet
- **Validation**: Ensuring merge data integrity

This service enables the BOQ system to support complex spreadsheet-like cell merging functionality, allowing users to merge cells across multiple entries and dynamic columns.

## Service Dependencies

```php
use App\Http\Resources\BoqSheetMergeResource;
use App\Models\BoqSheet;
use App\Models\BoqSheetMerge;
use App\Models\BoqEntry;
use App\Traits\ServiceResponder;
use Illuminate\Support\Facades\Validator;
```

- **ServiceResponder**: Trait for standardized API responses
- **BoqSheetMergeResource**: API resource for serialization
- **Validator**: Laravel validation facade

## Service Methods

### `store(BoqSheet $boqSheet, array $data)`

**Purpose:** Create a new merge configuration (Excel-style cell merging).

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$data`: Array containing `extra_fields` and `boq_sheet_entry_ids`

**Behavior:**
1. Validates input data
2. Gets extra columns from sheet
3. Validates all fields exist in extra_columns
4. Validates all entries belong to the sheet
5. Calculates cell count (entries × fields)
6. Validates minimum 2 cells required
7. **Uses transaction** for data consistency
8. Creates BoqSheetMerge record
9. Returns created merge

**Validation Rules:**
```php
[
    'extra_fields' => 'required|array|min:1',
    'extra_fields.*' => 'string',
    'boq_sheet_entry_ids' => 'required|array|min:1',
    'boq_sheet_entry_ids.*' => 'integer',
]
```

**Cell Count Calculation:**
```php
$cellCount = count($entryIds) * count($fields);
if ($cellCount < 2) {
    return $this->error('Merge must span at least 2 cells (entries × fields).', [], 422);
}
```

**Transaction Scope:**
```php
DB::transaction(function () use ($boqSheet, $fields, $entryIds) {
    $merge = BoqSheetMerge::create([
        'boq_sheet_id' => $boqSheet->id,
        'extra_fields' => $fields,
        'boq_sheet_entry_ids' => $entryIds,
    ]);
    return $merge;
});
```

**Good Practice:** This method correctly uses `DB::transaction()` to ensure data consistency.

**Response:**
```php
return $this->success('Merge created successfully', new BoqSheetMergeResource($merge), 201);
```

### `update(BoqSheet $boqSheet, BoqSheetMerge $boqSheetMerge, array $data)`

**Purpose:** Update an existing merge configuration.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$boqSheetMerge`: BoqSheetMerge instance to update
- `$data`: Array containing `extra_fields` and `boq_sheet_entry_ids`

**Behavior:**
1. Validates input data
2. Gets extra columns from sheet
3. Validates all fields exist in extra_columns
4. Validates all entries belong to the sheet
5. Calculates cell count
6. Validates minimum 2 cells required
7. **Uses transaction** for data consistency
8. Updates merge record
9. Returns updated merge

**Transaction Scope:**
```php
DB::transaction(function () use ($boqSheetMerge, $fields, $entryIds) {
    $boqSheetMerge->update([
        'extra_fields' => $fields,
        'boq_sheet_entry_ids' => $entryIds,
    ]);
});
```

**Good Practice:** This method correctly uses `DB::transaction()` to ensure data consistency.

**Response:**
```php
return $this->success('Merge updated successfully', new BoqSheetMergeResource($boqSheetMerge->fresh()), 200);
```

### `destroy(BoqSheet $boqSheet, BoqSheetMerge $boqSheetMerge)`

**Purpose:** Delete a merge configuration.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$boqSheetMerge`: BoqSheetMerge instance to delete

**Behavior:**
1. Validates merge belongs to sheet
2. **Uses transaction** for data consistency
3. Deletes merge record
4. Returns success

**Transaction Scope:**
```php
DB::transaction(function () use ($boqSheetMerge) {
    $boqSheetMerge->delete();
});
```

**Good Practice:** This method correctly uses `DB::transaction()` to ensure data consistency.

**Response:**
```php
return $this->success('Merge deleted successfully', [], 200);
```

### `listForSheet(BoqSheet $boqSheet)`

**Purpose:** List all merge configurations for a BOQ sheet.

**Parameters:**
- `$boqSheet`: BoqSheet instance

**Behavior:**
1. Queries all merges for the sheet
2. Returns as collection of `BoqSheetMergeResource`

**Response:**
```php
$merges = BoqSheetMerge::where('boq_sheet_id', $boqSheet->id)->get();
return $this->success('Merges retrieved successfully', BoqSheetMergeResource::collection($merges), 200);
```

## Merge Data Structure

### Cartesian Product Model

Merges are modeled as a cartesian product of entries × fields:

```
Entries: [1, 2, 3]
Fields: ["item_code", "specification"]

Resulting Cells:
- Entry 1, Field "item_code"
- Entry 1, Field "specification"
- Entry 2, Field "item_code"
- Entry 2, Field "specification"
- Entry 3, Field "item_code"
- Entry 3, Field "specification"

Total: 6 cells (3 entries × 2 fields)
```

### Minimum Cell Requirement

A merge must span at least 2 cells:

- **Valid**: 1 entry × 2 fields = 2 cells
- **Valid**: 2 entries × 1 field = 2 cells
- **Invalid**: 1 entry × 1 field = 1 cell

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No conflict detection | MEDIUM | Overlapping merges possible | Add overlap validation |
| No merge history | LOW | Limited audit trail | Add merge change tracking |
| No merge preview | LOW | UX limitation | Add preview endpoint |

## Cross-References

- [BoqSheetMerge-Model](/entities/boqsheetmergemodel) - Data model for merges
- [BoqSheet-Model](/entities/boqsheet-model) - Parent sheet for merges
- BoqEntry-Model - Entries included in merges
- [BoqSheetController](/entities/boqsheetcontroller) - Controller that uses this service
- [BoqSheetMergeResource](/entities/boqsheetmergeresource) - API resource for serialization

## Usage Examples

### Creating a merge

```php
$result = $boqSheetMergeService->store($boqSheet, [
    'extra_fields' => ['item_code', 'specification'],
    'boq_sheet_entry_ids' => [1, 2, 3]
]);

if ($result['status'] === 'success') {
    $merge = $result['data'];
}
```

### Updating a merge

```php
$result = $boqSheetMergeService->update($boqSheet, $boqSheetMerge, [
    'extra_fields' => ['item_code'],
    'boq_sheet_entry_ids' => [1, 2]
]);

if ($result['status'] === 'success') {
    $updatedMerge = $result['data'];
}
```

### Deleting a merge

```php
$result = $boqSheetMergeService->destroy($boqSheet, $boqSheetMerge);

if ($result['status'] === 'success') {
    // Merge deleted
}
```

### Listing merges for a sheet

```php
$result = $boqSheetMergeService->listForSheet($boqSheet);

if ($result['status'] === 'success') {
    $merges = $result['data'];
}
```

## Architecture Notes

...