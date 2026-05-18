---
aliases: []
tags: [laravel, backend, auto-generated]
title: "RFQ-Quotation-Domain"
---
# RFQ-Quotation-Domain

The Request for Quotation (RFQ) and Quotation domain manages the procurement workflow where buyers request quotes and vendors submit quotations. This is a core business domain connecting Buyer-Domain, **[Vendor-Domain](/entities/vendor-domain)**, and **[Product-Domain](/entities/product-domain)**.

## Current Architecture & Flow

### RFQ (Request for Quotation) Flow

1. **Buyer creates RFQ** via **[RfqController](/entities/rfqcontroller)** → **[RfqService](/entities/rfqservice)**
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

1. **Vendor submits quotation** via **[QuotationController](/entities/quotationcontroller)** → **[QuotationService](/entities/quotationservice)**
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
- **[Rfq Model](/entities/rfq-model)** - RFQ entity with soft deletes
- **[Quotation Model](/entities/quotation-model)** - Quotation entity with soft deletes
- **[QutationService Model](/entities/qutationservice-model)** - Quotation line items (note: typo in class name)

### Services
- **[RfqService](/entities/rfqservice)** - RFQ business logic (654 lines)
- **[QuotationService](/entities/quotationservice)** - Quotation business logic (800 lines)
- QuotationBoostScoreService - Subscription-based quotation ranking

### Controllers
- **[RfqController](/entities/rfqcontroller)** - Buyer RFQ endpoints
- **[QuotationController](/entities/quotationcontroller)** - Vendor quotation endpoints

### Resources
- **[RfqResource](/entities/rfqresource)** - RFQ API transformation
- **[QuotationResource](/entities/quotationresource)** - Quotation API transformation
- PublicRfqResource - Public RFQ view for vendors
- PrivateRfqResource - Private RFQ view

...
- **[RfqController](/entities/rfqcontroller)**: 613 lines with extensive inline authorization checks
  - Authorization logic repeated across methods
  - Should extract to policies or middleware

- **[QuotationController](/entities/quotationcontroller)**: 577 lines with similar issues
  - Mixed concerns: authorization, validation, business logic
  - JWTAuth mixed with Auth facade

### Service Layer Issues
- **[RfqService](/entities/rfqservice)**: 654 lines - large service class
  - Multiple responsibilities: RFQ CRUD, document handling, public/private RFQs
  - `updateRfq()` has manual field filtering (lines 228-271) - should use request validation
  - Commented-out code for category sync and purchase list integration

- **[QuotationService](/entities/quotationservice)**: 800 lines - largest service in codebase
  - Complex document upload handling with multiple formats (uploaded file, base64)
  - Manual total calculation logic scattered throughout
  - `createQuotation()` has extensive logging and conditional logic

### Naming Issues
- **[QutationService Model](/entities/qutationservice-model)**: Typo in class name ("Qutation" instead of "Quotation")
  - This is a breaking change waiting to happen
  - Used throughout the codebase

...