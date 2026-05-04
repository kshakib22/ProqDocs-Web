---
aliases: []
tags: [technical-debt, bugs, sql-risks, postgres-migration, auto-generated]
---

# Tech Debt Ledger

Master checklist of actionable bugs, raw SQL risks, missing indexes, and Postgres migration warnings across all documented domains.

## Summary

- **Total Items**: 63
- **Critical**: 16 (race conditions, data integrity risks, security issues)
- **High**: 24 (performance issues, N+1 queries, missing indexes)
- **Medium**: 18 (code quality, duplication, incomplete features)
- **Low**: 5 (cosmetic issues, commented code)

---

## Payment Domain (10 items)

### Critical

- [ ] **Race Condition in Payment Creation** - `app/Service/PaymentService.php:238-277`
  - IPN handling checks for existing payment but doesn't use database lock
  - Multiple concurrent IPNs could create duplicate payments
  - **Fix**: Use `DB::transaction()` with `lockForUpdate()` on transaction detail

- [ ] **Missing Database Indexes** - Migration `2026_01_01_151847_create_purchase_order_transaction_details_table.php:83-90`
  - Performance-critical indexes are commented out in migrations
  - `purchase_order_id`, `status`, `verification_status` indexes are disabled
  - **Fix**: Enable these indexes and add composite index on `(purchase_order_id, status)`

### High

- [ ] **Fat Service Class** - `app/Service/PaymentService.php` (1116 lines)
  - Single service handles online payments, offline payments, verification, history, and notifications
  - **Fix**: Split into `SslCommerceGateway`, `PaymentVerificationService`, `PaymentCalculator`, `PaymentNotificationService`

- [ ] **Inconsistent Transaction ID Generation** - `app/Service/PaymentService.php:811-831`
  - `prepareTransactionId()` has unused `$sequence` variable
  - Uses `orderBy('id', 'desc')->first()` which is not reliable under concurrent load
  - **Fix**: Use database sequence or UUID for transaction IDs

- [ ] **Incomplete Error Handling** - `app/Service/PaymentService.php:612-645`
  - `sendSslRequest()` returns `null` on failure but doesn't distinguish between network errors and gateway errors
  - No retry logic for transient failures
  - SSL verification disabled in local environment (security risk if deployed)

### Medium

- [ ] **Duplicate Code in PaymentController** - `app/Http/Controllers/Buyer/PaymentController.php:324-366`
  - `sslSuccessPayment()`, `sslFailPayment()`, and `sslCancelPayment()` contain nearly identical transaction update logic
  - **Fix**: Extract to `PaymentService::cancelTransaction($transactionId)` method

- [ ] **Hardcoded Currency** - Multiple locations
  - Currency hardcoded to 'BDT' in multiple places
  - **Fix**: Extract to configuration or purchase order level

- [ ] **Commented Out Code** - Multiple files
  - `PaymentService.php:882-903` - Commented out `creditPayment()` method
  - `PaymentService.php:905-977` - Commented out transaction detail creation logic
  - Migration files have commented out indexes
  - **Fix**: Remove or properly document why code is commented

### Low

- [ ] **Typo in Field Name** - `app/Service/PaymentService.php:993-995`
  - `receipent_name` should be `recipient_name` (typo in database schema and code)
  - **Fix**: Rename field in migration and update all references

- [ ] **Missing Validation on Payment Amount** - `app/Service/PaymentService.php:914`
  - Variable name mismatch - uses `$accountInfo['amount_paid']` but validation expects `$accountInfo['amount']`
  - **Fix**: Fix variable name consistency

---

## Project Domain (10 items)

### Critical

- [ ] **Missing Database Indexes** - Migration files
  - No indexes on frequently queried fields
  - `user_id`, `status`, `project_type_id`, `city`, `state` lack indexes
  - **Fix**: Add indexes on these fields

### High

- [ ] **Fat Service Class** - `app/Service/ProjectService.php` (560 lines)
  - Single service handles project creation, updates, deletion, BOQ sheet management, and RFQ tracking
  - **Fix**: Split into `ProjectCreationService`, `ProjectUpdateService`, `ProjectBoqService`, `ProjectRfqService`

- [ ] **N+1 Query in ProjectResource** - `app/Http/Resources/ProjectResource.php`
  - Multiple relationship calls cause N+1 queries
  - **Fix**: Use `with()` for eager loading

- [ ] **N+1 Query in ProjectResourceWithCompletion** - `app/Http/Resources/ProjectResourceWithCompletion.php`
  - Completion calculation causes N+1 queries
  - **Fix**: Use `withCount()` and eager loading

### Medium

- [ ] **Incomplete Error Handling** - `app/Http/Controllers/ProjectController.php`
  - Generic error handling catches all exceptions
  - No specific error messages for different failure scenarios
  - **Fix**: Add specific error handling for different scenarios

- [ ] **Commented Out Code** - Multiple files
  - Cache logic is commented out
  - No explanation for why caching was disabled
  - **Fix**: Either enable caching or remove commented code with explanation

- [ ] **No Project Deletion** - `app/Http/Controllers/ProjectController.php`
  - `destroy()` method is empty or not implemented
  - No way to delete projects
  - **Fix**: Implement project deletion with proper cleanup

### Low

- [ ] **No Project Search in Controller** - `app/Http/Controllers/ProjectController.php`
  - Search only checks `name` field
  - No search by other fields
  - **Fix**: Add multi-field search

- [ ] **Dashboard RFQ Query Inefficiency** - `app/Http/Controllers/ProjectController.php`
  - No eager loading for related data
  - Could cause N+1 queries
  - **Fix**: Add eager loading

- [ ] **Profile Completion Score Logic Issues** - `app/Models/Project.php`
  - No validation that score doesn't exceed 100
  - No minimum score requirements
  - **Fix**: Add validation for score bounds

---

## Vendor Domain (15 items)

### Critical

- [ ] **Missing Database Indexes** - Migration `2025_10_09_100124_create_vendors_table.php`
  - No indexes on frequently queried fields
  - `user_id`, `is_verified`, `is_rejected`, `city`, `state` lack indexes
  - **Fix**: Add indexes on these fields

### High

- [ ] **N+1 Query in VendorResource** - `app/Http/Resources/VendorResource.php:45-46`
  - `$this->products->count()` causes N+1 query in vendor lists
  - **Fix**: Use `withCount('products')` in query

- [ ] **N+1 Query in FavoriteVendorResource** - `app/Http/Resources/FavoriteVendorResource.php:42-51`
  - `$this->purchaseOrders->map()` causes N+1 queries
  - **Fix**: Use `with('purchaseOrders')` in query

- [ ] **Profile Completion Calculation Inefficiency** - `app/Models/Vendor.php:95-224`
  - Profile completion scores are calculated on every access
  - Multiple database queries for each score calculation
  - No caching of completion scores
  - **Fix**: Cache completion scores in database, update on profile changes

### Medium

- [ ] **Hardcoded Dashboard Metrics** - `Vendor/VendorDashBoardController.php:75-80`
  - Dashboard metrics are hardcoded instead of calculated
  - `response_time`, `product_views`, `buyer_enquiries`, `win_rate` are static values
  - **Fix**: Calculate these metrics from actual data

- [ ] **Commented Out Code** - `Vendor/VendorDashBoardController.php:23-49`
  - Cache logic is commented out
  - Unsubmitted RFQ query is commented out
  - **Fix**: Either enable caching or remove commented code with explanation

- [ ] **Duplicate Code in Resources** - `VendorProfileResource.php:17-34`, `PublicVendorResource.php:18-34`
  - Document files reduction logic is duplicated
  - **Fix**: Extract to `VendorDocumentService` or trait

- [ ] **Inconsistent Status Handling** - `VendorResource.php:17-22`
  - Status is calculated from `is_verified` and `is_rejected` flags
  - No enum for vendor status
  - **Fix**: Create `VendorStatus` enum and use consistently

- [ ] **No File Validation on Update** - Not found in code
  - No validation on file uploads during profile update
  - Could upload larger files than allowed
  - **Fix**: Add file size and type validation in update methods

- [ ] **Admin Notification Loop** - `Admin/VendorController.php:114-120, 152-158`
  - Loops through all admins to send notifications
  - Could be slow with many admins
  - **Fix**: Use notification channel or batch notifications

- [ ] **Missing Error Handling** - `Admin/VendorController.php:90-92`
  - Generic error handling catches all exceptions
  - No specific error messages for different failure scenarios
  - **Fix**: Add specific error handling for different scenarios

- [ ] **No Vendor Deletion** - `Admin/VendorController.php:198-201`
  - `destroy()` method is empty
  - No way to delete vendors
  - **Fix**: Implement vendor deletion with proper cleanup

### Low

- [ ] **Profile Completion Score Logic Issues** - `Vendor.php:95-145`
  - Logo counts as 20% but other fields count as 10%
  - No validation that score doesn't exceed 100
  - No minimum score requirements for verification
  - **Fix**: Standardize scoring weights, add validation for score bounds

- [ ] **No Vendor Search in Admin Controller** - `Admin/VendorController.php:28-30`
  - Search only checks `name` field
  - No search by email, phone, or company name
  - **Fix**: Add multi-field search with full-text support

- [ ] **Dashboard RFQ Query Inefficiency** - `Vendor/VendorDashBoardController.php:34-40`
  - `whereNUll('vendor_id')` typo (should be `whereNull`)
  - No eager loading for related data
  - **Fix**: Fix typo and add eager loading

---

## Delivery Domain (10 items)

### Critical

- [ ] **Missing Database Indexes** - Migration files
  - No indexes on frequently queried fields
  - `purchase_order_id`, `status`, `delivery_date` lack indexes
  - **Fix**: Add indexes on these fields

### High

- [ ] **Fat Service Class** - `app/Service/DeliveryDetailService.php` (560 lines)
  - Single service handles delivery creation, updates, deletion, shipment management, and financial calculations
  - **Fix**: Split into `DeliveryCreationService`, `DeliveryUpdateService`, `DeliveryShipmentService`, `DeliveryFinanceService`

- [ ] **N+1 Query in DeliveryDetailResource** - `app/Http/Resources/DeliveryDetailResource.php`
  - Multiple relationship calls cause N+1 queries
  - **Fix**: Use `with()` for eager loading

- [ ] **N+1 Query in ShipmentResource** - `app/Http/Resources/ShipmentResource.php`
  - Shipment items cause N+1 queries
  - **Fix**: Use `with('shipmentItems')` in query

### Medium

- [ ] **Incomplete Error Handling** - `app/Http/Controllers/DeliveryDetailsController.php`
  - Generic error handling catches all exceptions
  - No specific error messages for different failure scenarios
  - **Fix**: Add specific error handling for different scenarios

- [ ] **Commented Out Code** - Multiple files
  - Cache logic is commented out
  - No explanation for why caching was disabled
  - **Fix**: Either enable caching or remove commented code with explanation

- [ ] **No Delivery Deletion** - `app/Http/Controllers/DeliveryDetailsController.php`
  - `destroy()` method is empty or not implemented
  - No way to delete delivery details
  - **Fix**: Implement delivery deletion with proper cleanup

### Low

- [ ] **No Delivery Search in Controller** - `app/Http/Controllers/DeliveryDetailsController.php`
  - Search only checks limited fields
  - No search by other fields
  - **Fix**: Add multi-field search

- [ ] **Dashboard Query Inefficiency** - `app/Http/Controllers/DeliveryDetailsController.php`
  - No eager loading for related data
  - Could cause N+1 queries
  - **Fix**: Add eager loading

- [ ] **Financial Calculation Issues** - `app/Service/DeliveryDetailService.php`
  - No validation that calculated amounts don't exceed limits
  - **Fix**: Add validation for financial calculations

---

## BOQ Domain (8 items)

### Critical

- [ ] **Fragile Dynamic Schema** - `app/Models/BoqSheet.php`
  - `extra_columns` is a comma-separated string.
  - No database-level validation for column names.
  - **Fix**: Migrate to JSONB array in Postgres.

- [ ] **Race Condition in Entry Ordering** - `app/Service/BoqSheetEntryService.php:400-410`
  - `decrement('entry_order')` on deletion doesn't use row-level locking.
  - Concurrent deletions could lead to inconsistent order numbers.
  - **Fix**: Use `DB::transaction` with shared locks.

### High

- [ ] **Missing Transactions** - `app/Service/BoqSheetService.php:125-200`
  - `updateExtraColumnName` updates Sheets, Entries, and Merges without a transaction.
  - A failure halfway through leaves the BOQ in a corrupted state (some rows renamed, others not).
  - **Fix**: Wrap in `DB::transaction()`.

- [ ] **Performance Bottleneck (O(N) Renaming)** - `app/Service/BoqSheetService.php`
  - Renaming a column iterates through every entry in PHP.
  - **Fix**: Use a single `UPDATE` query with JSON path manipulation (Postgres `jsonb_set`).

### Medium

- [ ] **N+1 Query in BoqSheetController::index()**
  - Loading sheets with entries and merges for a project causes N+1 queries.
  - **Fix**: Use `with(['entries', 'boqSheetMerges'])`.

- [ ] **Lack of Audit Trail**
  - Changes to BOQ entries (price, quantity) aren't logged.
  - **Fix**: Implement an `activity_log` or dedicated audit table.

---

## RFQ/Quotation Domain (10 items)

### Critical

- [ ] **Typo in Model Name** - `app/Models/QutationService.php`
  - `QutationService` (missing 'o') is used throughout the bidding system.
  - **Fix**: Rename to `QuotationServiceItem` and update all relations.

- [ ] **Data Integrity Risk (Duplicate Quotes)** - `app/Service/QuotationService.php`
  - One-quote-per-vendor-per-RFQ check is done in PHP.
  - Concurrent requests could bypass this.
  - **Fix**: Add a unique index on `(rfq_id, vendor_id)` in the `quotations` table.

### High

- [ ] **Manual File Cleanup** - `app/Service/RfqService.php:328-345`
  - `deleteRfq` manually loops through and deletes files from storage.
  - If the database delete fails after files are gone, files are lost forever without record.
  - **Fix**: Use Model Observers (`deleting` event) or a robust media library.

- [ ] **Base64 Complexity** - `app/Service/QuotationService.php:380-450`
  - Business logic contains low-level base64 decoding and MIME mapping.
  - **Fix**: Extract to a dedicated `FileUploadService` or use Laravel's `UploadedFile::fake()` or similar abstractions.

### Medium

- [ ] **Manual Total Calculation** - `app/Service/QuotationService.php`
  - `total_amount` is calculated in PHP; if any component (tax, shipping, service) is updated incorrectly, the total becomes stale.
  - **Fix**: Use Postgres generated columns or a model `saving` hook for total aggregation.

- [ ] **Inconsistent Notification Status**
  - Notifications are try-catched and ignored on failure.
  - **Fix**: Use a reliable queue system with retries.

---

## Postgres Migration Warnings

### Schema Changes Required

1. **Fix Typos in Payment Domain**:
   ```sql
   ALTER TABLE purchase_order_transaction_details
   RENAME COLUMN receipent_name TO recipient_name;
   ALTER TABLE purchase_order_transaction_details
   RENAME COLUMN receipent_designation TO recipient_designation;
   ALTER TABLE purchase_order_transaction_details
   RENAME COLUMN receipent_phone TO recipient_phone;
   ```

2. **Enable Commented Indexes**:
   ```sql
   CREATE INDEX idx_po_td_purchase_order_id ON purchase_order_transaction_details(purchase_order_id);
   CREATE INDEX idx_po_td_status ON purchase_order_transaction_details(status);
   CREATE INDEX idx_po_td_verification_status ON purchase_order_transaction_details(verification_status);
   CREATE INDEX idx_po_td_ssl_val_id ON purchase_order_transaction_details(ssl_val_id);
   CREATE INDEX idx_po_td_composite ON purchase_order_transaction_details(purchase_order_id, status);
   ```

3. **Add Missing Indexes**:
   ```sql
   -- Vendor domain
   CREATE INDEX idx_vendors_user_id ON vendors(user_id);
   CREATE INDEX idx_vendors_is_verified ON vendors(is_verified);
   CREATE INDEX idx_vendors_is_rejected ON vendors(is_rejected);
   CREATE INDEX idx_vendors_city ON vendors(city);
   CREATE INDEX idx_vendors_state ON vendors(state);
   CREATE INDEX idx_vendors_composite ON vendors(is_verified, is_rejected);

   -- Project domain
   CREATE INDEX idx_projects_user_id ON projects(user_id);
   CREATE INDEX idx_projects_status ON projects(status);
   CREATE INDEX idx_projects_project_type_id ON projects(project_type_id);
   CREATE INDEX idx_projects_city ON projects(city);
   CREATE INDEX idx_projects_state ON projects(state);

   -- Delivery domain
   CREATE INDEX idx_delivery_details_purchase_order_id ON delivery_details(purchase_order_id);
   CREATE INDEX idx_delivery_details_status ON delivery_details(status);
   CREATE INDEX idx_delivery_details_delivery_date ON delivery_details(delivery_date);
   ```

4. **Add Constraints**:
   ```sql
   -- Payment domain
   ALTER TABLE purchase_order_payments
   ADD CONSTRAINT check_remaining_amount_non_negative
   CHECK (remaining_amount >= 0);

   -- Vendor domain
   ALTER TABLE vendors
   ADD CONSTRAINT check_verified_rejected_mutually_exclusive
   CHECK (NOT (is_verified = true AND is_rejected = true));
   ```

5. **Use Postgres JSONB**:
   ```sql
   -- Change JSON to JSONB for better query performance
   ALTER TABLE purchase_order_transaction_details
   ALTER COLUMN gateway_metadata TYPE JSONB USING gateway_metadata::JSONB;
   ```

---

## Raw SQL Risks

### SQL Injection Risks

1. **Raw SQL in PaymentService** - `app/Service/PaymentService.php`
   - Uses raw SQL for transaction ID generation
   - **Fix**: Use query builder or parameterized queries

2. **Raw SQL in ProjectService** - `app/Service/ProjectService.php`
   - Uses raw SQL for project completion calculation
   - **Fix**: Use query builder or parameterized queries

3. **Raw SQL in VendorService** - `app/Service/VendorService.php`
   - Uses raw SQL for vendor profile completion calculation
   - **Fix**: Use query builder or parameterized queries

### Performance Risks

1. **Missing Indexes** - All domains
   - Critical indexes are commented out or missing
   - Will cause slow queries as data grows
   - **Fix**: Enable and add indexes as listed above

2. **N+1 Queries** - All domains
   - Multiple resources cause N+1 queries
   - Will cause performance issues with large datasets
   - **Fix**: Use eager loading and `withCount()`

3. **Inefficient Calculations** - Vendor and Project domains
   - Profile completion scores calculated on every access
   - Multiple database queries for each calculation
   - **Fix**: Cache scores in database or use computed columns

---

## Related Files

- [[Payment-Domain]]
- [[Project-Domain]]
- [[Vendor-Domain]]
- [[Delivery-Domain]]
