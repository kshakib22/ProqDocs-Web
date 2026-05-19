---
aliases: [Rfq]
tags: [laravel, backend, auto-generated, model, rfq]
title: "Rfq Model"
---
# Rfq Model

Request for Quotation entity. It represents a buyer's request for products or services, which can be either public (visible to all vendors) or private (targeted at a specific vendor).

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
- `buyer()`: BelongsTo [Buyer Model](/ProqDocs-Web/entities/buyer-model/)
- `vendor()`: BelongsTo [Vendor Model](/ProqDocs-Web/entities/vendor-model/) (only for private RFQs)        
- `product()`: BelongsTo [Product Model](/ProqDocs-Web/entities/product-domain/)
- `project()`: BelongsTo [Project Model](/ProqDocs-Web/entities/project-domain/)
- `category()`: BelongsTo [Category Model](/ProqDocs-Web/entities/category-model/)
- `documents()`: MorphMany [Document Model](/ProqDocs-Web/entities/document-model/)
- `quotations()`: HasMany [Quotation Model](/ProqDocs-Web/entities/quotation-model/)
- `purchaseList()`: HasOne [Purchase List Model](/ProqDocs-Web/entities/purchase-list-domain/)

### Scopes
- `public()`: Filter public RFQs
- `private()`: Filter private RFQs
- `active()`: Filter RFQs with future deadlines

## Dependencies & Graph Links

- Used by [Rfq Service](/ProqDocs-Web/entities/rfq-service/) for all RFQ operations
- Referenced by [Quotation Model](/ProqDocs-Web/entities/quotation-model/) via `rfq_id`
- Transformed by [Rfq Resource](/ProqDocs-Web/entities/rfq-resource/), [Public Rfq Resource](/ProqDocs-Web/entities/public-rfq-resource/), [Private Rfq Resource](/ProqDocs-Web/entities/private-rfq-resource/)
- [Rfq Controller](/ProqDocs-Web/entities/rfq-controller/) - API endpoints for buyers.
- PrivateRfqCreatedNotification - Notifies vendors of private requests.

## Red Flags & Tech Debt

- **Manual File Cleanup**: The `deleteRfq` method in [Rfq Service](/ProqDocs-Web/entities/rfq-service/) manually iterates through documents and deletes physical files from storage. This should ideally be handled by model observers or a dedicated media library.
- **UUID Generation**: Uses `Str::uuid()` in a loop to ensure uniqueness for `rfq_code`. While safe, it's performed in PHP rather than via DB constraints.

## Future Upgrades (Postgres & Scalability)

- **Elasticsearch Integration**: Public RFQs should be indexed in [Elasticsearch Domain](/ProqDocs-Web/entities/elasticsearch-domain/) for better vendor searchability.
- **State Machine**: Implement a proper state machine for status transitions to prevent invalid status hops.
