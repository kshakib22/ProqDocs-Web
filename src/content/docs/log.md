---
title: "Documentation Log"
---
# Documentation Log

## [2026-05-01] ingest | Payment Domain Documentation

**Action**: Created comprehensive documentation for the Payment domain.

**Files Created**:
- `docs/wiki/entities/Payment-Domain.md`

**Key Findings**:
- PaymentService is the most connected service (31 edges) with 1116 lines - needs refactoring
- Duplicate code in PaymentController for SSL callback handling
- Missing database indexes (commented out in migrations)
- Race condition in IPN payment creation
- Typo in field names: `receipent_*` should be `recipient_*`

**Next Domain**: ProductService (26 edges)

---

## [2026-05-01] ingest | Product Domain Documentation

**Action**: Created comprehensive documentation for the Product domain.

**Files Created**:
- `docs/wiki/entities/Product-Domain.md`

**Key Findings**:
- ProductService (1090 lines) and ElasticService (1012 lines) are fat service classes
- Duplicate code in ProductController for status management
- Missing database indexes on vendor_id, status, slug, sku
- Race condition in slug generation
- Typo in field names: `delevary_*` should be `delivery_*`
- Excel import has complex image extraction logic
- Chunked upload lacks session cleanup and timeout
- Elasticsearch search returns null on failure without fallback

**Next Domain**: Vendor (22 edges)

---

## [2026-05-01] ingest | Vendor Domain Documentation

**Action**: Created comprehensive documentation for the Vendor domain.

**Files Created**:
- `docs/wiki/entities/Vendor-Domain.md`

**Key Findings**:
- Hardcoded dashboard metrics instead of calculated values
- Commented out cache logic in dashboard controller
- N+1 queries in VendorResource and FavoriteVendorResource
- Profile completion scores calculated on every access without caching
- Missing database indexes on user_id, is_verified, is_rejected, city, state
- Duplicate document file handling code in resources
- Inconsistent status handling (calculated vs enum)
- No file validation on profile update
- Admin notification loop could be slow with many admins
- Empty destroy() method - no vendor deletion
- Typo in dashboard: `whereNUll` should be `whereNull`

**Next Domain**: BoqEntry (22 edges)

---

## [2026-05-02] ingest | BoqEntry / BoqSheet Domain Documentation

**Action**: Created comprehensive documentation for the BOQ domain.

**Files Created**:
- `docs/wiki/entities/BoqEntry-BoqSheet-Domain.md`

**Key Findings**:
- Fat controllers: BoqSheetController (503 lines) and BoqEntryController (527 lines)
- Duplicate buyer validation code in multiple methods
- Duplicate catch block in BoqSheetEntryService::deleteEntryFromBoqSheet()
- Typo in migration: `unsigendInteger` should be `unsignedInteger`
- Commented out store() method in BoqEntryController should be removed
- N+1 queries in BoqSheetController::index() with nested relationships
- Race condition in entry_order calculation without locking
- Missing database indexes on boq_sheet_id, entry_order, project_id, buyer_id
- No FK constraint on boq_sheet_merges (intentional but risky)
- Large JSON columns (dynamic_values, cell_colors, merged_cells) can grow large
- Excel export lacks pagination for large projects
- No role-based access control, only buyer ownership checks

**Next Domain**: PurchaseList (22 edges)

---

## [2026-05-02] ingest | RFQ-Quotation Domain Documentation

**Action**: Created comprehensive documentation for the RFQ/Quotation domain.

**Files Created**:
- `docs/wiki/entities/RFQ-Quotation-Domain.md`
- `docs/wiki/entities/Rfq-Model.md`
- `docs/wiki/entities/Quotation-Model.md`
- `docs/wiki/entities/QutationService-Model.md`
- `docs/wiki/entities/RfqService.md`
- `docs/wiki/entities/QuotationService.md`
- `docs/wiki/entities/RfqController.md`
- `docs/wiki/entities/QuotationController.md`
- `docs/wiki/entities/RfqResource.md`
- `docs/wiki/entities/QuotationResource.md`

**Key Findings**:
- **CRITICAL**: Typo in class name `QutationService` instead of `QuotationServiceItem` - breaking change waiting to happen
- Fat service classes: RfqService (654 lines), QuotationService (800 lines - largest in codebase)
- Fat controllers: RfqController (613 lines), QuotationController (577 lines)
- Manual field filtering in RfqService::updateRfq() (lines 228-271) - should use request validation
- Complex document upload handling with multiple formats (uploaded file, base64)
- Inconsistent authentication: Auth::user() vs JWTAuth::user() in QuotationController
- No database-level enforcement of one-quotation-per-vendor-per-RFQ rule
- No check constraints for positive amounts and deadline validation
- Storage existence checks in resource layer add I/O overhead
- Commented-out code for category sync and purchase list integration
- No rate limiting on RFQ creation or quotation submission
- No caching for public RFQ listings (high read volume)

**Next Domain**: PurchaseOrder (22 edges)

---

## [2026-05-02] ingest | PurchaseList Domain Documentation

**Action**: Created comprehensive documentation for the PurchaseList domain.

**Files Created**:
- `docs/wiki/entities/PurchaseList-Domain.md`

**Key Findings**:
- Inconsistent costing methods: both incremental and recalculation exist, but recalculation is preferred
- Duplicate status filter in getPurchaseLists() (lines 31-32 and 67-69)
- Broken sort logic in getPurchaseLists() - second condition only paginates
- Commented-out dead code: createOrServePurchaseOrderFromBoqEntry(), createPurchaseOrderFromBoqEntry(), updatePurchaseOrderFromPurchaseList()
- Complex vendor grouping query with subquery and multiple database calls
- No database constraints for positive amounts or status/ordered consistency
- Race condition in createOrServePurchaseOrder() - not atomic, could create duplicate orders
- N+1 queries in getPurchaseListsByVendors() - loads items in loop
- Missing indexes on buyer_id, project_id, status, is_ordered
- Image handling in resource checks storage for each image

**Next Domain**: Delivery (22 edges)

---

## [2026-05-02] ingest | PurchaseOrder Domain Documentation

**Action**: Created comprehensive documentation for the PurchaseOrder domain.

**Files Created**:
- `docs/wiki/entities/PurchaseOrder-Domain.md`

**Key Findings**:
- PDF generation code duplicated across both Buyer and Vendor controllers (150+ lines)
- No service layer - business logic embedded in controllers
- N+1 query risk in `due_amount` accessor
- SQL syntax errors in status count scopes (line 67 uses `||` instead of `OR`)
- Status mapping bugs: `cancelled_count` maps to `shipped` status (line 55)
- Duplicate `delivered_count` calculation (line 56)
- Missing database indexes on status, buyer_id, vendor_id, payment_status
- Soft deletes without cleanup strategy on payment models
- `confirmDelivery()` updates shipments without DB transaction
- Manual authorization checks instead of middleware/policies

**Next Domain**: Delivery (22 edges)

---

## [2026-05-02] ingest | Project Domain Documentation

**Action**: Created comprehensive documentation for the Project domain.

**Files Created**:
- `docs/wiki/entities/Project-Domain.md`

**Key Findings**:
- ProjectService is relatively clean at 183 lines
- ProjectController is thin at 93 lines - good separation of concerns
- Race condition in generateUniqueProjectCode() - do-while loop without locking
- Commented-out code in ProjectService (lines 52-54)
- Commented-out project_manager in both ProjectResource and ProjectResourceWithCompletion (line 31)
- N+1 query risk in listProjects() - withCount on rfqs with nested whereHas
- Missing database indexes on buyer_id, boq_status, project_manager_id, created_at
- Soft deletes without cleanup strategy for related records
- No check constraints for positive amounts or date validation
- No caching for project listings
- Manual authorization checks instead of using ProjectPolicy
- No rate limiting on project endpoints

**Next Domain**: Delivery (22 edges)

---

## [2026-05-03] ingest | Delivery Domain Documentation

**Action**: Created comprehensive documentation for the Delivery domain.

**Files Created**:
- `docs/wiki/entities/Delivery-Domain.md`

**Key Findings**:
- Typo in variable name: `$purchaseOrder->ser` should be `$purchaseOrder->services_charge` (line 37)
- Typo in field name: `installation_number` should be `installment_number` (line 308)
- Debug logger statements in production code (lines 55, 57, 87, 155)
- No database indexes on purchase_order_id, status in delivery-related tables
- No check constraints for positive amounts
- No transaction for shipment confirmation - updates multiple records without atomicity
- Duplicate data in resource: financial_summary duplicates existing fields
- Business logic in resource layer: shipment_item_value calculation should be in model
- No audit trail: no soft deletes or status change tracking
- No validation for partial shipments: no check that total quantities match purchase list requirements
- No validation that all purchase list items are covered by shipments
- No validation that total shipment charges are reasonable
- No validation that status transitions are valid
- No check for minimum shipment requirements
- No check for duplicate payment types
- No validation that total payment amounts match purchase order total
- No unique constraint on purchase_order_id (should be 1:1)
- No shipment_time column in migration (used in controller but not in schema)
- No human-readable status labels in resources
- No calculated fields like total_charge in ShipmentResource
- No pagination for shipments array in DeliveryDetailResource
- No caching for frequently accessed delivery details
- No rate limiting on endpoints
- Manual authorization checks instead of using DeliveryDetailPolicy
- calculateFinancialSummary() performs multiple database queries without transaction
- Incomplete feature: commented out rfq_id logic in createShipment()
- Inefficient null check for purchase_list_id in createShipment()
- Complex services array transformation in service layer
- Default eager loading in Shipment and ShipmentItem models may cause unnecessary queries

**Next Domain**: TBD

---

---

## [2026-05-03] ingest | BOQ and RFQ/Quotation Domains

**Action**: Performed bulk ingest and generation for BOQ and RFQ domains to fill grey links in index.md.

**Files Created**:
- `docs/wiki/entities/Boq Model.md`
- `docs/wiki/entities/BoqSheet Model.md`
- `docs/wiki/entities/BoqEntry Model.md`
- `docs/wiki/entities/BoqSheetMerge Model.md`
- `docs/wiki/entities/BoqSheetController.md`
- `docs/wiki/entities/BoqEntryController.md`
- `docs/wiki/entities/BoqSheetService.md`
- `docs/wiki/entities/BoqSheetEntryService.md`
- `docs/wiki/entities/BoqSheetMergeService.md`
- `docs/wiki/entities/BoqSheetResource.md`
- `docs/wiki/entities/BoqEntryResource.md`
- `docs/wiki/entities/BoqSheetMergeResource.md`
- `docs/wiki/entities/Rfq Model.md`
- `docs/wiki/entities/Quotation Model.md`
- `docs/wiki/entities/QutationService Model.md`
- `docs/wiki/entities/RfqService.md`
- `docs/wiki/entities/QuotationService.md`
- `docs/wiki/entities/RfqController.md`
- `docs/wiki/entities/QuotationController.md`
- `docs/wiki/entities/RfqResource.md`
- `docs/wiki/entities/QuotationResource.md`
- `docs/wiki/entities/QuotationsServiceResource.md`

**Key Findings**:
- **Critical Typo**: `QutationService` model name (missing 'o') throughout the RFQ domain.
- **Fragile dynamic schema**: BOQ `extra_columns` stored as comma-separated strings; renaming/deleting columns requires O(N) manual PHP loops.
- **Missing Transactions**: Critical multi-table updates in `BoqSheetService` and `BoqSheetMergeService` lack explicit `DB::beginTransaction`.
- **Race Conditions**: `entry_order` decrements and one-quote-per-vendor rules rely on PHP checks rather than DB locks or unique constraints.
- **Manual File Cleanup**: `RfqService` manually handles storage deletions, creating a risk of orphaned files or premature data loss.
- **Base64 Bloat**: Low-level decoding logic inside `QuotationService` adds unnecessary complexity to business logic.

**Next Domain**: PurchaseOrder (Validation)
