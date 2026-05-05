---
name: BoqEntryController
description: Laravel HTTP controller for BOQ (Bill of Quantities) entry management - handles all HTTP requests for BOQ entry operations
type: entity
title: "BoqEntryController"
---

# BoqEntryController

## Architectural Purpose

`BoqEntryController` (located in `App\Http\Controllers\Buyer\`) is the primary HTTP endpoint handler for all BOQ entry operations. This controller serves as the API gateway for:

- **Entry CRUD**: Read, update, and delete BOQ entries
- **Entry creation**: Add entries from quotations or directly from products
- **Bulk operations**: Create multiple entries at once
- **Ordering**: Reorder entries within a sheet
- **Cell styling**: Update cell colors for dynamic columns
- **Sheet transfer**: Move entries between sheets

This controller delegates business logic to [BoqSheetEntryService](./BoqSheetEntryService.md), following the thin controller pattern.

## Controller Dependencies

```php
public function __construct(private BoqSheetEntryService $boqSheetEntryService)
{
}
```

- **BoqSheetEntryService**: Handles all entry-related business logic

## API Endpoints

### `GET /projects/{project}/boq-sheets/{boqSheet}/entries` - `index()`

**Purpose:** Retrieve all entries for a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Behavior:**
1. Validates buyer ownership of project and sheet
2. Loads entries with sheet merges
3. Orders by `entry_order` ASC, then `created_at` DESC
4. Returns entries as `BoqEntryResource` collection

**Response:**
```json
{
  "status": "success",
  "message": "BOQ entries retrieved successfully",
  "data": [
    {
      "id": 1,
      "rfq_code": "RFQ-001",
      "item_name": "Portland Cement",
      "unit": "kg",
      "unit_price": 15.50,
      "quantity": 1000,
      "amount": 15500.00,
      "dynamic_values": {
        "item_code": "MAT-001"
      },
      "cell_colors": {
        "item_code": "#FF0000"
      }
    }
  ]
}
```

### `GET /projects/{project}/boq-sheets/{boqSheet}/entries/{boqEntry}` - `show()`

**Purpose:** Get a specific BOQ entry with all relationships.

**Authorization:** Requires authenticated buyer with ownership of the project, sheet, and entry.

**Behavior:**
- Loads entry with all related entities (sheet, project, product, quotation, RFQ, vendor, buyer, user)

**Response:**
```json
{
  "status": "success",
  "message": "BOQ entry retrieved successfully",
  "data": {
    "id": 1,
    "rfq_code": "RFQ-001",
    "item_name": "Portland Cement",
    "unit": "kg",
    "unit_price": 15.50,
    "quantity": 1000,
    "amount": 15500.00,
    "dynamic_values": { /* ... */ },
    "cell_colors": { /* ... */ },
    "boqSheet": { /* ... */ },
    "project": { /* ... */ },
    "product": { /* ... */ },
    "quotation": { /* ... */ },
    "rfq": { /* ... */ },
    "vendor": { /* ... */ },
    "buyer": { /* ... */ },
    "user": { /* ... */ }
  }
}
```

### `PUT /projects/{project}/boq-sheets/{boqSheet}/entries/{boqEntry}` - `update()`

**Purpose:** Update a BOQ entry's extra columns (dynamic values and cell colors only).

**Authorization:** Requires authenticated buyer with ownership of the project, sheet, and entry.

**Request Body:**
```json
{
  "dynamic_values": {
    "item_code": "MAT-002",
    "specification": "Grade 42.5"
  },
  "cell_colors": {
    "item_code": "#00FF00",
    "specification": "#FFFF00"
  }
}
```

**Validation:**
- `dynamic_values`: Nullable, array
- `cell_colors`: Nullable, array

**Behavior:**
1. Validates ownership
2. Delegates to `BoqSheetEntryService::storeOrUpdate()`
3. Only updates extra columns, not fixed columns

**Response:**
```json
{
  "status": "success",
  "message": "Entry updated successfully",
  "data": { /* BoqEntryResource */ }
}
```

**Note:** Fixed columns (item_name, unit_price, quantity, etc.) are updated through different methods, not this one.

### `DELETE /projects/{project}/boq-sheets/{boqSheet}/entries/{boqEntry}` - `destroy()`

**Purpose:** Delete a BOQ entry.

**Authorization:** Requires authenticated buyer with ownership of the project, sheet, and entry.

**Behavior:**
1. Validates ownership
2. Delegates to `BoqSheetEntryService::deleteEntryFromBoqSheet()`
3. Returns success or error

**Response:**
```json
{
  "status": "success",
  "message": "BOQ entry deleted successfully"
}
```

### `POST /boq-entries/add-to-sheet` - `addEntryToBoqSheet()`

**Purpose:** Add an entry to a BOQ sheet from a quotation.

**Authorization:** Requires authenticated buyer.

**Request Body:**
```json
{
  "project_id": 1,
  "boq_sheet_id": 1,
  "quotation_id": 5
}
```

**Validation:**
- `project_id`: Required, exists in `projects`
- `boq_sheet_id`: Required, exists in `boq_sheets`
- `quotation_id`: Required, exists in `quotations`

**Behavior:**
1. Validates quotation belongs to project
2. Validates sheet belongs to project
3. Validates project and sheet belong to buyer
4. Validates quotation belongs to buyer
5. Delegates to `BoqSheetEntryService::addEntryToBoqSheet()`

**Response:**
```json
{
  "status": "success",
  "message": "Entry added to BOQ sheet successfully",
  "data": { /* BoqEntryResource */ }
}
```

### `POST /boq-entries/add-direct` - `addDirectEntryToBoqSheet()`

**Purpose:** Add an entry directly from a product to a BOQ sheet.

**Authorization:** Requires authenticated buyer.

**Request Body:**
```json
{
  "project_id": 1,
  "boq_sheet_id": 1,
  "product_id": 10,
  "quantity": 100
}
```

**Validation:**
- `project_id`: Required, exists in `projects`
- `boq_sheet_id`: Required, exists in `boq_sheets`
- `product_id`: Required, exists in `products`
- `quantity`: Required, numeric, min 0

**Behavior:**
1. Validates sheet belongs to project
2. Delegates to `BoqSheetEntryService::addDirectEntryToBoqSheet()`

**Response:**
```json
{
  "status": "success",
  "message": "Direct entry added to BOQ sheet successfully",
  "data": { /* BoqEntryResource */ }
}
```

### `PUT /projects/{project}/boq-sheets/{boqSheet}/entries/{boqEntry}/cell-colors` - `updateCellColors()`

**Purpose:** Update cell colors for a specific entry.

**Authorization:** Requires authenticated buyer with ownership of the project, sheet, and entry.

**Request Body:**
```json
{
  "cell_colors": {
    "item_code": "#FF0000",
    "specification": "#00FF00"
  }
}
```

**Validation:**
- `cell_colors`: Required, array

**Behavior:**
1. Validates ownership
2. Filters cell colors to only include dynamic columns
3. Returns error if no valid dynamic columns found
4. Updates entry with filtered colors

**Response:**
```json
{
  "status": "success",
  "message": "Cell colors updated successfully",
  "data": { /* BoqEntryResource */ }
}
```

**Helper Method:**
```php
private function filterCellColorsForDynamicColumns(array $cellColors, BoqSheet $boqSheet): array
{
    $extraColumns = $boqSheet->extra_columns
        ? array_map('trim', explode(',', $boqSheet->extra_columns))
        : [];

    $filtered = [];
    foreach ($cellColors as $columnName => $color) {
        if (in_array($columnName, $extraColumns)) {
            $filtered[$columnName] = $color;
        }
    }

    return $filtered;
}
```

### `POST /projects/{project}/boq-sheets/{boqSheet}/entries/exchange-order` - `exchangeEntryOrder()`

**Purpose:** Swap the order of two entries within a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "source_boq_entry_id": 1,
  "target_boq_entry_id": 5
}
```

**Validation:**
- `source_boq_entry_id`: Required, integer, exists in `boq_entries`
- `target_boq_entry_id`: Required, integer, exists in `boq_entries`

**Behavior:**
1. Validates ownership
2. Validates both entries belong to the sheet
3. Validates source and target are different
4. **Uses transaction** with row locking
5. Rebuilds entire sequence with source moved to target position

**Transaction Logic:**
```php
DB::transaction(function () use ($boqSheet, $sourceBoqEntry, $targetBoqEntry): void {
    // Lock entries and rebuild exact sequence
    $orderedIds = BoqEntry::query()
        ->where('boq_sheet_id', $boqSheet->id)
        ->orderByRaw('COALESCE(entry_order, 2147483647) ASC')
        ->orderBy('id')
        ->lockForUpdate()
        ->pluck('id')
        ->values();

    $sourceIndex = $orderedIds->search($sourceBoqEntry->id);
    $targetIndex = $orderedIds->search($targetBoqEntry->id);

    $ids = $orderedIds->all();
    $sourceId = $ids[$sourceIndex];
    array_splice($ids, $sourceIndex, 1);
    array_splice($ids, $targetIndex, 0, [$sourceId]);

    foreach ($ids as $index => $id) {
        BoqEntry::query()->where('id', $id)->update(['entry_order' => $index + 1]);
    }
});
```

**Response:**
```json
{
  "status": "success",
  "message": "BOQ entry order updated successfully",
  "data": { /* BoqEntryResource */ }
}
```

**Good Practice:** This method correctly uses `DB::transaction()` with `lockForUpdate()` to prevent race conditions.

### `POST /projects/{project}/boq-sheets/{boqSheet}/entries/bulk` - `bulkStore()`

**Purpose:** Create multiple BOQ entries at once.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "entries": [
    {
      "rfq_code": "RFQ-001",
      "item_name": "Portland Cement",
      "unit": "kg",
      "unit_price": 15.50,
      "quantity": 1000,
      "vat_tax": 0,
      "dynamic_values": {
        "item_code": "MAT-001"
      },
      "cell_colors": {
        "item_code": "#FF0000"
      }
    },
    {
      "rfq_code": "RFQ-002",
      "item_name": "Steel Rebar",
      "unit": "ton",
      "unit_price": 500.00,
      "quantity": 10,
      "vat_tax": 0
    }
  ]
}
```

**Validation:**
- `entries`: Required, array, min 1
- Each entry validates individual fields

**Behavior:**
1. Validates ownership
2. Calculates amount and total for each entry
3. Filters cell colors to only include dynamic columns
4. Uses `BoqEntry::insert()` for bulk insert
5. Returns created entries

**Response:**
```json
{
  "status": "success",
  "message": "BOQ entries created successfully",
  "data": [
    { /* BoqEntryResource */ },
    { /* BoqEntryResource */ }
  ],
  "code": 201
}
```

**Tech Debt:**
- **NO TRANSACTION**: Bulk insert is not wrapped in a transaction
- If insert fails, partial data may be inserted
- No rollback mechanism

**Recommended Fix:**
```php
DB::transaction(function () use ($entries) {
    BoqEntry::insert($entries);
});
```

### `DELETE /projects/{project}/boq-sheets/{boqSheet}/entries/{boqEntry}/delete` - `deleteEntryFromBoqSheet()`

**Purpose:** Delete a BOQ entry (alternative endpoint).

**Authorization:** Requires authenticated buyer with ownership of the project, sheet, and entry.

**Behavior:**
- Delegates to `BoqSheetEntryService::deleteEntryFromBoqSheet()`

**Response:**
```json
{
  "status": "success",
  "message": "BOQ entry deleted successfully"
}
```

### `POST /projects/{project}/boq-sheets/{boqSheet}/entries/{boqEntry}/exchange-sheet` - `exchangeEntrySheet()`

**Purpose:** Move an entry to a different BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project, sheet, and entry.

**Behavior:**
- Delegates to `BoqSheetEntryService::exchangeEntrySheet()`

**Response:**
```json
{
  "status": "success",
  "message": "Entry moved to different sheet successfully",
  "data": { /* BoqEntryResource */ }
}
```

## Authorization Pattern

All methods follow this authorization pattern:

```php
$buyer = $this->currentBuyer();
if (!$buyer) {
    return $this->error('Buyer profile not found.', [], 404);
}

// Verify project, sheet, and entry belong to buyer
if ($project->buyer_id !== $buyer->id
    || $boqSheet->project_id !== $project->id
    || $boqEntry->boq_sheet_id !== $boqSheet->id) {
    return $this->error('BOQ entry not found.', [], 404);
}
```

**Helper Method:**
```php
private function currentBuyer()
{
    return JWTAuth::user()?->buyer ?? null;
}
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No transaction in `bulkStore()` | HIGH | Partial inserts on failure | Wrap in `DB::transaction()` |
| Commented out `store()` method | MEDIUM | Code confusion | Remove or implement |
| No rate limiting | LOW | Potential abuse | Add rate limiting middleware |
| No input sanitization | LOW | XSS risk | Add sanitization middleware |

## Cross-References

- [BoqSheetEntryService](./BoqSheetEntryService.md) - Business logic for entry operations
- [BoqEntry-Model](./BoqEntryModel.md) - Data model for entries
- [BoqSheetController](./BoqSheetController.md) - Controller for sheets
- [BoqEntryResource](./BoqEntryResource.md) - API resource for serialization

## Usage Examples

### Getting all entries for a sheet

```bash
GET /api/projects/1/boq-sheets/1/entries
Authorization: Bearer {jwt_token}
```

### Updating an entry's extra columns

```bash
PUT /api/projects/1/boq-sheets/1/entries/1
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "dynamic_values": {
    "item_code": "MAT-002",
    "specification": "Grade 42.5"
  },
  "cell_colors": {
    "item_code": "#00FF00"
  }
}
```

### Adding entry from quotation

```bash
POST /api/boq-entries/add-to-sheet
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "project_id": 1,
  "boq_sheet_id": 1,
  "quotation_id": 5
}
```

### Adding direct entry from product

```bash
POST /api/boq-entries/add-direct
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "project_id": 1,
  "boq_sheet_id": 1,
  "product_id": 10,
  "quantity": 100
}
```

### Swapping entry order

```bash
POST /api/projects/1/boq-sheets/1/entries/exchange-order
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "source_boq_entry_id": 1,
  "target_boq_entry_id": 5
}
```

### Bulk creating entries

```bash
POST /api/projects/1/boq-sheets/1/entries/bulk
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "entries": [
    {
      "item_name": "Portland Cement",
      "unit": "kg",
      "unit_price": 15.50,
      "quantity": 1000
    },
    {
      "item_name": "Steel Rebar",
      "unit": "ton",
      "unit_price": 500.00,
      "quantity": 10
    }
  ]
}
```

### Updating cell colors

```bash
PUT /api/projects/1/boq-sheets/1/entries/1/cell-colors
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "cell_colors": {
    "item_code": "#FF0000",
    "specification": "#00FF00"
  }
}
```
