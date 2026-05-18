---
name: BoqSheetService
description: Laravel service class for BOQ (Bill of Quantities) sheet business logic - handles sheet creation and extra column management
type: entity
title: "BoqSheetService"
---

# BoqSheetService

## Architectural Purpose

`BoqSheetService` is the business logic layer for BOQ sheet operations. This service encapsulates all complex operations related to:

- **Sheet creation**: Creating new BOQ sheets with automatic ordering
- **Extra column management**: Adding, renaming, and deleting dynamic columns
- **Data integrity**: Ensuring consistency between sheets and their entries
- **Merge cleanup**: Cleaning up merge records when columns are modified

This service follows the service layer pattern, keeping controllers thin and business logic centralized.

## Service Dependencies

```php
use App\Http\Resources\BoqSheetResource;
use App\Models\BoqSheet;
use App\Models\BoqEntry;
use App\Models\Project;
use App\Models\Buyer;
use App\Models\Vendor;
use App\Models\Rfq;
use App\Models\Quotation;
use App\Models\QutationService;
use App\Traits\ServiceResponder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Validator;
```

- **ServiceResponder**: Trait for standardized API responses
- **BoqSheetResource**: API resource for serialization
- **Log**: Laravel logging facade
- **DB**: Database facade (imported but not used)

## Service Methods

### `validateData(array $data)`

**Purpose:** Validate sheet creation data.

**Parameters:**
- `$data`: Array of input data

**Validation Rules:**
```php
[
    'sheet_name' => 'required|string|min:4|max:50',
]
```

**Returns:** Validator instance

**Usage:**
```php
$validator = $this->validateData($data);
if ($validator->fails()) {
    return $this->error('Validation failed', $validator->errors()->toArray(), 422);
}
```

### `createBoqSheet(Buyer $buyer, Project $project, array $data)`

**Purpose:** Create a new BOQ sheet with automatic ordering.

**Parameters:**
- `$buyer`: Buyer instance (for authorization)
- `$project`: Project instance
- `$data`: Array containing `sheet_name`

**Behavior:**
1. Validates input data
2. Finds the last sheet in the project by `sheet_order`
3. Calculates new order (last order + 1, or 1 if no sheets exist)
4. Creates new sheet with calculated order
5. Returns success response with `BoqSheetResource`

**Tech Debt:**
- **NO TRANSACTION**: Sheet creation is not wrapped in a transaction
- If creation fails, no rollback mechanism
- No locking mechanism to prevent race conditions on `sheet_order`

**Recommended Fix:**
```php
DB::transaction(function () use ($project, $data) {
    $lastSheet = $project->boqSheets()
        ->orderBy('sheet_order', 'desc')
        ->lockForUpdate()
        ->first();
    $sheetOrder = $lastSheet ? $lastSheet->sheet_order + 1 : 1;
    $boqSheet = BoqSheet::create([
        'project_id' => $project->id,
        'sheet_name' => $data['sheet_name'],
        'sheet_order' => $sheetOrder
    ]);
    return $boqSheet;
});
```

**Response:**
```php
return $this->success('Boq sheet created successfully', new BoqSheetResource($boqSheet), 201);
```

### `addExtraColumns(BoqSheet $boqSheet, array $data)`

**Purpose:** Add a new dynamic column to a BOQ sheet.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$data`: Array containing `column_name`

**Behavior:**
1. Validates column name using `validateExtraColumns()`
2. Gets existing columns as array from comma-separated string
3. Checks if column already exists (returns error if duplicate)
4. Adds new column to array
5. Converts back to comma-separated string
6. Saves sheet
7. Returns updated sheet

**Validation Rules:**
```php
[
    'column_name' => [
        'required',
        'string',
        'min:4',
        'max:50',
        function ($attribute, $value, $fail) use ($boqSheet) {
            $extraColumns = $boqSheet->extra_columns
                ? array_map('trim', explode(',', $boqSheet->extra_columns))
                : [];
            if (in_array($value, $extraColumns)) {
                $fail('A column with the same name already exists in the extra_columns of this BoqSheet.');
            }
        },
    ],
]
```

**Tech Debt:**
- **NO TRANSACTION**: Column addition is not wrapped in a transaction
- If save fails, no rollback mechanism

**Response:**
```php
return $this->success('Extra column added successfully', new BoqSheetResource($boqSheet->fresh()), 200);
```

### `validateExtraColumns($data, BoqSheet $boqSheet)`

**Purpose:** Validate extra column data.

**Parameters:**
- `$data`: Array containing `column_name`
- `$boqSheet`: BoqSheet instance for duplicate checking

**Returns:** Validator instance

**Validation Logic:**
- Required, string, min 4, max 50 characters
- Custom validation to check for duplicates in existing columns

### `updateExtraColumnName(BoqSheet $boqSheet, array $data)`

**Purpose:** Rename an existing extra column and update all references in entries and merges.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$data`: Array containing `old_column_name` and `new_column_name`

**Behavior:**
1. Validates both old and new column names
2. Checks if old column exists (returns 404 if not)
3. Checks if new name already exists (and is not the old name)
4. Updates column name in sheet's `extra_columns`
5. **Updates all BoqEntry records** that reference the old column:
   - Updates `dynamic_values` key
   - Updates `cell_colors` key
6. **Updates all BoqSheetMerge records** that reference the old column:
   - Updates `extra_fields` array
7. Returns updated sheet

**Tech Debt:**
- **NO TRANSACTION**: This is a **CRITICAL** issue - the operation updates multiple records across multiple tables without transaction protection
- If any update fails, data inconsistency will occur
- No locking mechanism to prevent concurrent modifications
- Each entry is saved individually (N+1 query problem)

**Recommended Fix:**
```php
DB::transaction(function () use ($boqSheet, $oldColumnName, $newColumnName) {
    // Update sheet
    $boqSheet->save();

    // Update entries in bulk
    BoqEntry::where('boq_sheet_id', $boqSheet->id)
        ->whereJsonContains('dynamic_values', $oldColumnName)
        ->update([
            'dynamic_values' => DB::raw("JSON_SET(dynamic_values, '$.$newColumnName', JSON_EXTRACT(dynamic_values, '$.$oldColumnName'))")
        ]);

    // Similar for cell_colors and merges
});
```

**Entry Update Logic:**
```php
foreach ($entries as $entry) {
    $updated = false;

    // Update dynamic_values
    if ($entry->dynamic_values && is_array($entry->dynamic_values)) {
        if (isset($entry->dynamic_values[$oldColumnName])) {
            $dynamicValues = $entry->dynamic_values;
            $dynamicValues[$newColumnName] = $dynamicValues[$oldColumnName];
            unset($dynamicValues[$oldColumnName]);
            $entry->dynamic_values = $dynamicValues;
            $updated = true;
        }
    }

    // Update cell_colors
    if ($entry->cell_colors && is_array($entry->cell_colors)) {
        if (isset($entry->cell_colors[$oldColumnName])) {
            $cellColors = $entry->cell_colors;
            $cellColors[$newColumnName] = $cellColors[$oldColumnName];
            unset($cellColors[$oldColumnName]);
            $entry->cell_colors = $cellColors;
            $updated = true;
        }
    }

    if ($updated) {
        $entry->save();
    }
}
```

**Merge Update Logic:**
```php
foreach ($boqSheet->boqSheetMerges()->get() as $merge) {
    $fields = $merge->extra_fields ?? [];
    $mergeUpdated = false;
    foreach ($fields as $i => $name) {
        if ($name === $oldColumnName) {
            $fields[$i] = $newColumnName;
            $mergeUpdated = true;
        }
    }
    if ($mergeUpdated) {
        $merge->extra_fields = array_values(array_unique($fields));
        $merge->save();
    }
}
```

**Response:**
```php
return $this->success(
    'Extra column name updated successfully',
    new BoqSheetResource($boqSheet->fresh(['boqSheetMerges'])),
    200
);
```

### `deleteExtraColumn(BoqSheet $boqSheet, array $data)`

**Purpose:** Delete an extra column from a BOQ sheet and remove all references in entries and merges.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$data`: Array containing `column_name`

**Behavior:**
1. Validates column name
2. Checks if column exists (returns 404 if not)
3. Removes column from sheet's `extra_columns`
4. **Updates all BoqEntry records** to remove references:
   - Removes from `dynamic_values`
   - Removes from `cell_colors`
5. **Updates all BoqSheetMerge records**:
   - Removes column from `extra_fields`
   - Deletes merge if no fields or entries remain
6. Returns updated sheet

**Tech Debt:**
- **NO TRANSACTION**: This is a **CRITICAL** issue - the operation updates multiple records across multiple tables without transaction protection
- If any update fails, data inconsistency will occur
- No locking mechanism to prevent concurrent modifications
- Each entry is saved individually (N+1 query problem)

**Entry Update Logic:**
```php
foreach ($entries as $entry) {
    $updated = false;

    // Remove from dynamic_values
    if ($entry->dynamic_values && is_array($entry->dynamic_values)) {
        if (isset($entry->dynamic_values[$columnName])) {
            $dynamicValues = $entry->dynamic_values;
            unset($dynamicValues[$columnName]);
            $entry->dynamic_values = $dynamicValues;
            $updated = true;
        }
    }

    // Remove from cell_colors
    if ($entry->cell_colors && is_array($entry->cell_colors)) {
        if (isset($entry->cell_colors[$columnName])) {
            $cellColors = $entry->cell_colors;
            unset($cellColors[$columnName]);
            $entry->cell_colors = $cellColors;
            $updated = true;
        }
    }

    if ($updated) {
        $entry->save();
    }
}
```

**Merge Update Logic:**
```php
foreach ($boqSheet->boqSheetMerges()->get() as $merge) {
    $fields = array_values(array_filter(
        $merge->extra_fields ?? [],
        fn ($f) => trim((string) $f) !== $columnName
    ));
    $entryIds = $merge->boq_sheet_entry_ids ?? [];
    $cellCount = count($entryIds) * max(count($fields), 1);

    // Delete merge if no fields or insufficient cells
    if (count($fields) < 1 || $cellCount < 2) {
        $merge->delete();
    } else {
        $merge->extra_fields = $fields;
        $merge->save();
    }
}
```

**Response:**
```php
return $this->success(
    'Extra column deleted successfully',
    new BoqSheetResource($boqSheet->fresh(['boqSheetMerges'])),
    200
);
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No transaction in `createBoqSheet()` | HIGH | Race conditions on `sheet_order` | Wrap in `DB::transaction()` with lock |
| No transaction in `addExtraColumns()` | MEDIUM | Partial updates on failure | Wrap in `DB::transaction()` |
| No transaction in `updateExtraColumnName()` | **CRITICAL** | Data inconsistency across tables | Wrap in `DB::transaction()` |
| No transaction in `deleteExtraColumn()` | **CRITICAL** | Data inconsistency across tables | Wrap in `DB::transaction()` |
| N+1 query in `updateExtraColumnName()` | MEDIUM | Performance issue | Use bulk update with JSON functions |
| N+1 query in `deleteExtraColumn()` | MEDIUM | Performance issue | Use bulk update with JSON functions |
| No locking for concurrent modifications | HIGH | Race conditions | Add `lockForUpdate()` |
| Unused `DB` import | LOW | Code confusion | Remove or use |

## Cross-References

- [BoqSheet-Model](/entities/boqsheet-model) - Data model for sheets
- BoqEntry-Model - Data model for entries
- BoqSheetMerge-Model - Data model for merges
- [BoqSheetController](/entities/boqsheetcontroller) - Controller that uses this service
- ServiceResponder - Trait for standardized responses

## Usage Examples

### Creating a new sheet

```php
$result = $boqSheetService->createBoqSheet($buyer, $project, [
    'sheet_name' => 'Foundation Works'
]);

if ($result['status'] === 'success') {
    $sheet = $result['data'];
}
```

### Adding an extra column

```php
$result = $boqSheetService->addExtraColumns($boqSheet, [
    'column_name' => 'item_code'
]);

if ($result['status'] === 'success') {
    $updatedSheet = $result['data'];
}
```

### Renaming a column

```php
$result = $boqSheetService->updateExtraColumnName($boqSheet, [
    'old_column_name' => 'item_code',
    'new_column_name' => 'item_number'
]);

if ($result['status'] === 'success') {
    $updatedSheet = $result['data'];
}
```

### Deleting a column

```php
$result = $boqSheetService->deleteExtraColumn($boqSheet, [
    'column_name' => 'item_code'
]);

if ($result['status'] === 'success') {
    $updatedSheet = $result['data'];
}
```

## Architecture Notes

...