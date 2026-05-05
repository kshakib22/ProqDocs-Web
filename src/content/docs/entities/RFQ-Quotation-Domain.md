---
aliases: []
tags: [laravel, backend, auto-generated]
title: "RFQ-Quotation-Domain"
---
# RFQ-Quotation-Domain

The Request for Quotation (RFQ) and Quotation domain manages the procurement workflow where buyers request quotes and vendors submit quotations. This is a core business domain connecting Buyer-Domain, **[Vendor-Domain](./Vendor-Domain.md)**, and **[Product-Domain](./Product-Domain.md)**.

## Current Architecture & Flow

### RFQ (Request for Quotation) Flow

1. **Buyer creates RFQ** via **[RfqController](./RfqController.md)** → **[RfqService](./RfqService.md)**
   - Public RFQ: Visible to all vendors, multiple vendors can quote
   - Private RFQ: Sent to specific vendor, only that vendor can quote
   - RFQ includes: product details, quantity, budget range, deadline, urgency

2. **RFQ Status Lifecycle**:
   - `in_review` → Initial state
   - `active` → Open for quotations
   - `accepted` → Buyer accepted a quotation
   - `rejected` → Buyer rejected the RFQ
   - `cancelled` → Buyer cancelled the RFQ

3. **RFQ Types**:
   - `public`: Any vendor can view and quote
   - `private`: Only assigned vendor can view and quote

### Quotation Flow

1. **Vendor submits quotation** via **[QuotationController](./QuotationController.md)** → **[QuotationService](./QuotationService.md)**
   - Validates RFQ accessibility (private RFQs restricted to assigned vendor)
   - Checks deadline hasn't passed
   - Prevents duplicate quotations from same vendor
   - Calculates total: subtotal + services + tax + shipping + loading

2. **Quotation Status Lifecycle**:
   - `in_review` → Initial state, vendor can edit/delete
   - `accepted` → Buyer accepted this quotation
   - `rejected` → Buyer rejected this quotation

3. **Quotation Components**:
   - Unit price × quantity = subtotal
   - QutationService items (additional services)
   - VAT/tax amount
   - Shipping amount
   - Loading charge
   - Validity period (days)

### Key Relationships

```
Buyer → creates → RFQ → has many → Quotations
Vendor → submits → Quotation → belongs to → RFQ
RFQ → belongs to → Product, Project, Category
Quotation → has many → QutationService (line items)
```

## Dependencies & Graph Links

### Models
- **[Rfq Model](./Rfq Model.md)** - RFQ entity with soft deletes
- **[Quotation Model](./Quotation Model.md)** - Quotation entity with soft deletes
- **[QutationService Model](./QutationService Model.md)** - Quotation line items (note: typo in class name)

### Services
- **[RfqService](./RfqService.md)** - RFQ business logic (654 lines)
- **[QuotationService](./QuotationService.md)** - Quotation business logic (800 lines)
- QuotationBoostScoreService - Subscription-based quotation ranking

### Controllers
- **[RfqController](./RfqController.md)** - Buyer RFQ endpoints
- **[QuotationController](./QuotationController.md)** - Vendor quotation endpoints

### Resources
- **[RfqResource](./RfqResource.md)** - RFQ API transformation
- **[QuotationResource](./QuotationResource.md)** - Quotation API transformation
- PublicRfqResource - Public RFQ view for vendors
- PrivateRfqResource - Private RFQ view

### Notifications
- QuotationSubmittedNotification - Sent to buyer when vendor quotes
- QuotationUpdatedNotification - Sent to buyer when vendor updates quote
- PrivateRfqCreatedNotification - Sent to vendor for private RFQs


## Red Flags & Tech Debt

### Fat Controllers
- **[RfqController](./RfqController.md)**: 613 lines with extensive inline authorization checks
  - Authorization logic repeated across methods
  - Should extract to policies or middleware

- **[QuotationController](./QuotationController.md)**: 577 lines with similar issues
  - Mixed concerns: authorization, validation, business logic
  - JWTAuth mixed with Auth facade

### Service Layer Issues
- **[RfqService](./RfqService.md)**: 654 lines - large service class
  - Multiple responsibilities: RFQ CRUD, document handling, public/private RFQs
  - `updateRfq()` has manual field filtering (lines 228-271) - should use request validation
  - Commented-out code for category sync and purchase list integration

- **[QuotationService](./QuotationService.md)**: 800 lines - largest service in codebase
  - Complex document upload handling with multiple formats (uploaded file, base64)
  - Manual total calculation logic scattered throughout
  - `createQuotation()` has extensive logging and conditional logic

### Naming Issues
- **[QutationService Model](./QutationService Model.md)**: Typo in class name ("Qutation" instead of "Quotation")
  - This is a breaking change waiting to happen
  - Used throughout the codebase


### Data Integrity
- RFQ deadline validation only in service layer, not database constraints
- No database-level enforcement of one-quotation-per-vendor-per-RFQ rule
- Soft deletes used but no cleanup strategy for orphaned documents

### Performance
- Multiple eager loading patterns but some N+1 queries likely remain
- No caching for public RFQ listings (high read volume)
- Document storage checks in resource layer (`Storage::disk('public')->exists()`)

## Future Upgrades (Postgres & Scalability)

### Database Optimizations
1. **Add composite indexes**:
   ```sql
   CREATE INDEX idx_rfqs_buyer_status ON rfqs(buyer_id, status);
   CREATE INDEX idx_rfqs_public_active ON rfqs(type, status, dead_line_date);
   CREATE INDEX idx_quotations_rfq_vendor ON quotations(rfq_id, vendor_id);
   CREATE INDEX idx_quotations_status_created ON quotations(status, created_at DESC);
   ```

2. **Add check constraints**:
   ```sql
   ALTER TABLE rfqs ADD CONSTRAINT chk_deadline_future
     CHECK (dead_line_date >= created_at);
   ALTER TABLE quotations ADD CONSTRAINT chk_positive_amounts
     CHECK (unit_price >= 0 AND total_amount >= 0);
   ```

3. **Consider partitioning** for large `quotations` table by year/quarter

### Architecture Improvements
1. **Extract authorization to policies**:
   - `RfqPolicy` for RFQ access control
   - `QuotationPolicy` for quotation operations

2. **Split large services**:
   - `RfqDocumentService` for document handling
   - `QuotationCalculationService` for pricing logic
   - `QuotationDocumentService` for quotation documents

3. **Add event-driven architecture**:
   - `QuotationSubmitted` event → triggers notifications
   - `RfqExpired` event → closes expired RFQs
   - `QuotationAccepted` event → triggers purchase order creation

4. **Fix naming**:
   - Rename `QutationService` → `QuotationServiceItem`
   - Create migration to update foreign key references

### Caching Strategy
1. **Cache public RFQ listings** with TTL based on deadline proximity
2. **Cache quotation counts** for RFQ detail pages
3. **Use Redis for rate limiting** on quotation submissions

### Monitoring & Observability
1. Add metrics for:
   - RFQ-to-quotation conversion rate
   - Average time to first quotation
   - Quotation acceptance rate by vendor
2. Add logging for:
   - RFQ deadline expirations
   - Failed quotation submissions
   - Private RFQ delivery failures
