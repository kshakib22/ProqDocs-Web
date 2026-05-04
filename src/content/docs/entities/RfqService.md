---
name: RfqService
description: Laravel service class for RFQ (Request for Quotation) business logic - handles RFQ creation, management, and vendor engagement
type: entity
---

# RfqService

## Architectural Purpose

`RfqService` is the business logic layer for RFQ (Request for Quotation) operations. This service encapsulates all complex operations related to:

- **RFQ Creation**: Creating public and private RFQs with validation
- **RFQ Management**: Updating, deleting, and querying RFQs
- **Vendor Engagement**: Managing public and private RFQ visibility
- **Document Handling**: Storing and managing RFQ documents
- **Image Management**: Handling product images for RFQs
- **Status Tracking**: Monitoring RFQ lifecycle and status counts

This service serves as the central hub for RFQ operations, ensuring data consistency and business rule enforcement across the procurement workflow.

## Service Dependencies

```php
use App\Http\Requests\PrivateRfqRequest;
use App\Http\Requests\StoreRfqRequest;
use App\Http\Resources\PrivateRfqResource;
use App\Http\Resources\PublicRfqResource;
use App\Http\Resources\RfqResource;
use App\Models\Buyer;
use App\Models\Product;
use App\Models\Rfq;
use App\Notifications\PrivateRfqCreatedNotification;
use App\Traits\ServiceResponder;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
```

- **ServiceResponder**: Trait for standardized API responses
- **RfqResource**: API resource for serialization
- **DB**: Database facade for transactions
- **Storage**: File storage for documents and images
- **Log**: Laravel logging facade

## Service Methods

### `getRfqsForBuyer(Buyer $buyer, Request $request): array`

**Purpose:** Get paginated RFQs for a buyer with filters and search.

**Parameters:**
- `$buyer`: Buyer instance
- `$request`: HTTP request with filters

**Behavior:**
1. Builds query with eager loading
2. Filters to public and active RFQs
3. Applies search, status, and type filters
4. Applies sorting
5. Returns paginated results with status counts

**Tech Debt:**
- **N+1 Query Risk**: `getStatusCounts()` runs multiple count queries
- **Inconsistent Status Values**: Uses 'pending', 'active', 'closed', 'cancelled' but model uses different values

### `createRfq(Buyer $buyer, StoreRfqRequest $request): array`

**Purpose:** Create a new RFQ.

**Parameters:**
- `$buyer`: Buyer instance
- `$request`: Validated request data

**Behavior:**
1. **Uses transaction** for data consistency
2. Extracts documents payload
3. Stores product image if provided
4. Generates unique RFQ code
5. Creates RFQ with buyer and user IDs
6. Stores documents
7. Returns created RFQ

**Transaction Scope:**
```php
DB::beginTransaction();
// Create RFQ
// Store documents
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()`.

### `createPrivateRfq(Buyer $buyer, PrivateRfqRequest $request): array`

**Purpose:** Create a private RFQ for a specific vendor.

**Parameters:**
- `$buyer`: Buyer instance
- `$request`: Validated request data

**Behavior:**
1. **Uses transaction** for data consistency
2. Loads product data
3. Generates RFQ title and code
4. Calculates budget based on product price
5. Sets type to 'private'
6. Creates RFQ
7. Sends notification to vendor
8. Returns created RFQ

**Transaction Scope:**
```php
DB::beginTransaction();
// Create RFQ
// Send notification
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()`.

**Tech Debt:**
- **Commented Code**: Lines 154-162 contain commented purchase list logic
- **No Validation**: No validation on vendor_id existence

### `getRfq(Rfq $rfq): array`

**Purpose:** Get a single RFQ with full details.

**Parameters:**
- `$rfq`: Rfq instance

**Behavior:**
1. Loads relationships
2. Returns RFQ resource

**Tech Debt:**
- **No Transaction**: Single read operation doesn't need transaction

### `updateRfq(Buyer $buyer, Rfq $rfq, Request $request): array`

**Purpose:** Update an existing RFQ.

**Parameters:**
- `$buyer`: Buyer instance
- `$rfq`: Rfq instance
- `$request`: Request with update data

**Behavior:**
1. **Uses transaction** for data consistency
2. Extracts documents payload
3. Handles product image update
4. Filters update data
5. Updates RFQ
6. Deletes old image if needed
7. Stores new documents
8. Returns updated RFQ

**Transaction Scope:**
```php
DB::beginTransaction();
// Update RFQ
// Delete old image
// Store new documents
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()`.

**Tech Debt:**
- **Commented Code**: Lines 210-213, 278 contain commented code
- **Manual Field Filtering**: Lines 228-270 manually filter fields (inefficient)
- **Typo in Method Name**: `categoies()` instead of `categories()` (line 324)

### `deleteRfq(Buyer $buyer, Rfq $rfq): array`

**Purpose:** Delete an RFQ (soft delete).

**Parameters:**
- `$buyer`: Buyer instance
- `$rfq`: Rfq instance

**Behavior:**
1. **Uses transaction** for data consistency
2. Gets all associated documents
3. Deletes physical files from storage
4. Deletes sample image
5. Deletes document records
6. Detaches categories
7. Soft deletes RFQ
8. Returns success

**Transaction Scope:**
```php
DB::beginTransaction();
// Delete document files
// Delete sample image
// Delete document records
// Detach categories
// Soft delete RFQ
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()` and properly cleans up files.

### `getStatusCounts(Buyer $buyer): array`

**Purpose:** Get status counts for a buyer's RFQs.

**Parameters:**
- `$buyer`: Buyer instance

**Behavior:**
1. Runs multiple count queries
2. Returns status breakdown

**Tech Debt:**
- **N+1 Query Risk**: Runs 5 separate count queries
- **Inconsistent Status Values**: Uses status values that may not match model

**Recommended Fix:**
```php
private function getStatusCounts(Buyer $buyer): array
{
    return $buyer->rfqs()
        ->selectRaw('status, COUNT(*) as count')
        ->groupBy('status')
        ->pluck('count', 'status')
        ->toArray();
}
```

### `generateRfqCode($type="live"): string`

**Purpose:** Generate a unique RFQ code.

**Parameters:**
- `$type`: RFQ type (default: 'live')

**Behavior:**
1. Generates code with UUID
2. Checks for uniqueness
3. Returns unique code

**Format:** `RFQ-{type}-{uuid}`

### `generateRfqTitle(Product $product, Buyer $buyer): string`

**Purpose:** Generate RFQ title for private RFQs.

**Parameters:**
- `$product`: Product instance
- `$buyer`: Buyer instance

**Behavior:**
1. Returns title in format: `RFQ-{product_name}-{buyer_id}`

**Tech Debt:**
- **Poor Title Format**: Uses buyer ID instead of buyer name
- **No Validation**: No validation on product or buyer

### `storeDocuments(Rfq $rfq, array $documents): void`

**Purpose:** Persist uploaded documents for the RFQ.

**Parameters:**
- `$rfq`: Rfq instance
- `$documents`: Array of document data

**Behavior:**
1. Iterates through documents
2. Stores file to storage
3. Creates document record
4. Links to RFQ

### `storeProductImageFile(UploadedFile $file): string`

**Purpose:** Store product image file.

**Parameters:**
- `$file`: Uploaded file instance

**Behavior:**
1. Stores file to `rfqs/product-images`
2. Returns stored path

### `deleteStoredFile(?string $path): void`

**Purpose:** Delete stored file.

**Parameters:**
- `$path`: File path

**Behavior:**
1. Checks if path exists
2. Deletes file from storage

### `syncCategories(Rfq $rfq, mixed $categoryIds, bool $detachIfEmpty = false): void`

**Purpose:** Sync category IDs with RFQ.

**Parameters:**
- `$rfq`: Rfq instance
- `$categoryIds`: Category IDs (array or string)
- `$detachIfEmpty`: Whether to detach if empty

**Behavior:**
1. Checks if categories relationship exists
2. Converts string to array if needed
3. Syncs categories
4. Detaches if empty and requested

**Tech Debt:**
- **Typo in Method Name**: `categoies()` instead of `categories()` (line 431)

### `resolveDocumentLevel(?string $level): string`

**Purpose:** Resolve document level to allowed value.

**Parameters:**
- `$level`: Document level

**Behavior:**
1. Checks if level is allowed
2. Returns level or 'low' default

### `extractCategoryIds(Request $request): array|string|null`

**Purpose:** Extract category IDs from request.

**Parameters:**
- `$request`: HTTP request

**Behavior:**
1. Gets category_ids from request
2. Filters array values
3. Returns array, string, or null

### `extractDocumentsPayload(Request $request, array &$data): array`

**Purpose:** Extract document payload from validated data or request input.

**Parameters:**
- `$request`: HTTP request
- `$data`: Reference to data array

**Behavior:**
1. Gets documents from data
2. Unsets documents from data
3. Falls back to request input
4. Returns documents array

### `storageDisk(): string`

**Purpose:** Get storage disk configuration.

**Behavior:**
1. Returns configured storage disk
2. Defaults to 'public'

### `getPublicRfqsForBuyer(Request $request, Buyer $buyer): array`

**Purpose:** Get public RFQs for a buyer.

**Parameters:**
- `$request`: HTTP request with filters
- `$buyer`: Buyer instance

**Behavior:**
1. Builds query with eager loading
2. Filters to public and active RFQs
3. Applies search, category, status, and project filters
4. Applies sorting
5. Returns paginated results

**Tech Debt:**
- **No Transaction**: Read-only operation
- **N+1 Query Risk**: Eager loads quotations and their relationships

### `getPublicRfqsForVendor(Request $request): array`

**Purpose:** Get public RFQs for vendors to view.

**Parameters:**
- `$request`: HTTP request with filters

**Behavior:**
1. Builds query with eager loading
2. Filters to public and active RFQs
3. Applies search and category filters
4. Returns paginated results

**Tech Debt:**
- **No Transaction**: Read-only operation
- **Limited Eager Loading**: Only loads project and product

### `getPrivateRfqsForBuyer(Request $request, Buyer $buyer): array`

**Purpose:** Get private RFQs for a buyer.

**Parameters:**
- `$request`: HTTP request with filters
- `$buyer`: Buyer instance

**Behavior:**
1. Builds query with eager loading
2. Filters to private RFQs
3. Applies search and project filters
4. Applies sorting
5. Returns paginated results

**Tech Debt:**
- **No Transaction**: Read-only operation
- **Commented Status Filter**: Line 615 has commented status filter

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| N+1 query in `getStatusCounts()` | HIGH | Performance issue | Use single query with GROUP BY |
| Commented code throughout | MEDIUM | Code confusion | Remove or document |
| Typo in `categoies()` method | MEDIUM | Potential errors | Fix to `categories()` |
| Inconsistent status values | MEDIUM | Data inconsistency | Standardize status values |
| Manual field filtering in `updateRfq()` | MEDIUM | Code inefficiency | Use `only()` or `except()` |
| No validation in `createPrivateRfq()` | LOW | Data integrity risk | Add validation rules |
| Poor title format in `generateRfqTitle()` | LOW | UX issue | Use buyer name instead of ID |

## Cross-References

- [[Rfq-Model]] - Data model for RFQs
- [[RfqController]] - Controller that uses this service
- [[Quotation-Model]] - Vendor responses to RFQs
- [[QuotationService]] - Service for quotation operations

## Usage Examples

### Creating a public RFQ

```php
$result = $rfqService->createRfq($buyer, $request);

if ($result['status'] === 'success') {
    $rfq = $result['data'];
}
```

### Creating a private RFQ

```php
$result = $rfqService->createPrivateRfq($buyer, $request);

if ($result['status'] === 'success') {
    $rfq = $result['data'];
}
```

### Getting RFQs for buyer

```php
$result = $rfqService->getRfqsForBuyer($buyer, $request);

if ($result['status'] === 'success') {
    $rfqs = $result['data']['rfqs'];
}
```

### Updating an RFQ

```php
$result = $rfqService->updateRfq($buyer, $rfq, $request);

if ($result['status'] === 'success') {
    $updatedRfq = $result['data'];
}
```

### Deleting an RFQ

```php
$result = $rfqService->deleteRfq($buyer, $rfq);

if ($result['status'] === 'success') {
    // RFQ deleted with all documents
}
```

## Architecture Notes

### Why This Service Exists

The `RfqService` serves several critical purposes:

1. **Business Logic Encapsulation**: Keeps complex operations out of controllers
2. **Data Consistency**: Ensures RFQ data integrity through transactions
3. **File Management**: Handles document and image storage
4. **Validation**: Enforces business rules for RFQ operations
5. **Notification**: Sends notifications for private RFQs

### Relationship to Other Services

```
RfqController
    │
    └──> RfqService (this service)
            ├──> Rfq (model)
            ├──> Document (file management)
            ├──> Product (data source)
            └──> Notification (vendor engagement)
```

### Future Enhancements

Potential improvements to this service:

1. **Fix N+1 queries**: Optimize `getStatusCounts()` method
2. **Remove commented code**: Clean up unused code sections
3. **Fix typos**: Correct `categoies()` to `categories()`
4. **Add validation**: Add validation rules for all operations
5. **Improve title generation**: Use buyer name instead of ID
6. **Standardize status values**: Ensure consistency across codebase
7. **Add event dispatching**: Emit events for RFQ lifecycle changes
8. **Add caching**: Cache frequently accessed RFQ data
