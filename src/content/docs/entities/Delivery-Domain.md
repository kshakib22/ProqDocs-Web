---
title: "Delivery Domain"
---

# Delivery Domain

## Overview

The Delivery domain manages the shipment and delivery lifecycle of purchase orders. It handles the creation of delivery details, shipment planning, item tracking, and financial calculations for delivery-related charges including shipping, loading/unloading, services, and platform fees.

## Core Entities

### DeliveryDetail

**File**: `app/Models/DeliveryDetail.php`

**Purpose**: Represents the delivery plan for a purchase order, containing financial summaries and shipment information.

**Relationships**:
- `purchaseOrder()` → [PurchaseOrder](/entities/purchaseorder-domain) (BelongsTo)
- `shipments()` → [Shipment](/entities/shipment-model) (HasMany)

**Key Methods**:
- `calculateFinancialSummary()` - Recalculates all delivery-related charges and updates both DeliveryDetail and PurchaseOrder

**Financial Fields**:
- `sub_total` - Base amount from purchase order
- `delivery_cost` - Sum of all shipment charges
- `loading_unloading_charge` - Sum of all loading/unloading charges
- `services_charge` - Sum of all services charges from shipments
- `platform_fee` - Calculated percentage based on total amount using [PlatformFeeSlab](/entities/platformfeeslab)
- `tax_amount` - Tax from purchase order
- `total_amount` - Final total including all charges
- `status` - Current delivery status

**Red Flags**:
- No database indexes on `purchase_order_id` or `status`
- No check constraints for positive amounts
- `calculateFinancialSummary()` performs multiple database queries without transaction

---

### Shipment

**File**: `app/Models/Shipment.php`

**Purpose**: Represents a single shipment within a delivery detail, containing delivery date, charges, and status.

**Relationships**:
- `deliveryDetail()` → [DeliveryDetail](/entities/deliverydetail-model) (BelongsTo)
- `shipmentItems()` → [ShipmentItem](/entities/shipmentitem-model) (HasMany)

**Key Fields**:
- `expected_delivery_date` - Planned delivery date
- `shipment_charge` - Shipping cost for this shipment
- `loading_unloading_charge` - Loading/unloading cost for this shipment
- `services_charge` - Additional services cost for this shipment
- `status` - `pending`, `in_transit`, `delivered`, `cancelled`
- `shipment_time` - Timestamp when shipment was dispatched

**Eager Loading**: Always loads `shipmentItems` by default (`protected $with`)

**Red Flags**:
- No database indexes on `status` or `shipment_time`
- No check constraints for positive charges
- Default eager loading may cause unnecessary queries

---

### ShipmentItem

**File**: `app/Models/ShipmentItem.php`

**Purpose**: Represents individual items within a shipment, linking to purchase lists and RFQs.

**Relationships**:
- `shipment()` → [Shipment](/entities/shipment-model) (BelongsTo)
- `purchaseList()` → [PurchaseList](/entities/purchaselist-domain) (BelongsTo)
- `rfq()` → [Rfq](/entities/rfq-quotation-domain) (BelongsTo)

**Key Fields**:
- `quantity` - Quantity for this shipment (can be partial from purchase list)
- `services` - JSON array of additional services with pricing

**Eager Loading**: Always loads `purchaseList` and `rfq` by default (`protected $with`)

**Red Flags**:
- No database indexes on `quantity` for partial shipment queries
- No validation that quantity doesn't exceed purchase list quantity
- Default eager loading may cause unnecessary queries

---

## Services

### DeliveryDetailService

**File**: `app/Service/DeliveryDetailService.php`

**Purpose**: Business logic for creating and managing delivery details and shipments.

**Key Methods**:

#### `createFromPurchaseOrder(PurchaseOrder $purchaseOrder): DeliveryDetail`
Creates a new DeliveryDetail from a confirmed purchase order.

**Red Flags**:
- Line 37: Incomplete variable `$purchaseOrder->ser` - appears to be a typo, should be `$purchaseOrder->services_charge`
- No check if DeliveryDetail already exists (commented out check on line 31)
- No database transaction for creation

#### `createShipment(DeliveryDetail $deliveryDetail, $purchaseOrder, array $data): Shipment`
Creates a single shipment with items and services.

**Red Flags**:
- Lines 99-103: Inefficient null check for `purchase_list_id` - should use validation
- Line 106: Commented out `rfq_id` logic - incomplete feature
- Lines 109-120: Complex services array transformation in service layer
- No validation that total quantity matches purchase list requirements

#### `createShipments(PurchaseOrder $purchaseOrder, array $data): array`
Creates multiple shipments and payment infos in a transaction.

**Red Flags**:
- Line 87: Debug logger statement in production code
- Line 155: Debug logger statement in production code
- Line 57: Debug logger statement in production code
- No validation that all purchase list items are covered by shipments
- No validation that total shipment charges are reasonable

#### `updateShipment(Shipment $shipment, array $data): array`
Updates shipment details and recalculates financial summary.

**Red Flags**:
- No validation that status transitions are valid (e.g., can't go from `delivered` back to `pending`)
- No audit trail for status changes

#### `deleteShipment(Shipment $shipment): array`
Deletes a shipment and recalculates financial summary.

**Red Flags**:
- No check if shipment has already been shipped or delivered
- No soft delete for audit trail

#### `savePaymentInfo(PurchaseOrder $purchaseOrder, array $data)`
Saves payment information for the purchase order.

**Red Flags**:
- Line 308: Typo `installation_number` should be `installment_number`
- No validation that total payment amounts match purchase order total
- No check for duplicate payment types

---

## Controllers

### Buyer/DeliveryDetailsController

**File**: `app/Http/Controllers/Buyer/DeliveryDetailsController.php`

**Purpose**: Buyer endpoints for viewing delivery details.

**Endpoints**:
- `showByPurchaseOrder(PurchaseOrder $purchaseOrder)` - View delivery details for a purchase order
- `show(DeliveryDetail $deliveryDetail)` - View a specific delivery detail

**Red Flags**:
- Manual authorization checks instead of using [DeliveryDetailPolicy](/entities/deliverydetailpolicy)
- No caching for frequently accessed delivery details
- No rate limiting on endpoints

---

### Vendor/DeliveryDetailsController

**File**: `app/Http/Controllers/Vendor/DeliveryDetailsController.php`

**Purpose**: Vendor endpoints for creating and managing delivery details.

**Endpoints**:
- `storeFromPurchaseOrder(Request $request, Vendor $vendor, PurchaseOrder $purchaseOrder)` - Create delivery details and shipments
- `showByPurchaseOrder(Vendor $vendor, PurchaseOrder $purchaseOrder)` - View delivery details
- `confirmShipments(Request $request, Vendor $vendor, PurchaseOrder $purchaseOrder)` - Mark all shipments as in transit

**Red Flags**:
- Lines 55-57: Debug logger statements in production code
- Line 98-100: Updates all shipments without database transaction
- No validation that all items are covered before confirming shipments
- No check for minimum shipment requirements
- Manual authorization checks instead of using [DeliveryDetailPolicy](/entities/deliverydetailpolicy)

---

## Resources

### DeliveryDetailResource

**File**: `app/Http/Resources/DeliveryDetailResource.php`

**Purpose**: API transformation for delivery details.

**Red Flags**:
- Lines 30-38: Duplicate `financial_summary` data - same fields repeated
- Line 39: Complex conditional loading for payment infos
- No pagination for shipments array

---

### ShipmentResource

**File**: `app/Http/Resources/ShipmentResource.php`

**Purpose**: API transformation for shipments.

**Red Flags**:
- No human-readable status labels
- No calculated fields like `total_charge` (shipment + loading + services)

---

### ShipmentItemResource

**File**: `app/Http/Resources/ShipmentItemResource.php`

**Purpose**: API transformation for shipment items.

**Red Flags**:
- Line 32: Complex calculation `shipment_item_value` in resource layer - should be in model
- Line 24: Ternary operator for null check could be simplified
- No validation that `purchaseList` exists before accessing `unit_price`

---

## Database Schema

### delivery_details Table

**Migration**: `database/migrations/Boq/2025_12_18_121622_create_delivery_details_table.php`

**Columns**:
- `id` - Primary key
- `purchase_order_id` - Foreign key to [purchase_orders](/entities/purchaseorder-domain)
- `sub_total` - Base amount
- `delivery_cost` - Total shipping charges
- `loading_unloading_charge` - Total loading/unloading charges
- `platform_fee` - Platform fee percentage
- `services_charge` - Total services charges
- `tax_amount` - Tax amount
- `total_amount` - Final total
- `status` - Delivery status
- `created_at`, `updated_at` - Timestamps

**Red Flags**:
- No indexes on `purchase_order_id` or `status`
- No check constraints for positive amounts
- No unique constraint on `purchase_order_id` (should be 1:1)

---

### shipments Table

**Migration**: `database/migrations/Boq/2025_12_18_121632_create_shipments_table.php`

**Columns**:
- `id` - Primary key
- `delivery_detail_id` - Foreign key to [delivery_details](/entities/deliverydetail-model)
- `expected_delivery_date` - Planned delivery date
- `shipment_charge` - Shipping cost
- `loading_unloading_charge` - Loading/unloading cost
- `services_charge` - Services cost
- `status` - `pending`, `in_transit`, `delivered`, `cancelled`
- `created_at`, `updated_at` - Timestamps

**Red Flags**:
- No index on `status` for filtering
- No check constraints for positive charges
- No `shipment_time` column in migration (used in controller but not in schema)

---

### shipment_items Table

**Migration**: `database/migrations/Boq/2025_12_18_121640_create_shipment_items_table.php`

**Columns**:
- `id` - Primary key
- `shipment_id` - Foreign key to shipments
- `purchase_list_id` - Foreign key to [purchase_lists](/entities/purchaselist-domain)
- `rfq_id` - Foreign key to [rfqs](/entities/rfq-quotation-domain) (nullable)
- `quantity` - Shipment quantity
- `services` - JSON array of services
- `created_at`, `updated_at` - Timestamps

**Red Flags**:
- No check constraint that quantity is positive
- No validation that quantity doesn't exceed purchase list quantity
- No index on `quantity` for partial shipment queries

---

## Cross-References

- [PurchaseOrder-Domain](/entities/purchaseorder-domain) - Delivery details are created from purchase orders
- [PurchaseList-Domain](/entities/purchaselist-domain) - Shipment items reference purchase lists
- [RFQ-Quotation-Domain](/entities/rfq-quotation-domain) - Shipment items reference RFQs for tracking
- [Payment-Domain](/entities/payment-domain) - Payment infos are saved with delivery details

---

## Critical Issues Summary

1. **Typo in variable name**: Line 37 in `DeliveryDetailService::createFromPurchaseOrder()` uses `$purchaseOrder->ser` instead of `$purchaseOrder->services_charge`
2. **Typo in field name**: Line 308 in `DeliveryDetailService::savePaymentInfo()` uses `installation_number` instead of `installment_number`
3. **Missing database indexes**: No indexes on `purchase_order_id`, `status` in delivery-related tables
4. **No check constraints**: No database-level validation for positive amounts
5. **Debug logger statements**: Multiple logger statements in production code (lines 55, 57, 87, 155 in DeliveryDetailService)
6. **No transaction for shipment confirmation**: `confirmShipments()` updates multiple records without transaction
7. **Duplicate data in resource**: `financial_summary` in `DeliveryDetailResource` duplicates existing fields
8. **Business logic in resource layer**: `shipment_item_value` calculation in `ShipmentItemResource` should be in model
9. **No audit trail**: No soft deletes or status change tracking
10. **No validation for partial shipments**: No check that total shipment quantities match purchase list requirements
