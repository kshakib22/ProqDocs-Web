---
aliases: []
tags: [laravel, backend, auto-generated]
title: "Quotation Model"
---
# Quotation Model

The Quotation model represents a vendor's response to an RFQ. It contains pricing details, terms, and supporting documents.

## Current Architecture & Flow

### Model Structure
- **Table**: `quotations`
- **Soft Deletes**: Enabled
- **Key Attributes**:
  - `quotation_number`: Unique identifier (format: `QT-{rfq_id}-{random}`)
  - `status`: `in_review`, `accepted`, `rejected`
  - `unit_count`: Quantity being quoted
  - `unit_price`: Price per unit
  - `sub_amount`: Subtotal (unit_count × unit_price)
  - `services_charge`: Total of [QutationService Model](QutationService Model.md) items
  - `total_amount`: Final total (subtotal + services + tax + shipping + loading)
  - `vat_rate`: VAT percentage
  - `tax_amount`: Calculated tax amount
  - `shipping_amount`: Shipping cost
  - `loading_charge`: Loading/handling fee
  - `validity_period`: Days until quotation expires
  - `quotation_date`: Date quotation was issued

### Relationships
- `rfq()`: BelongsTo [Rfq Model](Rfq Model.md) (withTrashed)
- `vendor()`: BelongsTo [Vendor Model](Vendor Model.md)
- `buyer()`: BelongsTo [Buyer Model](Buyer Model.md)
- `user()`: BelongsTo [User Model](User Model.md)
- `project()`: BelongsTo [Project Model](Project Model.md) (withTrashed)
- `product()`: BelongsTo [Product Model](Product Model.md) (withTrashed)
- `category()`: BelongsTo [Category Model](Category Model.md) (withTrashed)
- `documents()`: MorphMany [Document Model](Document Model.md)
- `quotationServices()`: HasMany [QutationService Model](QutationService Model.md)

### Total Calculation Formula
```
total_amount = sub_amount + services_charge + tax_amount + shipping_amount + loading_charge
```

## Dependencies & Graph Links

- Created by [QuotationService](QuotationService.md)
- Referenced by [Rfq Model](Rfq Model.md) via `quotations()` relationship
- Transformed by [QuotationResource](QuotationResource.md)
- Triggers [QuotationSubmittedNotification](QuotationSubmittedNotification.md) and [QuotationUpdatedNotification](QuotationUpdatedNotification.md)

## Red Flags & Tech Debt

### Missing Database Constraints
- No check constraint ensuring `total_amount >= 0`
- No unique constraint on `quotation_number` (only application-level)
- No constraint preventing multiple quotations from same vendor for same RFQ

### Business Logic in Service Layer
- Total calculation logic is in [QuotationService](QuotationService.md) instead of model
- No model-level validation for status transitions
- `withTrashed()` on relationships suggests potential orphan data issues

### Data Integrity
- No database-level enforcement of one-quotation-per-vendor-per-RFQ
- Soft deletes may leave orphaned documents

## Future Upgrades (Postgres & Scalability)

### Database Improvements
```sql
-- Add check constraints
ALTER TABLE quotations ADD CONSTRAINT chk_positive_amounts
  CHECK (unit_price >= 0 AND total_amount >= 0 AND sub_amount >= 0);

-- Add unique constraint for vendor-RFQ combination
CREATE UNIQUE INDEX idx_quotations_vendor_rfq
  ON quotations(vendor_id, rfq_id)
  WHERE deleted_at IS NULL;

-- Add composite indexes for common queries
CREATE INDEX idx_quotations_rfq_vendor ON quotations(rfq_id, vendor_id);
CREATE INDEX idx_quotations_status_created ON quotations(status, created_at DESC);
CREATE INDEX idx_quotations_buyer_status ON quotations(buyer_id, status);
```

### Model Enhancements
1. Add `calculateTotal()` method to encapsulate pricing logic
2. Add status transition validation
3. Add `isExpired()` accessor based on validity_period
4. Consider adding `is_valid` computed column
5. Add event listeners for status changes

### Performance
- Add partial index for active quotations
- Consider materialized view for quotation statistics
