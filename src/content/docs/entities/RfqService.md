---
name: RfqService
description: Laravel service class for RFQ (Request for Quotation) business logic - handles RFQ creation, management, and vendor engagement
type: entity
title: "RfqService"
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

...

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

...

### `createRfq(Buyer $buyer, StoreRfqRequest $request): array`

**Purpose:** Create a new RFQ.

...

### `createPrivateRfq(Buyer $buyer, PrivateRfqRequest $request): array`

**Purpose:** Create a private RFQ for a specific vendor.

...

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

...

### `deleteRfq(Buyer $buyer, Rfq $rfq): array`

**Purpose:** Delete an RFQ (soft delete).

...

### `getStatusCounts(Buyer $buyer): array`

**Purpose:** Get status counts for a buyer's RFQs.

...

### `generateRfqCode($type="live"): string`

**Purpose:** Generate a unique RFQ code.

...

### `generateRfqTitle(Product $product, Buyer $buyer): string`

**Purpose:** Generate RFQ title for private RFQs.

...

### `storeDocuments(Rfq $rfq, array $documents): void`

**Purpose:** Persist uploaded documents for the RFQ.

...

### `storeProductImageFile(UploadedFile $file): string`

**Purpose:** Store product image file.

...

### `deleteStoredFile(?string $path): void`

**Purpose:** Delete stored file.

...

### `syncCategories(Rfq $rfq, mixed $categoryIds, bool $detachIfEmpty = false): void`

**Purpose:** Sync category IDs with RFQ.

...

### `resolveDocumentLevel(?string $level): string`

**Purpose:** Resolve document level to allowed value.

...

### `extractCategoryIds(Request $request): array|string|null`

**Purpose:** Extract category IDs from request.

...

### `extractDocumentsPayload(Request $request, array &$data): array`

**Purpose:** Extract document payload from validated data or request input.

...

### `storageDisk(): string`

**Purpose:** Get storage disk configuration.

...

### `getPublicRfqsForBuyer(Request $request, Buyer $buyer): array`

**Purpose:** Get public RFQs for a buyer.

...

### `getPublicRfqsForVendor(Request $request): array`

**Purpose:** Get public RFQs for vendors to view.

...

### `getPrivateRfqsForBuyer(Request $request, Buyer $buyer): array`

**Purpose:** Get private RFQs for a buyer.

...

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

- [Rfq-Model](/entities/rfq-model) - Data model for RFQs
- [RfqController](/entities/rfqcontroller) - Controller that uses this service
- [Quotation-Model](/entities/quotation-model) - Vendor responses to RFQs
- [QuotationService](/entities/quotationservice) - Service for quotation operations

## Usage Examples

...
