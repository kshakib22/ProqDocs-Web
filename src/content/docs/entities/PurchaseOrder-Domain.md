---
aliases: []
tags: [laravel, backend, auto-generated]
title: "PurchaseOrder Domain"
---
# PurchaseOrder Domain

## Overview

The PurchaseOrder Domain manages the procurement lifecycle from order creation through delivery confirmation. It serves as the central entity connecting [Buyer-Domain](Buyer-Domain.md), [Vendor-Domain](Vendor-Domain.md), [Product-Domain](Product-Domain.md), [RFQ-Quotation-Domain](RFQ-Quotation-Domain.md), and [PurchaseList-Domain](PurchaseList-Domain.md).

## Current Architecture & Flow

### Core Models

#### PurchaseOrder Model
**File:** `app/Models/PurchaseOrder.php`

The central entity representing a formal purchase order sent to a vendor.

**Key Attributes:**
- `order_number` - Unique PO identifier
- `status` - Order lifecycle: `pending`, `ordered`, `receipt_received`, `shipped`, `delivered`, `cancelled`
- `payment_status` - Payment state: `pending`, `paid`, `partial`
- `total_amount` - Final amount including all charges
- `due_amount` - Computed attribute (total - verified payments)
- `receipt_time`, `delivery_completion_time`, `confirm_time` - Timestamps for status transitions

**Relationships:**
- `belongsTo` [Project](Project.md), [Vendor](Vendor.md), [Buyer](Buyer.md)
- `hasMany` [PurchaseList](PurchaseList.md), [PurchaseOrderPayment](PurchaseOrderPayment.md), [PurchaseOrderTransactionDetail](PurchaseOrderTransactionDetail.md), [PurchaseOrderPaymentInfo](PurchaseOrderPaymentInfo.md)
- `hasOne` [DeliveryDetail](DeliveryDetail.md)
- `hasManyThrough` [Shipment](Shipment.md)

**Query Scopes:**
- `scopeStatusCounts()` - Aggregates order status counts
- `scopeStatusCountsByBuyer()` - Buyer-specific status aggregation
- `scopeStatusCountsByVendor()` - Vendor-specific status aggregation

**Issues:**
- Line 55: `cancelled_count` incorrectly maps to `shipped` status (typo)
- Line 56: `delivered_count` duplicated
- Line 67: Uses `||` instead of `OR` in SQL CASE statement
- `due_amount` accessor loads all `paymentInfos` relationship (N+1 risk)

#### PurchaseOrderPayment Model
**File:** `app/Models/PurchaseOrderPayment.php`

Represents payment records for purchase orders.

**Key Attributes:**
- `amount`, `total_payment`, `paid_amount`, `remaining_amount` - Financial tracking
- `paid_at` - Payment timestamp
- `metadata` - JSON for gateway-specific data

**Relationships:**
- `belongsTo` [PurchaseOrder](PurchaseOrder.md), [PaymentType](PaymentType.md), [Buyer](Buyer.md)
- `belongsTo` [PurchaseOrderTransactionDetail](PurchaseOrderTransactionDetail.md) (one-to-one)

**Helper Methods:**
- `isCompleted()` - Checks if payment status is completed
- `isFullyPaid()` - Checks if remaining amount is zero

#### PurchaseOrderTransactionDetail Model
**File:** `app/Models/PurchaseOrderTransactionDetail.php`

Tracks individual payment transactions with verification status.

**Key Attributes:**
- `total_payment`, `previous_payed`, `current_payment`, `remaining_payment` - Payment breakdown
- `is_verified` - Admin verification flag
- `verified_at`, `processed_at`, `completed_at` - Transaction timestamps
- `gateway_metadata` - JSON for gateway response data

**Constants:**
- `CHANNEL_ONLINE`, `CHANNEL_OFFLINE` - Payment channels
- `PAYMENT_METHODS` - Supported methods: SSL Commerce, Bank Transfer, Cash, Cheque, BEFTN, RTGS, NPSB

**Relationships:**
- `hasOne` [PurchaseOrderPayment](PurchaseOrderPayment.md)
- `belongsTo` [PurchaseOrder](PurchaseOrder.md), [PaymentType](PaymentType.md), [Buyer](Buyer.md)

**Helper Methods:**
- `isSuccess()` - Checks status + verification
- `isPending()`, `isFailed()` - Status checks

**Query Scopes:**
- `scopeSuccess()`, `scopePending()`, `scopeVerified()`, `scopeForPurchaseOrder()`

#### PurchaseOrderPaymentInfo Model
**File:** `app/Models/PurchaseOrderPaymentInfo.php`

Stores verified payment information for due amount calculations.

**Relationships:**
- `belongsTo` [PurchaseOrder](PurchaseOrder.md)

### Controllers

#### Buyer/PurchaseOrderController
**File:** `app/Http/Controllers/Buyer/PurchaseOrderController.php` (421 lines)

**Endpoints:**
- `getPurchaseOrders()` - List buyer's POs with filtering by status/project
- `confirmPurchaseOrder()` - Move PO from `pending` to `ordered`
- `show()` - View single PO with full details
- `view()` - Web view for PDF rendering
- `downloadPdf()` - Generate PDF using Spatie PDF/Browsershot
- `confirmDelivery()` - Mark PO as `delivered` when shipment received

**Issues:**
- Lines 244-398: PDF generation code duplicated with Vendor controller (150+ lines)
- Lines 248-276: Node.js path detection logic duplicated
- Lines 296-337: Chrome path detection logic duplicated
- No service layer - business logic embedded in controller
- `confirmDelivery()` updates shipments without transaction wrapper

#### Vendor/PurchaseOrderController
**File:** `app/Http/Controllers/Vendor/PurchaseOrderController.php` (259 lines)

**Endpoints:**
- `index()` - List vendor's POs with status filtering
- `show()` - View single PO with shipment details
- `downloadPdf()` - Generate PDF (same duplication as buyer)

**Issues:**
- Lines 80-256: PDF generation code duplicated with Buyer controller
- Same Node.js/Chrome path detection duplication
- No service layer

### Resources

#### PurchaseOrderResource
**File:** `app/Http/Resources/PurchaseOrderResource.php`

Standard PO representation with:
- Basic order info (number, amounts, status)
- Related entity names (vendor, buyer, project)
- Purchase lists collection
- Computed fields (due_amount, platform_fee)

#### PurchaseOrderWithShipmentResource
**File:** `app/Http/Resources/PurchaseOrderWithShipmentResource.php`

Extended representation including:
- Delivery detail with shipments count
- Payment info and payments collections
- All timestamps formatted

#### PurchaseOrderWithPaymentResource
**File:** `app/Http/Resources/PurchaseOrderWithPaymentResource.php`

Payment-focused representation with:
- Payment info and payments collections
- Minimal order details

#### PurchaseOrderPaymentResource
**File:** `app/Http/Resources/PurchaseOrderPaymentResource.php`

Payment transformation (not shown in output - likely minimal)

### Notifications

#### PurchaseOrderPaymentVendorNotification
**File:** `app/Notifications/PurchaseOrderPaymentVendorNotification.php`

Notifies vendor when buyer makes payment.

#### PurchaseOrderPaymentBuyerNotification
**File:** `app/Notifications/PurchaseOrderPaymentBuyerNotification.php`

Notifies buyer about their payment status.

## Dependencies & Graph Links

### Domain Dependencies
- [Buyer-Domain](Buyer-Domain.md) - PO owner
- [Vendor-Domain](Vendor-Domain.md) - PO recipient
- [Project-Domain](Project-Domain.md) - Associated project
- [Product-Domain](Product-Domain.md) - Items being purchased
- [RFQ-Quotation-Domain](RFQ-Quotation-Domain.md) - Source of pricing
- [PurchaseList-Domain](PurchaseList-Domain.md) - Line items
- [Payment-Domain](Payment-Domain.md) - Payment processing
- [Delivery-Domain](Delivery-Domain.md) - Shipment tracking

### Cross-Domain Flows
1. **PO Creation:** [PurchaseList-Domain](PurchaseList-Domain.md) → PurchaseOrder (items aggregated)
2. **Payment:** [Payment-Domain](Payment-Domain.md) → PurchaseOrderPayment → PurchaseOrder
3. **Delivery:** [Delivery-Domain](Delivery-Domain.md) → PurchaseOrder status updates
4. **Notifications:** PurchaseOrder events → Notification system

## Red Flags & Tech Debt

### Fat Controllers
1. **PDF Generation Duplication** - 150+ lines of Node.js/Chrome path detection duplicated across both Buyer and Vendor controllers
2. **No Service Layer** - All business logic in controllers (status transitions, calculations)
3. **Status Filtering Logic** - Complex conditional chains in `getPurchaseOrders()` and `index()` should be extracted

### Postgres Issues
1. **N+1 Query Risk** - `due_amount` accessor loads all `paymentInfos` without eager loading
2. **Raw SQL in Scopes** - `scopeStatusCounts*` methods use raw SQL that may not be Postgres-optimized
3. **No Database Indexes** - No evidence of indexes on frequently queried columns (status, buyer_id, vendor_id)
4. **Soft Deletes Without Cleanup** - `PurchaseOrderPayment` and `PurchaseOrderTransactionDetail` use soft deletes but no cleanup strategy

### Code Quality Issues
1. **Typo in Model** - `QutationService` (should be `QuotationService`)
2. **SQL Syntax Error** - Line 67 uses `||` instead of `OR` in CASE statement
3. **Status Mapping Bug** - Line 55 maps `cancelled_count` to `shipped` status
4. **Duplicate Count** - Line 56 duplicates `delivered_count` calculation
5. **Missing Transaction** - `confirmDelivery()` updates shipments without DB transaction

### Security Concerns
1. **Authorization Checks** - Manual authorization in controllers instead of middleware/policies
2. **No Input Sanitization** - Direct use of request input in queries

## Future Upgrades (Postgres & Scalability)

### Database Optimization
1. **Add Indexes:**
   ```sql
   CREATE INDEX idx_po_status ON purchase_orders(status);
   CREATE INDEX idx_po_buyer ON purchase_orders(buyer_id);
   CREATE INDEX idx_po_vendor ON purchase_orders(vendor_id);
   CREATE INDEX idx_po_payment_status ON purchase_orders(payment_status);
   CREATE INDEX idx_po_created_at ON purchase_orders(created_at DESC);
   ```

2. **Materialized Views for Counts:**
   ```sql
   CREATE MATERIALIZED VIEW po_status_counts AS
   SELECT buyer_id, vendor_id, status, COUNT(*) as count
   FROM purchase_orders GROUP BY buyer_id, vendor_id, status;
   ```

3. **Computed Columns for Due Amount:**
   ```sql
   ALTER TABLE purchase_orders
   ADD COLUMN due_amount DECIMAL(10,2)
   GENERATED ALWAYS AS (
     total_amount - COALESCE(
       (SELECT SUM(amount) FROM purchase_order_payment_infos
        WHERE purchase_order_id = purchase_orders.id AND is_verified = true),
       0
     )
   ) STORED;
   ```

### Architecture Improvements
1. **Extract PDF Service:**
   ```php
   class PurchaseOrderPdfService
   {
       public function generate(PurchaseOrder $order): StreamedResponse
       {
           // Centralized PDF generation logic
       }
   }
   ```

2. **Create PurchaseOrderService:**
   ```php
   class PurchaseOrderService
   {
       public function confirm(PurchaseOrder $order): void
       public function confirmDelivery(PurchaseOrder $order): void
       public function calculateDueAmount(PurchaseOrder $order): float
   }
   ```

3. **Implement Policies:**
   ```php
   class PurchaseOrderPolicy
   {
       public function view(User $user, PurchaseOrder $order): bool
       public function update(User $user, PurchaseOrder $order): bool
   }
   ```

### Scalability Considerations
1. **Event-Driven Architecture** - Dispatch events for PO status changes instead of direct updates
2. **Queue PDF Generation** - Move PDF generation to background jobs
3. **Caching Strategy** - Cache status counts with invalidation on status changes
4. **Read Replica** - Route read-heavy queries (list, show) to read replicas
