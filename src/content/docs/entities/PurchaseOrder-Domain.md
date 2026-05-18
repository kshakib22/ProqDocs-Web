---
aliases: []
tags: [laravel, backend, auto-generated]
title: "PurchaseOrder Domain"
---
# PurchaseOrder Domain

## Overview

The PurchaseOrder Domain manages the procurement lifecycle from order creation through delivery confirmation. It serves as the central entity connecting [Buyer-Domain](/entities/buyer-domain), [Vendor-Domain](/entities/vendor-domain), [Product-Domain](/entities/product-domain), [RFQ-Quotation-Domain](/entities/rfq-quotation-domain), and [PurchaseList-Domain](/entities/purchaselist-domain).

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
- `belongsTo` [Project](/entities/project-model), [Vendor](/entities/vendor-model), [Buyer](/entities/buyer-model)
- `hasMany` [PurchaseList](/entities/purchaselist-model), [PurchaseOrderPayment](/entities/purchaseorderpayment-model), [PurchaseOrderTransactionDetail](/entities/purchaseordertransactiondetail-model), [PurchaseOrderPaymentInfo](/entities/purchaseorderpaymentinfo-model)
- `hasOne` DeliveryDetail
- `hasManyThrough` [Shipment](/entities/shipment-model)

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
- `belongsTo` [PurchaseOrder](/entities/purchaseorder-model), [PaymentType](/entities/paymenttype-model), [Buyer](/entities/buyer-model)
- `belongsTo` [PurchaseOrderTransactionDetail](/entities/purchaseordertransactiondetail-model) (one-to-one)

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
- `hasOne` [PurchaseOrderPayment](/entities/purchaseorderpayment-model)
- `belongsTo` [PurchaseOrder](/entities/purchaseorder-model), [PaymentType](/entities/paymenttype-model), [Buyer](/entities/buyer-model)

**Helper Methods:**
- `isSuccess()` - Checks status + verification
- `isPending()`, `isFailed()` - Status checks

**Query Scopes:**
- `scopeSuccess()`, `scopePending()`, `scopeVerified()`, `scopeForPurchaseOrder()`

#### PurchaseOrderPaymentInfo Model
**File:** `app/Models/PurchaseOrderPaymentInfo.php`

Stores verified payment information for due amount calculations.

**Relationships:**
- `belongsTo` [PurchaseOrder](/entities/purchaseorder-model)

...

## Dependencies & Graph Links

### Domain Dependencies
- Buyer-Domain - PO owner
- Vendor-Domain - PO recipient
- [Project-Domain](/entities/project-domain) - Associated project
- [Product-Domain](/entities/product-domain) - Items being purchased
- [RFQ-Quotation-Domain](/entities/rfq-quotation-domain) - Source of pricing
- [PurchaseList-Domain](/entities/purchaselist-domain) - Line items
- [Payment-Domain](/entities/payment-domain) - Payment processing
- [Delivery-Domain](/entities/delivery-domain) - Shipment tracking

...
- `confirmDelivery()` updates shipments without DB transaction

...