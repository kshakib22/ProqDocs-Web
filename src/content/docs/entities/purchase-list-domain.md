---
aliases: []
tags: [laravel, backend, auto-generated]
title: "PurchaseList-Domain"
---
# PurchaseList-Domain

The PurchaseList domain manages the procurement cart where buyers accumulate items for purchase orders. Items can be added from RFQs, quotations, or directly from BOQ entries. This domain bridges the [RFQ-Quotation-Domain](/ProqDocs-Web/entities/rfq-quotation-domain/) and [BoqEntry-BoqSheet-Domain](/ProqDocs-Web/entities/boq-entry-boq-sheet-domain/) with the purchase order workflow.

## Current Architecture & Flow

### PurchaseList Creation Flows

1. **From RFQ** via `PurchaseListService::addToPurchaseListFromRfq()`
   - Buyer selects a product from an RFQ
   - Creates/links to a pending PurchaseOrder
   - Calculates: `total_price = unit_price × estimated_quantity`
   - Calculates tax: `tax_amount = total_price × vat_rate / 100`
   - Status: `pending`, `is_ordered: false`

2. **From Quotation** via `PurchaseListService::addToPurchaseListFromQuotation()`
   - Buyer accepts a quotation from a vendor
   - Validates quotation status is `in_review`
   - Uses BOQ entry data with fallback to quotation data
   - Includes: shipping, loading, services charges
   - Recalculates purchase order totals after addition

3. **Direct from BOQ Entry** via `PurchaseListService::addToPurchaseListDirect()`
   - Buyer adds items directly from BOQ without quotation
   - Uses BOQ entry pricing and quantities
   - Creates purchase order if none exists for vendor/project/buyer

### Purchase Order Management

**Auto-Creation Pattern**: `createOrServePurchaseOrder()`
- Finds existing pending purchase order for (buyer, vendor, project) triplet
- Creates new order if none exists with unique order number: `PO-{vendor_id}-{hex}`
- Initializes with zero totals, status: `pending`

**Costing Updates**:
- `updatePurchaseOrderCosting()` - Incremental updates (legacy, used in RFQ flow)
- `recalculatePurchaseOrderCosting()` - Full recalculation from all purchase lists (preferred)

### PurchaseList Status Lifecycle

- `pending` → Initial state, not yet ordered
- `ordered` → Linked to confirmed purchase order
- `cancelled` → Removed from purchase order

### Key Relationships

```
PurchaseList → belongs to → PurchaseOrder
PurchaseList → belongs to → Buyer, Vendor, Project
PurchaseList → belongs to → Product, Quotation, Rfq
PurchaseList → belongs to → BoqSheet, BoqEntry
PurchaseOrder → has many → PurchaseList
```

### Query Patterns

...

## Dependencies & Graph Links

### Models
- [PurchaseList Model](/ProqDocs-Web/entities/purchaselist-model/) - Purchase list entity with scopes
- [PurchaseOrder Model](/ProqDocs-Web/entities/purchaseorder-model/) - Parent purchase order with status counts

### Services
- [PurchaseListService](/ProqDocs-Web/entities/purchaselistservice/) - Purchase list business logic (451 lines)

### Controllers
- [PurchaseOrderController](/ProqDocs-Web/entities/purchaseordercontroller/) - Purchase order endpoints that manage purchase lists

### Resources
- [PurchaseListResource](/ProqDocs-Web/entities/purchaselistresource/) - Purchase list API transformation with image handling

### Related Domains
- [RFQ-Quotation-Domain](/ProqDocs-Web/entities/rfq-quotation-domain/) - Source of RFQ-based purchase lists
- [BoqEntry-BoqSheet-Domain](/ProqDocs-Web/entities/boq-entry-boq-sheet-domain/) - Source of BOQ-based purchase lists

...