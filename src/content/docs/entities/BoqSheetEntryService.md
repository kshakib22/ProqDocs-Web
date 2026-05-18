---
name: BoqSheetEntryService
description: Laravel service class for BOQ (Bill of Quantities) entry business logic - handles entry creation, deletion, and integration with PurchaseList domain
type: entity
title: "BoqSheetEntryService"
---

# BoqSheetEntryService

## Architectural Purpose

`BoqSheetEntryService` is the business logic layer for BOQ entry operations. This service encapsulates all complex operations related to:

- **Entry creation**: Adding entries from quotations or directly from products
- **Entry management**: Updating, deleting, and moving entries between sheets
- **PurchaseList integration**: Syncing entries with purchase orders and procurement workflow
- **Order management**: Maintaining entry order within sheets
- **Cell styling**: Adding colors to dynamic columns
- **Merge operations**: Creating Excel-style cell merges for dynamic columns

This service serves as the critical bridge between the BOQ domain and the procurement (PurchaseList) domain, ensuring data consistency across both systems.

## Service Dependencies

```php
use App\Http\Resources\BoqEntryResource;
use App\Http\Resources\RfqResource;
use App\Models\BoqSheet;
use App\Models\BoqEntry;
use App\Models\Project;
use App\Models\Buyer;
use App\Models\Vendor;
use App\Models\User;
use App\Models\Quotation;
use App\Models\Rfq;
use App\Models\Product;
use App\Models\PurchaseOrder;
use App\Traits\ServiceResponder;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
```

- **ServiceResponder**: Trait for standardized API responses
- **BoqSheetMergeService**: Handles merge operations
- **PurchaseListService**: Integration with procurement workflow
- **DB**: Database facade for transactions
- **Storage**: File storage for images
- **Auth**: Authentication facade

## Service Methods

### `validateData(array $data)`

**Purpose:** Validate entry creation data.

**Parameters:**
- `$data`: Array of input data

**Validation Rules:**
```php
[
    'boq_sheet_id' => 'required|exists:boq_sheets,id',
    'product_id' => 'required|exists:products,id',
    'quantity' => 'required|numeric|min:0',
]
```

**Returns:** Validator instance

### `addColors(BoqEntry $boqEntry, array $data)`

**Purpose:** Add colors to specific columns for a BoqEntry.

**Parameters:**
- `$boqEntry`: BoqEntry instance
- `$data`: Array of `['column_name' => 'color_hex']` mappings

**Behavior:**
1. Gets extra columns from parent sheet
2. Validates that all column names exist in extra_columns
3. Validates color format (hex color)
4. Updates entry's cell_colors
5. Returns updated entry

**Validation:**
- Column must exist in sheet's extra_columns
- Color must be valid hex format (e.g., #FF5599)

**Tech Debt:**
- **NO TRANSACTION**: Color update is not wrapped in a transaction

### `addMerge(BoqEntry $boqEntry, array $data)`

**Purpose:** Create a BoqSheetMerge for extra columns (Excel-style cell merging).

**Parameters:**
- `$boqEntry`: BoqEntry instance
- `$data`: Array containing `columns` and optional `boq_sheet_entry_ids`

**Behavior:**
1. Gets extra columns from parent sheet
2. Extracts column names from input (supports both `columns` array and flat string values)
3. Validates all columns exist in extra_columns
4. Defaults to current entry if no entry_ids provided
5. Delegates to `BoqSheetMergeService::store()`

**Input Formats:**
```php
// Format 1: columns array
['columns' => ['item_code', 'specification'], 'boq_sheet_entry_ids' => [1, 2]]

// Format 2: flat values
['item_code', 'specification', 'boq_sheet_entry_ids' => [1, 2]]
```

### `storeOrUpdate(BoqSheet $boqSheet, array $data, ?BoqEntry $boqEntry = null)`

**Purpose:** Store or update BoqEntry with dynamic values and cell colors.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$data`: Array of entry data
- `$boqEntry`: Optional BoqEntry instance (if provided, updates; otherwise creates)

**Behavior:**
1. Gets extra columns from sheet
2. Filters `dynamic_values` to only include valid columns
3. Filters `cell_colors` to only include valid columns with valid hex colors
4. Removes `merged_cells` from data (handled by merge API)
5. Updates or creates entry
6. Returns result

**Tech Debt:**
- **NO TRANSACTION**: Create/update is not wrapped in a transaction

### `addEntryToBoqSheet(BoqSheet $boqSheet, Quotation $quotation)`

**Purpose:** Add an entry to a BOQ sheet from a quotation and integrate with procurement workflow.

**Parameters:**
- `$boqSheet`: BoqSheet instance
- `$quotation`: Quotation instance

**Behavior:**
1. Validates quotation is in 'in_review' status
2. Loads RFQ and product data
3. Determines image source (quotation > RFQ > product)
4. **Uses transaction** for data consistency
5. Creates BoqEntry with calculated values
6. **Integrates with PurchaseList**: Calls `PurchaseListService::addToPurchaseListFromQuotation()`
7. **Rejects competing quotations**: Sets all other quotations for this RFQ to 'rejected'
8. **Updates RFQ status**: Sets RFQ to 'accepted'
9. **Updates quotation status**: Sets selected quotation to 'accepted'
10. Returns created entry

**Transaction Scope:**
```php
DB::beginTransaction();
try {
    // Create BoqEntry
    // Add to PurchaseList
    // Reject competing quotations
    // Update RFQ and quotation status
    DB::commit();
} catch (\Exception $e) {
    DB::rollBack();
}
```

**PurchaseList Integration:**
```php
$purchaseList = (new PurchaseListService())->addToPurchaseListFromQuotation($boqEntry, $quotation);
if($purchaseList['status'] == 'error'){
    DB::rollBack();
    return $this->error('Failed to add purchase list', [...$purchaseList]);
}
```

**Competing Quotation Rejection:**
```php
$rfq->quotations->filter(function($checkQuotation) use($quotation){
    return $checkQuotation->id !== $quotation->id;
})->map(function($cancelQuotation){
    $cancelQuotation->status = 'rejected';
    $cancelQuotation->save();
    return $cancelQuotation;
});
```

**Good Practice:** This method correctly uses `DB::transaction()` to ensure data consistency across multiple operations.

### `addDirectEntryToBoqSheet(Buyer $buyer, BoqSheet $boqSheet, $product_id, $quantity)`

**Purpose:** Add an entry directly from a product to a BOQ sheet (no quotation involved).

**Parameters:**
- `$buyer`: Buyer instance
- `$boqSheet`: BoqSheet instance
- `$product_id`: Product ID
- `$quantity`: Quantity to add

**Behavior:**
1. Loads product data
2. Determines image source
3. **Uses transaction** for data consistency
4. Calculates financial values using `bcmath`:
   - `amount = unit_price × quantity`
   - `vat_tax = amount × vat_rate / 100`
   - `total_amount = amount + vat_tax`
5. Creates BoqEntry with calculated values
6. **Integrates with PurchaseList**: Calls `PurchaseListService::addToPurchaseListDirect()`
7. Returns created entry

**Financial Calculations:**
```php
$amount = bcmul($product->unit_price, $quantity, 2);
$vat_tax = bcmul($amount * $product->vat_rate / 100, 2);
$total_amount = bcadd($amount, $vat_tax, 2);
```

**Good Practice:** Uses `bcmath` for precise financial calculations.

### `deleteEntryFromBoqSheet(BoqEntry $boqEntry)`

**Purpose:** Delete an entry from a BOQ sheet and handle all downstream effects.

**Parameters:**
- `$boqEntry`: BoqEntry instance

**Behavior:**
1. **Uses transaction** for data consistency
2. **Handles PurchaseList**: If entry has a purchase list:
   - Checks if purchase order exists and is not 'pending' (returns error if ordered)
   - Rejects associated quotation
   - Cancels and deletes purchase list
   - Recalculates purchase order costing
   - Deletes purchase order if no lists remain
3. **Updates entry order**: Shifts up all entries after the deleted one
4. Deletes entry
5. Returns success

**PurchaseList Cleanup:**
```php
$purchaseList = $boqEntry->purchaseList;
if($purchaseList){
    $purchaseOrder = $purchaseList->purchaseOrder;
    if($purchaseOrder && $purchaseOrder->status != 'pending'){
        return $this->error('You cannot delete an entry that has been ordered', [], 400);
    }

    $quotation = $purchaseList->quotation;
    if($quotation){
        $quotation->status = 'rejected';
        $quotation->save();
    }
    $purchaseList->status = 'cancelled';
    $purchaseList->save();
    $purchaseList->delete();

    if ($purchaseOrder) {
        (new PurchaseListService())->recalculatePurchaseOrderCosting($purchaseOrder);
        if($purchaseOrder->refresh()->purchase_lists->count() == 0){
            $purchaseOrder->status = 'cancelled';
            $purchaseOrder->save();
            $purchaseOrder->delete();
        }
    }
}
```

**Entry Order Update:**
```php
$sheetId = $boqEntry->boq_sheet_id ?? null;
$deletedOrder = (int) ($boqEntry->entry_order ?? 0);

if ($sheetId !== null && $deletedOrder > 0) {
    BoqEntry::query()
        ->where('boq_sheet_id', $sheetId)
        ->where('entry_order', '>', $deletedOrder)
        ->decrement('entry_order');
}
```

**Good Practice:** This method correctly uses `DB::transaction()` and handles all downstream effects.

**Tech Debt:**
- Duplicate catch block (lines 395-403)

### `exchangeEntrySheet(Project $project, BoqSheet $boqSheet, BoqEntry $boqEntry)`

**Purpose:** Move an entry to a different BOQ sheet.

**Parameters:**
- `$project`: Project instance
- `$boqSheet`: Source BoqSheet instance
- `$boqEntry`: BoqEntry instance to move

**Behavior:**
1. Validates `target_sheet_id` from request
2. Validates target sheet belongs to project
3. **Uses transaction** for data consistency
4. **Updates source sheet order**: Shifts up all entries after the moved one
5. **Updates PurchaseList**: If entry has a purchase list, updates its `boq_sheet_id`
6. **Moves entry**:
   - Updates `boq_sheet_id` to target sheet
   - Sets `entry_order` to end of target sheet
   - Clears `dynamic_values` and `cell_colors` (may not match target sheet's columns)
7. Returns success

**Transaction Scope:**
```php
DB::beginTransaction();
try {
    // Update source sheet order
    // Update PurchaseList boq_sheet_id
    // Move entry to target sheet
    DB::commit();
} catch (\Exception $e) {
    DB::rollBack();
}
```

**Good Practice:** This method correctly uses `DB::transaction()` and handles order management.

## PurchaseList Integration

The `BoqSheetEntryService` has deep integration with the `PurchaseList` domain:

### When Adding Entries

1. **From Quotation**: Calls `PurchaseListService::addToPurchaseListFromQuotation()`
   - Creates purchase list item linked to quotation
   - Syncs pricing and quantity

2. **Direct Entry**: Calls `PurchaseListService::addToPurchaseListDirect()`
   - Creates purchase list item without quotation
   - Uses product pricing

### When Deleting Entries

1. **PurchaseList Cleanup**:
   - Cancels and deletes purchase list item
   - Rejects associated quotation
   - Recalculates purchase order totals
   - Deletes purchase order if empty

2. **Purchase Order Management**:
   - Prevents deletion if order is not 'pending'
   - Recalculates costing after removal
   - Cancels empty purchase orders

### When Moving Entries

1. **PurchaseList Sync**:
   - Updates purchase list's `boq_sheet_id`
   - Maintains link to purchase order

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No transaction in `addColors()` | MEDIUM | Partial updates on failure | Wrap in `DB::transaction()` |
| No transaction in `storeOrUpdate()` | MEDIUM | Partial updates on failure | Wrap in `DB::transaction()` |
| Duplicate catch block in `deleteEntryFromBoqSheet()` | LOW | Code duplication | Remove duplicate |
| Uses `request()` in `exchangeEntrySheet()` | LOW | Tight coupling to HTTP | Pass target_sheet_id as parameter |
| Clears dynamic values on sheet move | MEDIUM | Data loss | Validate and preserve matching columns |

## Cross-References

- [BoqEntry-Model](/entities/boqentrymodel) - Data model for entries
- [BoqSheet-Model](/entities/boqsheet-model) - Data model for sheets
- [PurchaseListService](/entities/purchaselist-domain) - Procurement workflow integration
- [BoqSheetMergeService](/entities/boqsheetmergeservice) - Merge operations
- [Quotation](/entities/quotation-model) - Source data for entries
- Rfq - Request for quotation management

## Usage Examples

### Adding entry from quotation

```php
$result = $boqSheetEntryService->addEntryToBoqSheet($boqSheet, $quotation);

if ($result['status'] === 'success') {
    $entry = $result['data']['boq_entry'];
}
```

### Adding direct entry from product

```php
$result = $boqSheetEntryService->addDirectEntryToBoqSheet(
    $buyer,
    $boqSheet,
    $productId,
    $quantity
);

if ($result['status'] === 'success') {
    $entry = $result['data']['boq_entry'];
}
```

### Deleting entry

```php
$result = $boqSheetEntryService->deleteEntryFromBoqSheet($boqEntry);

if ($result['status'] === 'success') {
    // Entry deleted, purchase list cleaned up
}
```

### Moving entry to different sheet

```php
$result = $boqSheetEntryService->exchangeEntrySheet(
    $project,
    $sourceSheet,
    $boqEntry
);

if ($result['status'] === 'success') {
    // Entry moved to target sheet
}
```

### Adding colors to columns

```php
$result = $boqSheetEntryService->addColors($boqEntry, [
    'item_code' => '#FF0000',
    'specification' => '#00FF00'
]);

if ($result['status'] === 'success') {
    $updatedEntry = $result['data'];
}
```

## Architecture Notes

...