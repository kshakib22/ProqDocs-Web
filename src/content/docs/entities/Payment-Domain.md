---
aliases: []
tags: [laravel, backend, auto-generated]
title: "Payment Domain"
---
# Payment Domain

## Overview

The Payment domain is the most interconnected domain in the application (31 edges in the knowledge graph), handling all payment processing for [PurchaseOrder](PurchaseOrder.md) transactions. It integrates with SSL Commerce payment gateway for online payments and supports offline payment methods including bank transfers, cash, cheques, BEFTN, RTGS, and NPSB.

## Current Architecture & Flow

### Core Components

#### Models

- **[PurchaseOrderPayment](PurchaseOrderPayment.md)** - Represents successful payments. Only created when a transaction is verified and completed.
- **[PurchaseOrderTransactionDetail](PurchaseOrderTransactionDetail.md)** - Tracks all payment attempts (pending, success, failed, cancelled). Contains gateway metadata and verification status.
- **[PurchaseOrderPaymentInfo](PurchaseOrderPaymentInfo.md)** - Stores scheduled payment information (installments, due dates, amounts).
- **[PaymentType](PaymentType.md)** - Defines payment types: `100_percent_advance`, `100_percent_credit`, `installment`.
- **[PaymentMethod](PaymentMethod.md)** - Available payment methods (ssl_commerce, bank_transfer, cash, cheque, BEFTN, RTGS, NPSB).

#### Services

- **[PaymentService](PaymentService.md)** - Core payment processing service (1116 lines). Handles:
  - Online payment initiation with SSL Commerce
  - Transaction verification via SSL Commerce API
  - IPN (Instant Payment Notification) webhook handling
  - Offline payment creation
  - Payment history and summaries
  - Notification dispatch

- **[SubscriptionPaymentService](SubscriptionPaymentService.md)** - Handles subscription payments (separate from purchase order payments).

#### Controllers

- **[Buyer/PaymentController](Buyer/PaymentController.md)** - Buyer-facing payment endpoints (367 lines):
  - `initiate()` - Start SSL Commerce payment
  - `createOnlinePayment()` - Create online payment from payment info
  - `createOfflinePayment()` - Create offline payment with bank/cash details
  - `successPayment()` - Handle SSL Commerce success callback
  - `verifyTransaction()` - Manual transaction verification
  - `ipn()` - Handle IPN webhook
  - `history()` - Get payment history

- **[Vendor/PaymentController](Vendor/PaymentController.md)** - Vendor-facing payment endpoints.
- **[Vendor/SubscriptionPaymentController](Vendor/SubscriptionPaymentController.md)** - Vendor subscription payment handling.

#### Resources

- **[TransactionSuccessPaymentResource](TransactionSuccessPaymentResource.md)** - Response for successful payment verification.
- **[PurchaseOrderPaymentResource](PurchaseOrderPaymentResource.md)** - Payment details response.
- **[PaymentInfoResource](PaymentInfoResource.md)** - Payment info/schedule response.

#### Notifications

- **[PurchaseOrderPaymentBuyerNotification](PurchaseOrderPaymentBuyerNotification.md)** - Database notification sent to buyer on payment.
- **[PurchaseOrderPaymentVendorNotification](PurchaseOrderPaymentVendorNotification.md)** - Database notification sent to vendor on payment.

### Payment Flow

#### Online Payment (SSL Commerce)

1. **Initiation**: `PaymentService::initiatePayment()`
   - Validates purchase order ownership and payment amount
   - Creates `PurchaseOrderTransactionDetail` with status `pending`
   - Generates SSL Commerce hash and POST data
   - Sends request to SSL Commerce API
   - Returns gateway URL for redirect

2. **User Payment**: User completes payment on SSL Commerce page

3. **Success Callback**: `PaymentService::successPayment()`
   - Receives `val_id` and `tran_id` from SSL Commerce
   - Verifies transaction via SSL Commerce validation API
   - Updates transaction detail to `success` and `verified`
   - Creates `PurchaseOrderPayment` record
   - Updates `PurchaseOrderPaymentInfo.is_paid`
   - Updates `PurchaseOrder.payment_status`
   - Sends notifications to buyer and vendor

4. **IPN Webhook**: `PaymentService::handleIpn()`
   - Receives asynchronous notification from SSL Commerce
   - Implements idempotency via `verification_hash`
   - Verifies transaction
   - Creates payment record if not already created

#### Offline Payment

1. **Creation**: `PaymentService::createPaymentForOffline()`
   - Validates payment amount against remaining balance
   - Creates `PurchaseOrderTransactionDetail` with status `success`
   - Stores bank account info or cash recipient details
   - Uploads payment slip attachment
   - Creates `PurchaseOrderPayment` with `is_verified = false`
   - Updates purchase order payment status

### Transaction ID Generation

Format: `P0-{buyer_id}-{purchase_order_id}-{installment}-{sequence}`

Example: `P0-123-456-1-0001`

### Payment Number Generation

Format: `PAY-{timestamp}-{purchase_order_id}-{buyer_id}-{sequence}`

Example: `PAY-20260501-456-123-001`

## Dependencies & Graph Links

### Direct Dependencies

- **[PurchaseOrder](PurchaseOrder.md)** - Payments are always associated with a purchase order
- **[Buyer](Buyer.md)** - Payments are made by buyers
- **[Vendor](Vendor.md)** - Vendors receive payment notifications
- **[PaymentType](PaymentType.md)** - Defines payment structure (advance, credit, installment)
- **[PurchaseOrderPaymentInfo](PurchaseOrderPaymentInfo.md)** - Scheduled payment information

### Cross-Domain Connections

- **[Notification](Notification.md)** - Payment notifications sent via database notifications
- **[Subscription](Subscription.md)** - Separate subscription payment flow via `SubscriptionPaymentService`

## Red Flags & Tech Debt

### 1. Fat Service Class (PaymentService: 1116 lines)

**Location**: `app/Service/PaymentService.php`

**Issues**:
- Single service handles online payments, offline payments, verification, history, and notifications
- Multiple responsibilities: gateway integration, business logic, data persistence, notification dispatch
- Difficult to test individual concerns in isolation
- High cyclomatic complexity

**Recommendation**: Split into:
- `SslCommerceGateway` - Gateway API integration
- `PaymentVerificationService` - Transaction verification logic
- `PaymentCalculator` - Payment summary and remaining amount calculations
- `PaymentNotificationService` - Notification dispatch

### 2. Duplicate Code in PaymentController

**Location**: `app/Http/Controllers/Buyer/PaymentController.php:324-366`

**Issues**:
- `sslSuccessPayment()`, `sslFailPayment()`, and `sslCancelPayment()` contain nearly identical transaction update logic
- Lines 332-343, 351-362, 349-363 are duplicates

```php
// Repeated 3 times with minor variations
$transactionDetail = \App\Models\PurchaseOrderTransactionDetail::where('transaction_id', $tran_id)->first();
if ($transactionDetail) {
    $transactionDetail->update([
        'status' => 'cancelled',
        'verification_status' => 'cancelled',
        'error_code' => 'cancelled',
        'error_message' => 'Payment cancelled',
        'gateway_response' => json_encode($request->all()),
    ]);
}
```

**Recommendation**: Extract to `PaymentService::cancelTransaction($transactionId)` method.

### 3. Inconsistent Transaction ID Generation

**Location**: `app/Service/PaymentService.php:811-831`

**Issues**:
- `prepareTransactionId()` has unused `$sequence` variable
- Logic for installment counting is convoluted
- Uses `orderBy('id', 'desc')->first()` which is not reliable under concurrent load

**Recommendation**: Use database sequence or UUID for transaction IDs.

### 4. Missing Database Indexes

**Location**: Migration files (commented out indexes)

**Issues**:
- Performance-critical indexes are commented out in migrations
- `purchase_order_id`, `status`, `verification_status` indexes are disabled
- Will cause slow queries as data grows

**Migration**: `2026_01_01_151847_create_purchase_order_transaction_details_table.php:83-90`

```php
// $table->index('purchase_order_id');
// $table->index('status');
// $table->index('verification_status');
// $table->index('ssl_val_id');
```

**Recommendation**: Enable these indexes and add composite index on `(purchase_order_id, status)`.

### 5. Race Condition in Payment Creation

**Location**: `app/Service/PaymentService.php:238-277`

**Issues**:
- IPN handling checks for existing payment but doesn't use database lock
- Multiple concurrent IPNs could create duplicate payments
- Idempotency check uses `verification_hash` but payment creation is not atomic

**Recommendation**: Use `DB::transaction()` with `lockForUpdate()` on transaction detail.

### 6. Hardcoded Currency

**Location**: Multiple locations

**Issues**:
- Currency hardcoded to 'BDT' in multiple places
- Not configurable for multi-currency support

**Recommendation**: Extract to configuration or purchase order level.

### 7. Incomplete Error Handling

**Location**: `app/Service/PaymentService.php:612-645`

**Issues**:
- `sendSslRequest()` returns `null` on failure but doesn't distinguish between network errors and gateway errors
- No retry logic for transient failures
- SSL verification disabled in local environment (security risk if deployed)

### 8. Commented Out Code

**Location**: Multiple files

**Issues**:
- `PaymentService.php:882-903` - Commented out `creditPayment()` method
- `PaymentService.php:905-977` - Commented out transaction detail creation logic
- Migration files have commented out indexes

**Recommendation**: Remove or properly document why code is commented.

### 9. Typo in Field Name

**Location**: `app/Service/PaymentService.php:993-995`

**Issue**: `receipent_name` should be `recipient_name` (typo in database schema and code).

### 10. Missing Validation on Payment Amount

**Location**: `app/Service/PaymentService.php:914`

**Issue**: Variable name mismatch - uses `$accountInfo['amount_paid']` but validation expects `$accountInfo['amount']`.

## Future Upgrades (Postgres & Scalability)

### Database Schema Improvements

1. **Enable Indexes**:
   ```sql
   CREATE INDEX idx_po_td_purchase_order_id ON purchase_order_transaction_details(purchase_order_id);
   CREATE INDEX idx_po_td_status ON purchase_order_transaction_details(status);
   CREATE INDEX idx_po_td_verification_status ON purchase_order_transaction_details(verification_status);
   CREATE INDEX idx_po_td_ssl_val_id ON purchase_order_transaction_details(ssl_val_id);
   CREATE INDEX idx_po_td_composite ON purchase_order_transaction_details(purchase_order_id, status);
   ```

2. **Fix Typos**:
   - Rename `receipent_name` → `recipient_name`
   - Rename `receipent_designation` → `recipient_designation`
   - Rename `receipent_phone` → `recipient_phone`

3. **Add Constraints**:
   ```sql
   ALTER TABLE purchase_order_payments
   ADD CONSTRAINT check_remaining_amount_non_negative
   CHECK (remaining_amount >= 0);
   ```

4. **Use Postgres JSONB**:
   - Change `gateway_metadata` from JSON to JSONB for better query performance

### Architecture Improvements

1. **Event-Driven Architecture**:
   - Dispatch events on payment completion instead of direct notification calls
   - Allow multiple listeners (email, SMS, webhook, analytics)

2. **Payment Gateway Abstraction**:
   - Create `PaymentGatewayInterface` for multiple gateway support
   - Implement factory pattern for gateway selection

3. **Idempotency via Database**:
   - Use unique constraint on `(transaction_id, verification_hash)` instead of application-level checks

4. **Queue IPN Processing**:
   - Move IPN handling to background queue
   - Prevent webhook timeout issues

5. **Payment Status Machine**:
   - Implement state machine pattern for payment status transitions
   - Prevent invalid state changes

### Performance Optimizations

1. **Caching**:
   - Cache payment summaries for purchase orders
   - Cache payment type configurations

2. **Batch Processing**:
   - Batch payment status updates
   - Batch notification dispatch

3. **Read Replicas**:
   - Route payment history queries to read replicas

### Security Improvements

1. **Webhook Signature Verification**:
   - Verify SSL Commerce webhook signatures
   - Prevent fraudulent webhook calls

2. **Rate Limiting**:
   - Rate limit payment initiation endpoints
   - Prevent abuse

3. **Audit Logging**:
   - Log all payment state changes
   - Track who initiated/verified payments

## Related Files

### Models
- `app/Models/PurchaseOrderPayment.php`
- `app/Models/PurchaseOrderTransactionDetail.php`
- `app/Models/PurchaseOrderPaymentInfo.php`
- `app/Models/PaymentType.php`
- `app/Models/PaymentMethod.php`

### Services
- `app/Service/PaymentService.php`
- `app/Service/SubscriptionPaymentService.php`

### Controllers
- `app/Http/Controllers/Buyer/PaymentController.php`
- `app/Http/Controllers/Vendor/PaymentController.php`
- `app/Http/Controllers/Vendor/SubscriptionPaymentController.php`

### Resources
- `app/Http/Resources/TransactionSuccessPaymentResource.php`
- `app/Http/Resources/PurchaseOrderPaymentResource.php`
- `app/Http/Resources/PaymentInfoResource.php`

### Notifications
- `app/Notifications/PurchaseOrderPaymentBuyerNotification.php`
- `app/Notifications/PurchaseOrderPaymentVendorNotification.php`

### Migrations
- `database/migrations/2026_01_01_151840_create_purchase_order_payments_table.php`
- `database/migrations/2026_01_01_151847_create_purchase_order_transaction_details_table.php`
- `database/migrations/2026_02_09_123828_create_purchase_order_payment_infos_table.php`
- `database/migrations/2026_02_09_140001_create_payment_methods_table.php`
- `database/migrations/2026_02_08_125856_create_payment_types_table.php`
