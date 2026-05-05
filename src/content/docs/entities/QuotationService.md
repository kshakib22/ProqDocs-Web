---
name: QuotationService
description: Laravel service class for Quotation business logic - handles vendor quotation submission, management, and buyer acceptance
type: entity
title: "QuotationService"
---

# QuotationService

## Architectural Purpose

`QuotationService` is the business logic layer for Quotation operations. This service encapsulates all complex operations related to:

- **Quotation Creation**: Creating vendor quotations with pricing breakdown
- **Quotation Management**: Updating, deleting, and querying quotations
- **Pricing Calculations**: Aggregating unit prices, service charges, tax, and shipping
- **Status Management**: Handling acceptance/rejection flow and competitive bidding
- **Document Handling**: Storing and managing quotation documents
- **Vendor Engagement**: Managing vendor access and permissions

This service serves as the critical bridge between vendors submitting quotes and buyers accepting them, ensuring data consistency and business rule enforcement throughout the procurement workflow.

## Service Dependencies

```php
use App\Http\Requests\UpdateQuotationRequest;
use App\Http\Resources\QuotationResource;
use App\Models\Buyer;
use App\Models\Document;
use App\Models\Product;
use App\Models\Quotation;
use App\Models\QutationService;
use App\Models\Rfq;
use App\Models\Vendor;
use App\Notifications\QuotationSubmittedNotification;
use App\Notifications\QuotationUpdatedNotification;
use App\Traits\ServiceResponder;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
```

- **ServiceResponder**: Trait for standardized API responses
- **QuotationResource**: API resource for serialization
- **QutationService**: Line items for quotation breakdown
- **DB**: Database facade for transactions
- **Storage**: File storage for documents and images
- **Log**: Laravel logging facade

## Service Methods

### `getQuotationsForVendor(Vendor $vendor, Request $request): array`

**Purpose:** Get paginated quotations for a vendor with filters and search.

**Parameters:**
- `$vendor`: Vendor instance
- `$request`: HTTP request with filters

**Behavior:**
1. Builds query with eager loading
2. Filters to vendor's quotations
3. Applies search, status, and RFQ filters
4. Applies sorting
5. Returns paginated results with status counts

**Tech Debt:**
- **N+1 Query Risk**: `getStatusCounts()` runs multiple count queries

### `getQuotationsForBuyer(Buyer $buyer, Request $request): array`

**Purpose:** Get paginated quotations for a buyer's RFQs with filters and search.

**Parameters:**
- `$buyer`: Buyer instance
- `$request`: HTTP request with filters

**Behavior:**
1. Builds query with eager loading
2. Filters to buyer's quotations
3. Applies search, status, and RFQ filters
4. Applies sorting
5. Returns paginated results with status counts

**Tech Debt:**
- **N+1 Query Risk**: `getBuyerStatusCounts()` runs multiple count queries
- **Commented Code**: Line 134 has commented boost_score sorting

### `getQuotationsForRfq(Rfq $rfq, Request $request): array`

**Purpose:** Get quotations for a specific RFQ.

**Parameters:**
- `$rfq`: Rfq instance
- `$request`: Request with filters

**Behavior:**
1. Builds query with eager loading
2. Filters to RFQ's quotations
3. Applies status and sorting filters
4. Returns paginated results

### `createQuotation(Vendor $vendor, Request $request): array`

**Purpose:** Create a new quotation.

**Parameters:**
- `$vendor`: Vendor instance
- `$request`: Request with quotation data

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates RFQ access and deadline
3. Checks for existing quotation
4. Extracts services data
5. Stores quotation image
6. Calculates pricing totals
7. Creates quotation
8. Creates service line items
9. Handles document uploads
10. Sends notification to buyer
11. Returns created quotation

**Transaction Scope:**
```php
DB::transaction(function () use ($vendor, $request, $rfq) {
    // Create quotation
    // Create services
    // Handle documents
    // Send notification
});
```

**Good Practice:** This method correctly uses `DB::transaction()`.

**Pricing Calculation:**
```php
$servicesTotal = 0;
foreach ($services as $service) {
    $servicesTotal += ($service['unit_price'] * $service['quantity']);
}
$subtotal = $quotationData['unit_count'] * $quotationData['unit_price'];
$vatRate = array_key_exists('vat_rate', $quotationData) ? round((float) $quotationData['vat_rate'], 2) : 0;
$taxAmount = round($subtotal * $vatRate / 100, 2);
$calculatedTotal = $servicesTotal + $subtotal + $taxAmount + $shippingAmount + $loadingCharge;
```

**Tech Debt:**
- **Excessive Logging**: Multiple `logger()` calls (lines 237, 246, 248, 251, 253, 286, 317)
- **Commented Code**: Lines 243-245 contain commented code
- **No Validation**: No validation on service data
- **Hardcoded Defaults**: Default values set inline

### `createPrivateQuotation(Vendor $vendor, Request $request)`

**Purpose:** Create a private quotation.

**Parameters:**
- `$vendor`: Vendor instance
- `$request`: Request with quotation data

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates RFQ access
3. Checks for existing quotation
4. Returns error if validation fails

**Tech Debt:**
- **Incomplete Implementation**: Method only validates, doesn't create quotation
- **Early Return**: Returns error without completing transaction

### `handleDocumentUploads(Quotation $quotation, Request $request): void`

**Purpose:** Handle document uploads for quotations.

**Parameters:**
- `$quotation`: Quotation instance
- `$request`: Request with documents

**Behavior:**
1. Iterates through documents
2. Handles multiple file formats (uploaded file, base64 string)
3. Stores file to storage
4. Creates document record
5. Links to quotation

**Tech Debt:**
- **Complex Logic**: Handles multiple file formats in one method
- **No Validation**: No validation on file types or sizes
- **No Error Handling**: Continues on errors without reporting

### `decodeBase64File(string $value): array`

**Purpose:** Decode base64 file data.

**Parameters:**
- `$value`: Base64 encoded string

**Behavior:**
1. Parses data URL format
2. Decodes base64
3. Returns mime type and binary data

### `extensionFromMime(?string $mime, string $default): string`

**Purpose:** Map mime types to file extensions.

**Parameters:**
- `$mime`: Mime type
- `$default`: Default extension

**Behavior:**
1. Maps common mime types to extensions
2. Returns extension or default

**Supported Types:**
- Images: png, jpg, gif, webp, svg
- Documents: pdf, doc, docx, xls, xlsx
- 3D/CAD: dwg, dxf, skp, rvt, ifc, obj, fbx

### `getQuotation(Quotation $quotation): array`

**Purpose:** Get a single quotation with full details.

**Parameters:**
- `$quotation`: Quotation instance

**Behavior:**
1. Loads relationships
2. Returns quotation resource

### `updateQuotation(Vendor $vendor, Quotation $quotation, UpdateQuotationRequest $request): array`

**Purpose:** Update an existing quotation.

**Parameters:**
- `$vendor`: Vendor instance
- `$quotation`: Quotation instance
- `$request`: Request with update data

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates vendor ownership
3. Validates status is 'in_review'
4. Loads existing services
5. Calculates new totals
6. Updates quotation
7. Deletes and recreates services
8. Handles document uploads
9. Deletes old image if needed
10. Sends notification to buyer
11. Returns updated quotation

**Transaction Scope:**
```php
DB::beginTransaction();
// Update quotation
// Delete and recreate services
// Handle documents
// Delete old image
// Send notification
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()`.

**Tech Debt:**
- **Excessive Logging**: Multiple `logger()` calls (line 539)
- **Commented Code**: Lines 628-643 contain commented code
- **Service Deletion**: Deletes all services and recreates (inefficient)

### `updateQuotationStatus(Buyer $buyer, Quotation $quotation, Request $request): array`

**Purpose:** Update quotation status (for buyers).

**Parameters:**
- `$buyer`: Buyer instance
- `$quotation`: Quotation instance
- `$request`: Request with status

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates buyer ownership
3. Validates status is 'accepted' or 'rejected'
4. Updates quotation status
5. Optionally rejects competing quotations
6. Returns updated quotation

**Transaction Scope:**
```php
DB::beginTransaction();
// Update quotation status
// Reject competing quotations
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()`.

### `deleteQuotation(Vendor $vendor, Quotation $quotation): array`

**Purpose:** Delete a quotation (soft delete).

**Parameters:**
- `$vendor`: Vendor instance
- `$quotation`: Quotation instance

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates vendor ownership
3. Validates status is 'in_review'
4. Deletes quotation image
5. Soft deletes quotation
6. Returns success

**Transaction Scope:**
```php
DB::beginTransaction();
// Delete quotation image
// Soft delete quotation
DB::commit();
```

**Good Practice:** This method correctly uses `DB::transaction()`.

### `getStatusCounts(Vendor $vendor): array`

**Purpose:** Get status counts for a vendor's quotations.

**Parameters:**
- `$vendor`: Vendor instance

**Behavior:**
1. Runs multiple count queries
2. Returns status breakdown

**Tech Debt:**
- **N+1 Query Risk**: Runs 4 separate count queries

**Recommended Fix:**
```php
private function getStatusCounts(Vendor $vendor): array
{
    return $vendor->quotations()
        ->selectRaw('status, COUNT(*) as count')
        ->groupBy('status')
        ->pluck('count', 'status')
        ->toArray();
}
```

### `getBuyerStatusCounts(Buyer $buyer): array`

**Purpose:** Get status counts for a buyer's quotations.

**Parameters:**
- `$buyer`: Buyer instance

**Behavior:**
1. Runs multiple count queries
2. Returns status breakdown

**Tech Debt:**
- **N+1 Query Risk**: Runs 4 separate count queries

**Recommended Fix:**
```php
private function getBuyerStatusCounts(Buyer $buyer): array
{
    return Quotation::where('buyer_id', $buyer->id)
        ->selectRaw('status, COUNT(*) as count')
        ->groupBy('status')
        ->pluck('count', 'status')
        ->toArray();
}
```

### `generateQuotationNumber(int $rfqId): string`

**Purpose:** Generate a unique quotation number.

**Parameters:**
- `$rfqId`: RFQ ID

**Behavior:**
1. Generates number with random string
2. Checks for uniqueness
3. Returns unique number

**Format:** `QT-{rfq_id}-{random}`

### `removeDocument(Vendor $vendor, Quotation $quotation, Document $document)`

**Purpose:** Remove a document from a quotation.

**Parameters:**
- `$vendor`: Vendor instance
- `$quotation`: Quotation instance
- `$document`: Document instance

**Behavior:**
1. Validates vendor ownership
2. Deletes file from storage
3. Deletes document record
4. Returns success

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| N+1 query in `getStatusCounts()` | HIGH | Performance issue | Use single query with GROUP BY |
| N+1 query in `getBuyerStatusCounts()` | HIGH | Performance issue | Use single query with GROUP BY |
| Excessive logging in `createQuotation()` | MEDIUM | Performance impact | Remove or reduce logging |
| Commented code throughout | MEDIUM | Code confusion | Remove or document |
| Service deletion in `updateQuotation()` | MEDIUM | Performance issue | Use update instead of delete |
| Incomplete `createPrivateQuotation()` | MEDIUM | Functionality incomplete | Complete implementation |
| No validation on service data | LOW | Data integrity risk | Add validation rules |
| No file size validation | LOW | Security risk | Add file size limits |
| No error handling in `handleDocumentUploads()` | LOW | Silent failures | Add error handling |

## Cross-References

- [Quotation-Model](./Quotation-Model.md) - Data model for quotations
- [QutationService-Model](./QutationService-Model.md) - Line items for quotations
- [Rfq-Model](./Rfq-Model.md) - Parent RFQ for quotations
- [QuotationController](./QuotationController.md) - Controller that uses this service
- [QuotationResource](./QuotationResource.md) - API resource for serialization

## Usage Examples

### Creating a quotation

```php
$result = $quotationService->createQuotation($vendor, $request);

if ($result['status'] === 'success') {
    $quotation = $result['data'];
}
```

### Getting quotations for vendor

```php
$result = $quotationService->getQuotationsForVendor($vendor, $request);

if ($result['status'] === 'success') {
    $quotations = $result['data']['quotations'];
}
```

### Getting quotations for buyer

```php
$result = $quotationService->getQuotationsForBuyer($buyer, $request);

if ($result['status'] === 'success') {
    $quotations = $result['data']['quotations'];
}
```

### Updating a quotation

```php
$result = $quotationService->updateQuotation($vendor, $quotation, $request);

if ($result['status'] === 'success') {
    $updatedQuotation = $result['data'];
}
```

### Accepting a quotation

```php
$result = $quotationService->updateQuotationStatus($buyer, $quotation, $request);

if ($result['status'] === 'success') {
    // Quotation accepted, competing quotes rejected
}
```

### Deleting a quotation

```php
$result = $quotationService->deleteQuotation($vendor, $quotation);

if ($result['status'] === 'success') {
    // Quotation deleted
}
```

## Architecture Notes

### Why This Service Exists

The `QuotationService` serves several critical purposes:

1. **Business Logic Encapsulation**: Keeps complex operations out of controllers
2. **Data Consistency**: Ensures quotation data integrity through transactions
3. **Pricing Calculations**: Aggregates complex pricing breakdowns
4. **File Management**: Handles document and image storage
5. **Validation**: Enforces business rules for quotation operations
6. **Notification**: Sends notifications for quotation updates

### Relationship to Other Services

```
QuotationController
    │
    └──> QuotationService (this service)
            ├──> Quotation (model)
            ├──> QutationService (line items)
            ├──> Document (file management)
            ├──> Rfq (parent RFQ)
            └──> Notification (buyer engagement)
```

### Future Enhancements

Potential improvements to this service:

1. **Fix N+1 queries**: Optimize status count methods
2. **Remove commented code**: Clean up unused code sections
3. **Improve service updates**: Use update instead of delete/recreate
4. **Add validation**: Add validation rules for all operations
5. **Add file size limits**: Prevent large file uploads
6. **Add error handling**: Handle document upload failures
7. **Reduce logging**: Remove excessive logging
8. **Complete private quotation**: Finish `createPrivateQuotation()` implementation
9. **Add event dispatching**: Emit events for quotation lifecycle changes
10. **Add caching**: Cache frequently accessed quotation data
