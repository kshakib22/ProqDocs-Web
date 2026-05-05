---
aliases: []
tags: [laravel, backend, auto-generated]
title: "PurchaseList-Domain"
---
# PurchaseList-Domain

The PurchaseList domain manages the procurement cart where buyers accumulate items for purchase orders. Items can be added from RFQs, quotations, or directly from BOQ entries. This domain bridges the [RFQ-Quotation-Domain](./RFQ-Quotation-Domain.md) and [BoqEntry-BoqSheet-Domain](./BoqEntry-BoqSheet-Domain.md) with the purchase order workflow.

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

**By Vendor**: `getPurchaseListsByVendor()`
- Filters by vendor_id, unordered items
- Returns total count and total_amount

**Grouped by Vendor**: `getPurchaseListsByVendors()`
- Paginated vendor groups
- Each group contains items, total count, total_amount
- Uses complex SQL with subquery for pagination

**Filtered Search**: `getPurchaseLists()`
- Supports filtering by: search, status, project_id, vendor_id, buyer_id, rfq_id, product_id
- Supports sorting by any field
- Paginated results

## Dependencies & Graph Links

### Models
- [PurchaseList Model](./PurchaseList Model.md) - Purchase list entity with scopes
- [PurchaseOrder Model](./PurchaseOrder Model.md) - Parent purchase order with status counts

### Services
- [PurchaseListService](./PurchaseListService.md) - Purchase list business logic (451 lines)

### Controllers
- [PurchaseOrderController](./PurchaseOrderController.md) - Purchase order endpoints that manage purchase lists

### Resources
- [PurchaseListResource](./PurchaseListResource.md) - Purchase list API transformation with image handling

### Related Domains
- [RFQ-Quotation-Domain](./RFQ-Quotation-Domain.md) - Source of RFQ-based purchase lists
- [BoqEntry-BoqSheet-Domain](./BoqEntry-BoqSheet-Domain.md) - Source of BOQ-based purchase lists

## Red Flags & Tech Debt

### Service Layer Issues

**[PurchaseListService](./PurchaseListService.md)**: 451 lines with multiple concerns

1. **Inconsistent Costing Methods**:
   - `updatePurchaseOrderCosting()` - Incremental updates (lines 415-425)
   - `recalculatePurchaseOrderCosting()` - Full recalculation (lines 427-449)
   - Both exist, but recalculation is preferred for data integrity
   - RFQ flow still uses incremental method (line 213)

2. **Duplicate Status Filter**:
   - Lines 31-32 and 67-69 both filter by `status`
   - Redundant code in `getPurchaseLists()`

3. **Broken Sort Logic** (lines 82-88):
   ```php
   if($request->has('sort_by')){
       $query->orderBy($request->sort_by, $request->sort_order);
   }
   if($request->has('sort_order')){
       $purchaseLists = $query->paginate(10);
   }
   ```
   - Second condition only paginates, doesn't apply sort
   - Should be combined or fixed

4. **Commented-Out Code**:
   - Lines 328-342: `createOrServePurchaseOrderFromBoqEntry()` - dead code
   - Lines 384-412: `createPurchaseOrderFromBoqEntry()` - dead code
   - Lines 404-413: `updatePurchaseOrderFromPurchaseList()` - dead code

5. **Complex Vendor Grouping Query** (lines 121-178):
   - Uses subquery for pagination
   - Multiple database queries for aggregation
   - Could be optimized with single query

### Data Integrity

1. **No Database Constraints**:
   - No check constraint for positive amounts
   - No unique constraint on (buyer, vendor, project, product) combinations
   - Status enum only at application level

2. **Soft Delete Handling**:
   - No soft delete on purchase_lists
   - Related entities (RFQ, Quotation) use soft deletes
   - Orphaned purchase lists possible if parent deleted

3. **Race Conditions**:
   - `createOrServePurchaseOrder()` not atomic
   - Multiple concurrent requests could create duplicate orders
   - Should use database-level locking or unique constraint

### Performance

1. **N+1 Queries**:
   - `getPurchaseListsByVendors()` loads items in loop (line 158)
   - Each vendor group triggers separate query

2. **No Indexes on Common Filters**:
   - Migration only indexes `vendor_id` and `purchase_order_id`
   - Missing indexes on: `buyer_id`, `project_id`, `status`, `is_ordered`

3. **Image Handling in Resource**:
   - `PurchaseListResource` checks storage for each image
   - Could be cached or pre-processed

## Future Upgrades (Postgres & Scalability)

### Database Optimizations

1. **Add composite indexes**:
   ```sql
   CREATE INDEX idx_purchase_lists_buyer_vendor_project
     ON purchase_lists(buyer_id, vendor_id, project_id, status);
   CREATE INDEX idx_purchase_lists_vendor_ordered
     ON purchase_lists(vendor_id, is_ordered, status);
   CREATE INDEX idx_purchase_lists_project_status
     ON purchase_lists(project_id, status, created_at DESC);
   ```

2. **Add check constraints**:
   ```sql
   ALTER TABLE purchase_lists ADD CONSTRAINT chk_positive_amounts
     CHECK (quantity >= 0 AND unit_price >= 0 AND total_amount >= 0);
   ALTER TABLE purchase_lists ADD CONSTRAINT chk_status_ordered_consistency
     CHECK (
       (status = 'ordered' AND is_ordered = true) OR
       (status != 'ordered' AND is_ordered = false)
     );
   ```

3. **Add unique constraint** for order creation:
   ```sql
   CREATE UNIQUE INDEX idx_unique_pending_order
     ON purchase_orders(buyer_id, vendor_id, project_id)
     WHERE status = 'pending';
   ```

4. **Consider partitioning** for large `purchase_lists` table by year/quarter

### Architecture Improvements

1. **Extract costing logic**:
   - `PurchaseOrderCostingService` for all cost calculations
   - Remove incremental method, use only recalculation
   - Add event listeners for cost updates

2. **Fix vendor grouping query**:
   - Use single query with window functions
   - Or use database-specific pagination features

3. **Add database-level locking**:
   - Use `SELECT FOR UPDATE` in `createOrServePurchaseOrder()`
   - Or use unique constraint with `ON CONFLICT DO NOTHING`

4. **Remove dead code**:
   - Delete commented-out methods
   - Clean up unused imports

5. **Add validation layer**:
   - Form request validation for all inputs
   - Remove manual field filtering

### Caching Strategy

1. **Cache vendor groupings** with TTL based on activity
2. **Cache purchase order totals** with invalidation on purchase list changes
3. **Use Redis for rate limiting** on purchase list additions

### Monitoring & Observability

1. Add metrics for:
   - Purchase list to purchase order conversion rate
   - Average time from creation to order
   - Purchase list abandonment rate
2. Add logging for:
   - Purchase order creation conflicts
   - Cost calculation discrepancies
   - Failed purchase list additions
