---
aliases: []
tags: [laravel, backend, auto-generated]
title: "Rfq Model"
---
# Rfq Model

The RFQ (Request for Quotation) model represents a buyer's request for product quotes. It's the central entity in the procurement workflow.

## Current Architecture & Flow

### Model Structure
- **Table**: `rfqs`
- **Soft Deletes**: Enabled
- **Key Attributes**:
  - `rfq_code`: Unique identifier (format: `RFQ-{type}-{uuid}`)
  - `rfq_title`: Human-readable title
  - `type`: `public` or `private`
  - `status`: `in_review`, `active`, `accepted`, `rejected`, `cancelled`
  - `dead_line_date`: Quotation submission deadline
  - `budget_min`/`budget_max`: Price range expectations
  - `estimated_quantity`: Expected quantity
  - `urgency`: `low`, `medium`, `high`

### Relationships
- `buyer()`: BelongsTo [Buyer Model](Buyer Model.md)
- `vendor()`: BelongsTo [Vendor Model](Vendor Model.md) (only for private RFQs)
- `product()`: BelongsTo [Product Model](Product Model.md)
- `project()`: BelongsTo [Project Model](Project Model.md)
- `category()`: BelongsTo [Category Model](Category Model.md)
- `documents()`: MorphMany [Document Model](Document Model.md)
- `quotations()`: HasMany [Quotation Model](Quotation Model.md)
- `purchaseList()`: HasOne [PurchaseList Model](PurchaseList Model.md)

### Scopes
- `public()`: Filter public RFQs
- `private()`: Filter private RFQs
- `active()`: Filter RFQs with future deadlines

### Accessors
- `is_private`: Returns true if type is 'private'
- `is_public`: Returns true if type is 'public'

## Dependencies & Graph Links

- Used by [RfqService](RfqService.md) for all RFQ operations
- Referenced by [Quotation Model](Quotation Model.md) via `rfq_id`
- Transformed by [RfqResource](RfqResource.md), [PublicRfqResource](PublicRfqResource.md), [PrivateRfqResource](PrivateRfqResource.md)

## Red Flags & Tech Debt

### Missing Database Constraints
- No check constraint ensuring `dead_line_date >= created_at`
- No unique constraint on `rfq_code` (only application-level validation)
- No foreign key cascade for soft-deleted related records

### Business Logic in Model
- Type checking logic in accessors could be moved to scopes
- No validation on status transitions

### Naming Inconsistency
- Uses `estimated_quantity` but related models use `unit_count` or `quantity`

## Future Upgrades (Postgres & Scalability)

### Database Improvements
```sql
-- Add check constraints
ALTER TABLE rfqs ADD CONSTRAINT chk_deadline_future
  CHECK (dead_line_date >= created_at);

-- Add composite indexes for common queries
CREATE INDEX idx_rfqs_buyer_status ON rfqs(buyer_id, status);
CREATE INDEX idx_rfqs_public_active ON rfqs(type, status, dead_line_date)
  WHERE type = 'public' AND status = 'active';

-- Add partial index for active RFQs
CREATE INDEX idx_rfqs_active_deadline ON rfqs(dead_line_date)
  WHERE status = 'active' AND dead_line_date >= CURRENT_DATE;
```

### Model Enhancements
1. Add status transition validation
2. Add deadline expiration scope
3. Consider adding `is_expired` computed column
4. Add event listeners for status changes
