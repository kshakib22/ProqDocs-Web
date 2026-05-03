---
aliases: []
tags: [laravel, backend, auto-generated]
title: "RfqService"
---
# RfqService

The RfqService handles all RFQ business logic including creation, updates, deletion, and retrieval for both public and private RFQs.

## Current Architecture & Flow

### Service Methods

#### RFQ Retrieval
- `getRfqsForBuyer()`: Paginated RFQs with search, status, type filters
- `getPublicRfqsForBuyer()`: Public RFQs for buyer's projects
- `getPublicRfqsForVendor()`: Public RFQs available for vendors to quote
- `getPrivateRfqsForBuyer()`: Private RFQs sent by buyer
- `getRfq()`: Single RFQ with full details

#### RFQ Creation
- `createRfq()`: Create public RFQ with document uploads
- `createPrivateRfq()`: Create private RFQ for specific vendor
  - Auto-generates title from product and buyer
  - Calculates budget from product unit price
  - Sends [PrivateRfqCreatedNotification](PrivateRfqCreatedNotification.md) to vendor

#### RFQ Management
- `updateRfq()`: Update RFQ (only public RFQs, not private)
- `deleteRfq()`: Soft delete with document cleanup
- `rejectRfq()`: Reject RFQ and all associated quotations

### RFQ Code Generation
- Public: `RFQ-live-{uuid}`
- Private: `RFQ-private-{uuid}`

### Document Handling
- Stores documents in `rfqs/documents/` directory
- Stores product images in `rfqs/product-images/` directory
- Cleans up physical files on deletion

## Dependencies & Graph Links

- Used by [RfqController](RfqController.md) for all RFQ endpoints
- Creates [Rfq Model](Rfq Model.md) instances
- Sends [PrivateRfqCreatedNotification](PrivateRfqCreatedNotification.md)
- Uses [RfqResource](RfqResource.md), [PublicRfqResource](PublicRfqResource.md), [PrivateRfqResource](PrivateRfqResource.md)

## Red Flags & Tech Debt

### Large Service Class
- **654 lines** - too many responsibilities
- Handles both public and private RFQ logic
- Document handling mixed with core business logic
- Should be split into `RfqDocumentService`

### Code Quality Issues
- **Manual field filtering** in `updateRfq()` (lines 228-271):
  ```php
  if(array_key_exists('product_image', $updateData) && $updateData['product_image']){
      $data['product_image'] = $updateData['product_image'];
  }
  // ... repeated for 10+ fields
  ```
  This should be handled by request validation

- **Commented-out code** for category sync and purchase list integration
- Inconsistent error handling patterns

### Business Logic Issues
- No validation that private RFQs cannot be updated after creation
- No deadline enforcement at service level (only checked in queries)
- No rate limiting on RFQ creation

### Performance
- Multiple eager loading patterns but some N+1 queries likely
- No caching for public RFQ listings
- Document storage checks in resource layer

## Future Upgrades (Postgres & Scalability)

### Service Refactoring
1. **Extract document handling**:
   ```php
   class RfqDocumentService
   {
       public function storeDocuments(Rfq $rfq, array $documents): void
       public function deleteDocuments(Rfq $rfq): void
       public function storeProductImage(UploadedFile $file): string
   }
   ```

2. **Extract public/private RFQ logic**:
   ```php
   class PublicRfqService extends RfqService
   class PrivateRfqService extends RfqService
   ```

3. **Add command pattern for status transitions**:
   ```php
   class RejectRfqCommand
   class AcceptRfqCommand
   ```

### Caching Strategy
1. Cache public RFQ listings with TTL based on deadline proximity
2. Cache RFQ status counts for buyer dashboards
3. Use Redis for rate limiting on RFQ creation

### Event-Driven Architecture
1. Add events:
   - `RfqCreated` → triggers notifications
   - `RfqUpdated` → updates search index
   - `RfqExpired` → closes expired RFQs
   - `RfqRejected` → notifies vendors

2. Move notification logic to event listeners

### Monitoring
Add metrics for:
- RFQ creation rate by buyer
- RFQ-to-quotation conversion rate
- Average time to first quotation
- Private vs public RFQ ratio
