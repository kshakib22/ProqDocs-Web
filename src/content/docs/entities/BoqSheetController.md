---
name: BoqSheetController
description: Laravel HTTP controller for BOQ (Bill of Quantities) sheet management - handles all HTTP requests for BOQ sheet operations
type: entity
title: "BoqSheetController"
---

# BoqSheetController

## Architectural Purpose

`BoqSheetController` (located in `App\Http\Controllers\Buyer\`) is the primary HTTP endpoint handler for all BOQ sheet operations. This controller serves as the API gateway for:

- **Sheet CRUD**: Create, read, update, and delete BOQ sheets
- **Sheet ordering**: Reorder sheets within a project
- **Extra column management**: Add, rename, and delete dynamic columns
- **Merge operations**: Handle Excel-style cell merging for dynamic columns
- **Export functionality**: Export sheets to Excel format
- **Authorization**: Enforce buyer ownership and access control

This controller delegates business logic to [BoqSheetService](./BoqSheetService.md) and [BoqSheetMergeService](./BoqSheetMergeService.md), following the thin controller pattern.

## Controller Dependencies

```php
public function __construct(
    private BoqSheetService $boqSheetService,
    private BoqSheetMergeService $boqSheetMergeService
) {
}
```

- **BoqSheetService**: Handles sheet creation, extra column operations
- **BoqSheetMergeService**: Handles merge operations for dynamic columns

## API Endpoints

### `GET /projects/{project}/boq-sheets` - `index()`

**Purpose:** Retrieve all BOQ sheets for a project with the first sheet pre-selected.

**Authorization:** Requires authenticated buyer with ownership of the project.

**Behavior:**
1. Validates buyer ownership of the project
2. Loads all projects with their BOQ sheets
3. Selects the first sheet (or creates "Sheet 1" if none exists)
4. If `sheet_id` query parameter provided, selects that sheet instead
5. Returns selected sheet, all sheets, project, and all projects

**Response Structure:**
```json
{
  "selected_sheet": { /* BoqSheetResource */ },
  "sheets": [
    {
      "id": 1,
      "sheet_name": "Foundation Works",
      "project_id": 1,
      "entries_sum_total_amount": 15000.00
    }
  ],
  "project": { /* Project */ },
  "projects": [ /* All buyer's projects */ ]
}
```

**Tech Debt:**
- Creates "Sheet 1" automatically if no sheets exist - may not be desired behavior
- No validation on auto-created sheet name
- Uses `logger($request->all())` which logs all request data (potential security issue)

### `GET /projects/{project}/boq-sheets/list` - `getBoqSheetsForProject()`

**Purpose:** Get a simplified list of BOQ sheets for a project.

**Authorization:** Requires authenticated buyer with ownership of the project.

**Response:**
```json
[
  {
    "id": 1,
    "sheet_name": "Foundation Works",
    "project_id": 1
  }
]
```

### `POST /projects/{project}/boq-sheets` - `store()`

**Purpose:** Create a new BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project.

**Request Body:**
```json
{
  "sheet_name": "Foundation Works"
}
```

**Validation:**
- `sheet_name`: Required, string, max 255 characters

**Behavior:**
1. Validates buyer ownership
2. Delegates to `BoqSheetService::createBoqSheet()`
3. Returns created sheet with 201 status

**Response:**
```json
{
  "status": "success",
  "message": "Boq sheet created successfully",
  "data": { /* BoqSheetResource */ },
  "code": 201
}
```

### `PUT /projects/{project}/boq-sheets/{boqSheet}` - `update()`

**Purpose:** Update a BOQ sheet name.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "sheet_name": "Updated Sheet Name"
}
```

**Validation:**
- `sheet_name`: Required, string, max 255 characters

**Response:**
```json
{
  "status": "success",
  "message": "BOQ sheet updated successfully",
  "data": { /* BoqSheetResource */ }
}
```

### `GET /projects/{project}/boq-sheets/{boqSheet}` - `show()`

**Purpose:** Get a specific BOQ sheet with all entries and relationships.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Behavior:**
- Loads sheet with entries, products, vendors, and merges
- Returns complete sheet data

**Response:**
```json
{
  "status": "success",
  "message": "BOQ sheet retrieved successfully",
  "data": { /* BoqSheetResource with entries */ }
}
```

### `POST /projects/{project}/boq-sheets/exchange-order` - `exchangeSheetOrder()`

**Purpose:** Swap the order of two BOQ sheets within a project.

**Authorization:** Requires authenticated buyer with ownership of the project.

**Request Body:**
```json
{
  "old_sheet_id": 1,
  "intended_sheet_id": 2
}
```

**Validation:**
- `old_sheet_id`: Required, integer, exists in `boq_sheets`
- `intended_sheet_id`: Required, integer, exists in `boq_sheets`

**Behavior:**
1. Validates both sheets belong to the project
2. Swaps the `sheet_order` values
3. Returns success

**Tech Debt:**
- **NO TRANSACTION**: The order swap is not wrapped in a transaction
- If one update fails, the other may succeed, leaving inconsistent state
- No locking mechanism to prevent race conditions

**Recommended Fix:**
```php
DB::transaction(function () use ($oldSheet, $intendedSheet) {
    $intended_order = $intendedSheet->sheet_order;
    $old_order = $oldSheet->sheet_order;
    $intendedSheet->update(['sheet_order' => $old_order]);
    $oldSheet->update(['sheet_order' => $intended_order]);
});
```

### `DELETE /projects/{project}/boq-sheets/{boqSheet}` - `destroy()`

**Purpose:** Delete a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Validation:**
- Sheet must have no entries (returns 404 if entries exist)

**Behavior:**
1. Validates ownership
2. Checks if sheet has entries
3. Deletes sheet (cascade deletes entries and merges via database/model hooks)

**Response:**
```json
{
  "status": "success",
  "message": "BOQ sheet deleted successfully"
}
```

### `PUT /projects/{project}/boq-sheets/{boqSheet}/cell-colors` - `updateCellColors()`

**Purpose:** Update cell colors for a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "cell_colors": {
    "header": {
      "rfq_code": "#ff0000"
    }
  }
}
```

**Validation:**
- `cell_colors`: Required, array

**Response:**
```json
{
  "status": "success",
  "message": "Cell colors updated successfully",
  "data": { /* BoqSheetResource */ }
}
```

### `POST /projects/{project}/boq-sheets/{boqSheet}/extra-columns` - `addExtraColumn()`

**Purpose:** Add a new dynamic column to a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "column_name": "item_code"
}
```

**Behavior:**
1. Validates ownership
2. Delegates to `BoqSheetService::addExtraColumns()`
3. Returns updated sheet

**Response:**
```json
{
  "status": "success",
  "message": "Extra column added successfully",
  "data": { /* BoqSheetResource */ }
}
```

### `PUT /projects/{project}/boq-sheets/{boqSheet}/extra-columns/rename` - `renameColumn()`

**Purpose:** Rename an existing dynamic column.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "old_column_name": "item_code",
  "new_column_name": "item_number"
}
```

**Behavior:**
1. Validates ownership
2. Delegates to `BoqSheetService::updateExtraColumnName()`
3. Updates all entries and merges that reference the old column name

**Response:**
```json
{
  "status": "success",
  "message": "Extra column name updated successfully",
  "data": { /* BoqSheetResource */ }
}
```

### `DELETE /projects/{project}/boq-sheets/{boqSheet}/extra-columns` - `deleteExtraColumn()`

**Purpose:** Delete a dynamic column from a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "column_name": "item_code"
}
```

**Behavior:**
1. Validates ownership
2. Delegates to `BoqSheetService::deleteExtraColumn()`
3. Removes column from sheet and all entries
4. Cleans up affected merges

**Response:**
```json
{
  "status": "success",
  "message": "Extra column deleted successfully",
  "data": { /* BoqSheetResource */ }
}
```

### `GET /projects/{project}/boq-sheets/{boqSheet}/merges` - `listExtraFieldMerges()`

**Purpose:** List all merge configurations for a BOQ sheet.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Behavior:**
- Delegates to `BoqSheetMergeService::listForSheet()`

**Response:**
```json
{
  "status": "success",
  "message": "Merges retrieved successfully",
  "data": [ /* Array of merge configurations */ ]
}
```

### `POST /projects/{project}/boq-sheets/{boqSheet}/merges` - `storeExtraFieldMerge()`

**Purpose:** Create a new merge configuration (Excel-style cell merging).

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "extra_fields": ["item_code", "specification"],
  "boq_sheet_entry_ids": [1, 2, 3]
}
```

**Behavior:**
- Creates a cartesian product of entries × fields
- Minimum 2 cells required
- Delegates to `BoqSheetMergeService::store()`

**Response:**
```json
{
  "status": "success",
  "message": "Merge created successfully",
  "data": { /* BoqSheetMergeResource */ }
}
```

### `PUT /projects/{project}/boq-sheets/{boqSheet}/merges/{boqSheetMerge}` - `updateExtraFieldMerge()`

**Purpose:** Update an existing merge configuration.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Request Body:**
```json
{
  "extra_fields": ["item_code"],
  "boq_sheet_entry_ids": [1, 2]
}
```

**Behavior:**
- Delegates to `BoqSheetMergeService::update()`

**Response:**
```json
{
  "status": "success",
  "message": "Merge updated successfully",
  "data": { /* BoqSheetMergeResource */ }
}
```

### `DELETE /projects/{project}/boq-sheets/{boqSheet}/merges/{boqSheetMerge}` - `destroyExtraFieldMerge()`

**Purpose:** Delete a merge configuration.

**Authorization:** Requires authenticated buyer with ownership of the project and sheet.

**Behavior:**
- Delegates to `BoqSheetMergeService::destroy()`

**Response:**
```json
{
  "status": "success",
  "message": "Merge deleted successfully"
}
```

### `GET /projects/{project}/boq-sheets/export` - `exportProjectBoqSheets()`

**Purpose:** Export all BOQ sheets of a project to an Excel file.

**Authorization:** Currently commented out - no authorization check.

**Behavior:**
- Generates Excel file with one sheet per BOQ sheet
- Downloads file with timestamp in filename

**Tech Debt:**
- **NO AUTHORIZATION**: Authorization checks are commented out
- Anyone with the URL can export any project's BOQ sheets
- Should be uncommented and enforced

**Recommended Fix:**
```php
$buyer = $this->currentBuyer();
if (!$buyer) {
    return $this->error('Buyer profile not found.', [], 404);
}

if ($project->buyer_id !== $buyer->id) {
    return $this->error('Project not found.', [], 404);
}
```

### `GET /projects-with-boq-sheets` - `getProjectsWithBoqSheets()`

**Purpose:** Get all projects with their BOQ sheets for the current buyer.

**Authorization:** Requires authenticated buyer.

**Response:**
```json
{
  "status": "success",
  "message": "Projects with BOQ sheets fetched successfully",
  "data": [ /* ProjectSheetResource collection */ ]
}
```

## Authorization Pattern

All methods follow this authorization pattern:

```php
$buyer = $this->currentBuyer();
if (!$buyer) {
    return $this->error('Buyer profile not found.', [], 404);
}

if ($project->buyer_id !== $buyer->id || $boqSheet->project_id !== $project->id) {
    return $this->error('BOQ sheet not found.', [], 404);
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
| No transaction in `exchangeSheetOrder()` | HIGH | Race conditions, inconsistent state | Wrap in `DB::transaction()` |
| No authorization in `exportProjectBoqSheets()` | HIGH | Security vulnerability | Uncomment and enforce auth |
| Auto-creates "Sheet 1" in `index()` | MEDIUM | Unwanted side effects | Make opt-in or remove |
| Logs all request data in `index()` | LOW | Potential security issue | Remove or sanitize logging |
| No rate limiting | LOW | Potential abuse | Add rate limiting middleware |

## Cross-References

- [BoqSheetService](./BoqSheetService.md) - Business logic for sheet operations
- [BoqSheetMergeService](./BoqSheetMergeService.md) - Business logic for merge operations
- [BoqSheet-Model](./BoqSheet-Model.md) - Data model for sheets
- [BoqEntryController](./BoqEntryController.md) - Controller for entries
- [BoqSheetResource](./BoqSheetResource.md) - API resource for serialization

## Usage Examples

### Creating a new sheet

```bash
POST /api/projects/1/boq-sheets
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "sheet_name": "Foundation Works"
}
```

### Adding an extra column

```bash
POST /api/projects/1/boq-sheets/1/extra-columns
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "column_name": "item_code"
}
```

### Renaming a column

```bash
PUT /api/projects/1/boq-sheets/1/extra-columns/rename
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "old_column_name": "item_code",
  "new_column_name": "item_number"
}
```

### Creating a merge

```bash
POST /api/projects/1/boq-sheets/1/merges
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "extra_fields": ["item_code", "specification"],
  "boq_sheet_entry_ids": [1, 2, 3]
}
```

### Exporting to Excel

```bash
GET /api/projects/1/boq-sheets/export
Authorization: Bearer {jwt_token}
```
