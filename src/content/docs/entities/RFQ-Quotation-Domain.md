---
aliases: []
tags: [laravel, backend, auto-generated]
title: "RFQ-Quotation-Domain"
---
# RFQ-Quotation-Domain

The Request for Quotation (RFQ) and Quotation domain manages the procurement workflow where buyers request quotes and vendors submit quotations. This is a core business domain connecting Buyer-Domain, **[Vendor-Domain](/ProqDocs-Web/entities/vendor-domain/)**, and **[Product-Domain](/ProqDocs-Web/entities/product-domain/)**.

## Current Architecture & Flow

### RFQ (Request for Quotation) Flow

1. **Buyer creates RFQ** via **[RfqController](/ProqDocs-Web/entities/rfq-controller/)** → **[RfqService](/ProqDocs-Web/entities/rfq-service/)**
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

1. **Vendor submits quotation** via **[QuotationController](/ProqDocs-Web/entities/quotation-controller/)** → **[QuotationService](/ProqDocs-Web/entities/quotation-service/)**
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
- **[Rfq Model](/ProqDocs-Web/entities/rfq-model/)** - RFQ entity with soft deletes
- **[Quotation Model](/ProqDocs-Web/entities/quotation-model/)** - Quotation entity with soft deletes
- **[QutationService Model](/ProqDocs-Web/entities/qutationservice-model/)** - Quotation line items (note: typo in class name)

### Services
- **[RfqService](/ProqDocs-Web/entities/rfq-service/)** - RFQ business logic (654 lines)
- **[QuotationService](/ProqDocs-Web/entities/quotation-service/)** - Quotation business logic (800 lines)
- QuotationBoostScoreService - Subscription-based quotation ranking

### Controllers
- **[RfqController](/ProqDocs-Web/entities/rfq-controller/)** - Buyer RFQ endpoints
- **[QuotationController](/ProqDocs-Web/entities/quotation-controller/)** - Vendor quotation endpoints

### Resources
- **[RfqResource](/ProqDocs-Web/entities/rfq-resource/)** - RFQ API transformation
- **[QuotationResource](/ProqDocs-Web/entities/quotation-resource/)** - Quotation API transformation
- PublicRfqResource - Public RFQ view for vendors
- PrivateRfqResource - Private RFQ view

...
- **[RfqController](/ProqDocs-Web/entities/rfq-controller/)**: 613 lines with extensive inline authorization checks
  - Authorization logic repeated across methods
  - Should extract to policies or middleware

- **[QuotationController](/ProqDocs-Web/entities/quotation-controller/)**: 577 lines with similar issues
  - Mixed concerns: authorization, validation, business logic
  - JWTAuth mixed with Auth facade

### Service Layer Issues
- **[RfqService](/ProqDocs-Web/entities/rfq-service/)**: 654 lines - large service class
  - Multiple responsibilities: RFQ CRUD, document handling, public/private RFQs
  - `updateRfq()` has manual field filtering (lines 228-271) - should use request validation
  - Commented-out code for category sync and purchase list integration

- **[QuotationService](/ProqDocs-Web/entities/quotation-service/)**: 800 lines - largest service in codebase
  - Complex document upload handling with multiple formats (uploaded file, base64)
  - Manual total calculation logic scattered throughout
  - `createQuotation()` has extensive logging and conditional logic

### Naming Issues
- **[QutationService Model](/ProqDocs-Web/entities/qutationservice-model/)**: Typo in class name ("Qutation" instead of "Quotation")
  - This is a breaking change waiting to happen
  - Used throughout the codebase

...