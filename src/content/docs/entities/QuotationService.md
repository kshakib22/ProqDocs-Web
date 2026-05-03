---
aliases: []
tags: [laravel, backend, auto-generated]
title: "QuotationService"
---
# QuotationService

The QuotationService handles all quotation business logic including creation, updates, deletion, and status management. This is the **largest service class in the codebase** at 800 lines.

## Current Architecture & Flow

### Service Methods

#### Quotation Retrieval
- `getQuotationsForVendor()`: Paginated quotations with search, status, RFQ filters
- `getQuotationsForBuyer()`: Quotations received by buyer
- `getQuotationsForRfq()`: All quotations for a specific RFQ
- `getQuotation()`: Single quotation with full details

#### Quotation Creation
- `createQuotation()`: Create quotation with services and documents
  - Validates RFQ accessibility (private RFQs restricted)
  - Checks deadline hasn't passed
  - Prevents duplicate quotations
  - Calculates total from components
  - Sends [QuotationSubmittedNotification](QuotationSubmittedNotification.md)

- `createPrivateQuotation()`: Create quotation for private RFQ

#### Quotation Management
- `updateQuotation()`: Update quotation (only if status is `in_review`)
  - Recalculates totals
  - Updates services
  - Handles document uploads
  - Sends [QuotationUpdatedNotification](QuotationUpdatedNotification.md)

- `updateQuotationStatus()`: Buyer accepts/rejects quotation
  - Optionally rejects other quotations for same RFQ

- `deleteQuotation()`: Soft delete (only if status is `in_review`)
- `removeDocument()`: Remove specific document

### Total Calculation
```
services_total = Σ(service.unit_price × service.quantity)
subtotal = unit_count × unit_price
tax_amount = subtotal × (vat_rate / 100)
total_amount = services_total + subtotal + tax_amount + shipping_amount + loading_charge
```

### Document Handling
Supports multiple upload formats:
- Uploaded files via `Illuminate\Http\UploadedFile`
- Base64 encoded strings (data URLs or plain)
- Automatic MIME type detection and file extension mapping

## Dependencies & Graph Links

- Used by [QuotationController](QuotationController.md) for all quotation endpoints
- Creates [Quotation Model](Quotation Model.md) and [QutationService Model](QutationService Model.md) instances
- Sends [QuotationSubmittedNotification](QuotationSubmittedNotification.md) and [QuotationUpdatedNotification](QuotationUpdatedNotification.md)
- Uses [QuotationResource](QuotationResource.md)

## Red Flags & Tech Debt

### Critical Issues
- **800 lines** - largest service class, needs splitting
- **Complex document handling** with multiple code paths
- **Manual total calculation** scattered throughout
- **Extensive logging** in production code

### Code Quality Issues
- **Nested conditional logic** in `createQuotation()`:
  ```php
  if ($rfq->type == 'private' && $quotationImage == null) {
      logger('quotationImage is null');
      $product = Product::findOrFail($rfq->product_id);
      logger('product: '.json_encode($product));
      $quotationImage = $product->main_image;
      logger('quotationImage after if: '.$quotationImage);
  }
  ```

- **Inconsistent error handling** - some methods return arrays, others throw
- **Commented-out code** for document handling
- **Magic array access** for service data

### Business Logic Issues
- No validation that accepted quotations cannot be modified
- No enforcement of quotation validity period
- No rate limiting on quotation submissions
- No bulk operations for common scenarios

### Performance
- Multiple database queries in loops
- No caching for quotation calculations
- Document existence checks in resource layer

## Future Upgrades (Postgres & Scalability)

### Service Refactoring
1. **Extract document handling**:
   ```php
   class QuotationDocumentService
   {
       public function handleUploads(Quotation $quotation, Request $request): void
       public function removeDocument(Quotation $quotation, Document $document): void
       public function decodeBase64File(string $value): array
   }
   ```

2. **Extract calculation logic**:
   ```php
   class QuotationCalculator
   {
       public function calculateTotal(array $data): array
       public function calculateServicesTotal(array $services): float
       public function calculateTax(float $subtotal, float $vatRate): float
   }
   ```

3. **Extract validation logic**:
   ```php
   class QuotationValidator
   {
       public function canCreate(Vendor $vendor, Rfq $rfq): bool
       public function canUpdate(Quotation $quotation): bool
       public function canDelete(Quotation $quotation): bool
   }
   ```

### Event-Driven Architecture
1. Add events:
   - `QuotationCreated` → triggers notifications
   - `QuotationUpdated` → updates search index
   - `QuotationAccepted` → triggers purchase order creation
   - `QuotationRejected` → notifies vendor

2. Move notification logic to event listeners

### Caching Strategy
1. Cache quotation calculations
2. Cache vendor quotation counts
3. Use Redis for rate limiting

### Monitoring
Add metrics for:
- Quotation submission rate by vendor
- Quotation acceptance rate
- Average quotation response time
- Services charge distribution
