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
- `buyer()`: BelongsTo [Buyer Model](/entities/buyer-model)
- `vendor()`: BelongsTo [Vendor Model](/entities/vendor-model) (only for private RFQs)
- `product()`: BelongsTo [Product Model](/entities/product-domain)
- `project()`: BelongsTo [Project Model](/entities/project-domain)
- `category()`: BelongsTo [Category Model](/entities/category-model)
- `documents()`: MorphMany [Document Model](/entities/document-model)
- `quotations()`: HasMany [Quotation Model](/entities/quotation-model)
- `purchaseList()`: HasOne [PurchaseList Model](/entities/purchaselist-model)

### Scopes
- `public()`: Filter public RFQs
- `private()`: Filter private RFQs
- `active()`: Filter RFQs with future deadlines

...

## Dependencies & Graph Links

- Used by [RfqService](/entities/rfqservice) for all RFQ operations
- Referenced by [Quotation Model](/entities/quotation-model) via `rfq_id`
- Transformed by [RfqResource](/entities/rfqresource), [PublicRfqResource](/entities/publicrfqresource), [PrivateRfqResource](/entities/privaterfqresource)

...