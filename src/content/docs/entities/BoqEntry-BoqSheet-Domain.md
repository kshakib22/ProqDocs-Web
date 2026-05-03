---
aliases: []
tags: [laravel, backend, auto-generated]
title: "BoqEntry / BoqSheet Domain"
---
# BoqEntry / BoqSheet Domain

## Current Architecture & Flow

### Overview
The BOQ (Bill of Quantities) domain manages project cost estimation sheets with dynamic columns, Excel-style cell merging, and integration with quotations and purchase orders. It enables buyers to create structured cost breakdowns for construction projects.

### Core Models

#### [BoqSheet Model](BoqSheet Model.md)
- **Purpose:** Represents a single BOQ sheet within a project
- **Table:** `boq_sheets`
- **Key Fields:**
  - `sheet_name` (string) - Display name of the sheet
  - `sheet_order` (integer) - Ordering position within project
  - `extra_columns` (string) - Comma-separated dynamic column names
  - `cell_colors` (json) - Sheet-level cell color configurations
- **Relationships:**
  - `project()` - BelongsTo [Project Model](Project Model.md)
  - `entries()` - HasMany [BoqEntry Model](BoqEntry Model.md)
  - `boqSheetMerges()` - HasMany [BoqSheetMerge Model](BoqSheetMerge Model.md)
- **Behavior:**
  - Auto-deletes associated merges on deletion (booted hook)
  - Provides array accessor/mutator for `extra_columns`

#### [BoqEntry Model](BoqEntry Model.md)
- **Purpose:** Individual line items within a BOQ sheet
- **Table:** `boq_entries`
- **Key Fields:**
  - `entry_order` (integer) - Position within sheet
  - `rfq_code` (string) - Reference to RFQ
  - `item_name` (string) - Display name
  - `image` (string) - Product image path
  - `unit` (string) - Unit of measurement
  - `unit_price` (decimal) - Price per unit
  - `quantity` (decimal) - Quantity ordered
  - `amount` (decimal) - Calculated: quantity × unit_price
  - `vat_tax` (decimal) - Tax amount
  - `total` (decimal) - Calculated: amount + vat_tax
  - `tax_amount` (decimal) - Additional tax
  - `shipping_amount` (decimal) - Shipping cost
  - `loading_charge` (decimal) - Loading fee
  - `services_charge` (decimal) - Service fees
  - `total_amount` (decimal) - Final total
  - `discount_amount` (decimal) - Discount applied
  - `dynamic_values` (json) - Values for extra columns
  - `cell_colors` (json) - Cell-level color highlighting
  - `merged_cells` (json) - Merged cell configurations
- **Relationships:**
  - `boqSheet()` - BelongsTo [BoqSheet Model](BoqSheet Model.md)
  - `product()` - BelongsTo [Product Model](Product Model.md)
  - `quotation()` - BelongsTo [Quotation Model](Quotation Model.md)
  - `rfq()` - BelongsTo [Rfq Model](Rfq Model.md)
  - `vendor()` - BelongsTo [Vendor Model](Vendor Model.md)
  - `user()` - BelongsTo [User Model](User Model.md)
  - `buyer()` - BelongsTo [Buyer Model](Buyer Model.md)
  - `project()` - BelongsTo [Project Model](Project Model.md)
  - `purchaseList()` - HasOne [PurchaseList Model](PurchaseList Model.md)

#### [BoqSheetMerge Model](BoqSheetMerge Model.md)
- **Purpose:** Excel-style merged cells for dynamic extra columns
- **Table:** `boq_sheet_merges`
- **Key Fields:**
  - `boq_sheet_id` (unsignedBigInteger) - Reference to sheet (no FK constraint)
  - `extra_fields` (json) - Array of column names being merged
  - `boq_sheet_entry_ids` (json) - Array of entry IDs being merged
- **Relationships:**
  - `boqSheet()` - BelongsTo [BoqSheet Model](BoqSheet Model.md)
- **Note:** No DB-level FK to avoid MySQL 1824 errors; integrity enforced in app code

### Controllers

#### [BoqSheetController](BoqSheetController.md) (Buyer namespace)
- **Lines:** 503
- **Purpose:** Manage BOQ sheets for buyer projects
- **Key Methods:**
  - `index()` - Get all sheets for project with entries and merges
  - `store()` - Create new sheet via [BoqSheetService](BoqSheetService.md)
  - `update()` - Update sheet name
  - `show()` - Get specific sheet with entries
  - `destroy()` - Delete sheet (only if no entries)
  - `exchangeSheetOrder()` - Swap sheet order positions
  - `addExtraColumn()` - Add dynamic column via service
  - `renameColumn()` - Rename dynamic column
  - `deleteExtraColumn()` - Remove dynamic column
  - `listExtraFieldMerges()` - Get all merges for sheet
  - `storeExtraFieldMerge()` - Create new merge
  - `updateExtraFieldMerge()` - Update existing merge
  - `destroyExtraFieldMerge()` - Delete merge
  - `exportProjectBoqSheets()` - Export to Excel
  - `getProjectsWithBoqSheets()` - Get buyer's projects with sheets

#### [BoqEntryController](BoqEntryController.md) (Buyer namespace)
- **Lines:** 527
- **Purpose:** Manage individual BOQ entries
- **Key Methods:**
  - `index()` - Get all entries for a sheet
  - `show()` - Get specific entry with relationships
  - `update()` - Update dynamic values and cell colors only
  - `destroy()` - Delete entry via service
  - `addEntryToBoqSheet()` - Add entry from quotation
  - `addDirectEntryToBoqSheet()` - Add entry directly from product
  - `updateCellColors()` - Update cell colors for entry
  - `exchangeEntryOrder()` - Swap entry positions with locking
  - `bulkStore()` - Create multiple entries at once
  - `deleteEntryFromBoqSheet()` - Delete entry via service
  - `exchangeEntrySheet()` - Move entry to different sheet

### Services

#### [BoqSheetService](BoqSheetService.md)
- **Lines:** 334
- **Purpose:** Core BOQ sheet business logic
- **Key Methods:**
  - `createBoqSheet()` - Create new sheet with auto-incremented order
  - `addExtraColumns()` - Add dynamic column with validation
  - `updateExtraColumnName()` - Rename column and update all references
  - `deleteExtraColumn()` - Remove column and clean up references
- **Behavior:**
  - Validates column names (4-50 chars, unique)
  - Updates all BoqEntry records when column renamed/deleted
  - Updates/cleans up BoqSheetMerge records when column deleted

#### [BoqSheetEntryService](BoqSheetEntryService.md)
- **Lines:** 450
- **Purpose:** Entry-level operations with purchase list integration
- **Key Methods:**
  - `storeOrUpdate()` - Create/update entry with dynamic values
  - `addColors()` - Add cell colors with hex validation
  - `addMerge()` - Create merge via [BoqSheetMergeService](BoqSheetMergeService.md)
  - `addEntryToBoqSheet()` - Add from quotation, updates RFQ status
  - `addDirectEntryToBoqSheet()` - Add directly from product
  - `deleteEntryFromBoqSheet()` - Delete with purchase list cleanup
  - `exchangeEntrySheet()` - Move entry between sheets
- **Behavior:**
  - Integrates with [PurchaseListService](PurchaseListService.md)
  - Updates RFQ/Quotation statuses on entry operations
  - Recalculates entry_order on deletion
  - Clears dynamic values when moving between sheets

#### [BoqSheetMergeService](BoqSheetMergeService.md)
- **Lines:** 239
- **Purpose:** Manage Excel-style cell merges
- **Key Methods:**
  - `listForSheet()` - Get all merges for sheet
  - `store()` - Create merge with overlap detection
  - `update()` - Update merge with validation
  - `destroy()` - Delete merge
- **Behavior:**
  - Validates merge covers at least 2 cells
  - Detects and prevents overlapping merges
  - Validates columns exist in sheet's extra_columns
  - Validates entry IDs belong to sheet

### Resources

#### [BoqSheetResource](BoqSheetResource.md)
- Transforms sheet with entries, merges, and calculated totals
- Converts `extra_columns` string to array
- Includes `sum_total_amount` from entries

#### [BoqEntryResource](BoqEntryResource.md)
- Transforms entry with all pricing fields
- Resolves image URLs with fallback
- Includes `merged_cells` from [BoqSheetMerge Model](BoqSheetMerge Model.md)
- Filters `cell_colors` to dynamic columns only

#### [BoqSheetMergeResource](BoqSheetMergeResource.md)
- Simple transformation of merge data

## Dependencies & Graph Links

### God Nodes (from graph report)
- `BoqEntry` - 22 edges (5th most connected)
- `BoqSheetController` - Community 26 (isolated controller node)

### Community Structure
- **Community 0:** Contains BoqEntryController, BoqSheetController (low cohesion 0.03)
- **Community 17:** BoqSheetMerge, BoqDetails, BoqEntryResource, BoqSheetMergeResource, BoqSheetResource (cohesion 0.13)

### External Dependencies
- [Project Model](Project Model.md) - Sheets belong to projects
- [Product Model](Product Model.md) - Entries reference products
- [Quotation Model](Quotation Model.md) - Entries can be created from quotations
- [Rfq Model](Rfq Model.md) - Entries reference RFQ codes
- [Vendor Model](Vendor Model.md) - Entries reference vendors
- [PurchaseList Model](PurchaseList Model.md) - Entries have one-to-one with purchase lists
- [PurchaseListService](PurchaseListService.md) - Integration for purchase order creation

### Data Flow
1. Buyer creates project → [Project Model](Project Model.md)
2. Buyer creates BOQ sheet → [BoqSheet Model](BoqSheet Model.md)
3. Buyer adds dynamic columns → [BoqSheetService](BoqSheetService.md)
4. Buyer adds entries (from quotation or product) → [BoqSheetEntryService](BoqSheetEntryService.md)
5. Entries create purchase lists → [PurchaseListService](PurchaseListService.md)
6. Buyer can merge cells → [BoqSheetMergeService](BoqSheetMergeService.md)
7. Buyer exports to Excel → [ProjectBoqSheetsExport](ProjectBoqSheetsExport.md)

## Red Flags & Tech Debt

### Fat Controllers
1. **BoqSheetController (503 lines)** - Large controller with many methods
   - Consider extracting merge operations to separate controller
   - Move export logic to dedicated service

2. **BoqEntryController (527 lines)** - Large controller
   - Duplicate buyer validation in multiple methods
   - Commented out `store()` method (lines 50-122) should be removed
   - Consider splitting into separate controllers for different operations

### Code Quality Issues
1. **Duplicate Code** - Buyer validation repeated in every method
   ```php
   // Repeated pattern in both controllers
   $buyer = $this->currentBuyer();
   if (!$buyer) {
       return $this->error('Buyer profile not found.', [], 404);
   }
   ```

2. **Duplicate Catch Block** - In `BoqSheetEntryService::deleteEntryFromBoqSheet()`
   ```php
   } catch (\Exception $e) {
       DB::rollBack();
       logger('Error deleting entry from BoqSheet: '.$e->getMessage());
       return $this->error('Failed to delete entry from BoqSheet', [$e->getMessage()]);
   }
   catch (\Exception $e) {  // DUPLICATE!
       logger('Error deleting entry from BoqSheet: '.$e->getMessage());
       return $this->error('Failed to delete entry from BoqSheet', [$e->getMessage()]);
   }
   ```

3. **Typo in Migration** - `unsigendInteger` should be `unsignedInteger`
   ```php
   // Line 52 in boq_entries migration
   $table->unsigendInteger('entry_order')->default(1);
   ```

4. **Inconsistent Error Handling** - Some methods return error arrays, others throw exceptions

### N+1 Query Issues
1. **BoqSheetController::index()** - Loads nested relationships without eager loading
   ```php
   $first_sheet = $selectedProject->boqSheets()->with('entries.quotation.rfq','entries.quotation.product', ...)->first();
   ```
   - Consider using `with()` on all nested relationships

2. **BoqEntryController::index()** - Loads merges for each entry
   ```php
   $entries = BoqEntry::where('boq_sheet_id', $boqSheet->id)
       ->with('boqSheet.boqSheetMerges')
       ->get();
   ```

### Race Conditions
1. **Entry Order Calculation** - No locking in `addEntryToBoqSheet()`
   ```php
   $entryOrder = $boqSheet->entries()->max('entry_order') + 1;
   ```
   - Should use `lockForUpdate()` like in `exchangeEntryOrder()`

2. **Sheet Order Calculation** - No locking in `createBoqSheet()`
   ```php
   $lastSheet = $project->boqSheets()->orderBy('sheet_order', 'desc')->first();
   $sheetOrder = $lastSheet ? $lastSheet->sheet_order + 1 : 1;
   ```

### Missing Database Indexes
1. **boq_entries table** - Missing indexes on:
   - `boq_sheet_id` (frequently queried)
   - `entry_order` (used for ordering)
   - `project_id` (used in joins)
   - `buyer_id` (used for authorization)

2. **boq_sheets table** - Missing indexes on:
   - `project_id` (frequently queried)
   - `sheet_order` (used for ordering)

### Data Integrity Issues
1. **No FK Constraint on boq_sheet_merges** - Intentional but risky
   - Comment says "avoids MySQL 1824" but could cause orphaned records
   - Consider adding FK with proper error handling

2. **Cascade Delete Issues** - Multiple foreign keys with `onDelete('cascade')`
   - Could cause unexpected data loss
   - Consider soft deletes or explicit cleanup

### Performance Issues
1. **Large JSON Columns** - `dynamic_values`, `cell_colors`, `merged_cells` can grow large
   - Consider using separate table for dynamic columns
   - Add JSONB indexes if using PostgreSQL

2. **Excel Export** - No pagination or chunking for large projects
   - Could timeout on projects with many sheets/entries

### Security Issues
1. **Authorization Checks** - Buyer ownership checked but no role-based access
   - Consider using Laravel policies

2. **Input Validation** - Some fields lack proper validation
   - `extra_columns` names should be validated for SQL injection
   - Hex color validation exists but could be stricter

## Future Upgrades (Postgres & Scalability)

### Database Schema Improvements
1. **Add Missing Indexes**
   ```sql
   CREATE INDEX idx_boq_entries_sheet_id ON boq_entries(boq_sheet_id);
   CREATE INDEX idx_boq_entries_entry_order ON boq_entries(entry_order);
   CREATE INDEX idx_boq_entries_project_id ON boq_entries(project_id);
   CREATE INDEX idx_boq_entries_buyer_id ON boq_entries(buyer_id);
   CREATE INDEX idx_boq_sheets_project_id ON boq_sheets(project_id);
   CREATE INDEX idx_boq_sheets_sheet_order ON boq_sheets(sheet_order);
   ```

2. **Use JSONB for Dynamic Columns** (PostgreSQL)
   ```sql
   ALTER TABLE boq_entries ALTER COLUMN dynamic_values TYPE JSONB;
   ALTER TABLE boq_entries ALTER COLUMN cell_colors TYPE JSONB;
   CREATE INDEX idx_boq_entries_dynamic_values ON boq_entries USING GIN(dynamic_values);
   ```

3. **Add Composite Indexes**
   ```sql
   CREATE INDEX idx_boq_entries_sheet_order ON boq_entries(boq_sheet_id, entry_order);
   CREATE INDEX idx_boq_sheets_project_order ON boq_sheets(project_id, sheet_order);
   ```

4. **Add Foreign Key Constraints** (with proper error handling)
   ```sql
   ALTER TABLE boq_sheet_merges
   ADD CONSTRAINT fk_boq_sheet_merges_sheet_id
   FOREIGN KEY (boq_sheet_id) REFERENCES boq_sheets(id) ON DELETE CASCADE;
   ```

### Architecture Improvements
1. **Extract Fat Controllers**
   - Create `BoqSheetMergeController` for merge operations
   - Create `BoqSheetExportController` for export operations
   - Move validation to Form Request classes

2. **Implement Repository Pattern**
   - Create `BoqSheetRepository` for data access
   - Create `BoqEntryRepository` for data access
   - Reduce coupling between controllers and models

3. **Add Caching Layer**
   - Cache sheet structure (extra_columns)
   - Cache entry counts and totals
   - Use Redis for distributed locking

4. **Implement Event-Driven Architecture**
   - Dispatch events on entry creation/deletion
   - Listen for events to update purchase lists
   - Decouple services from each other

### Performance Optimizations
1. **Chunked Operations**
   - Use `chunk()` for bulk operations on large datasets
   - Implement queue-based processing for exports

2. **Query Optimization**
   - Use `withCount()` for counting relationships
   - Implement cursor-based pagination for large lists
   - Add query scopes for common filters

3. **Database Connection Pooling**
   - Configure read replicas for reporting queries
   - Use separate connection for exports

### Scalability Improvements
1. **Horizontal Scaling**
   - Design for stateless operations
   - Use Redis for distributed locking
   - Implement idempotent operations

2. **Data Partitioning**
   - Consider partitioning by project_id for large datasets
   - Archive old projects to separate tables

3. **Monitoring & Observability**
   - Add metrics for sheet/entry operations
   - Track query performance
   - Monitor JSON column sizes

### Security Enhancements
1. **Implement Laravel Policies**
   - Create `BoqSheetPolicy` for authorization
   - Create `BoqEntryPolicy` for authorization
   - Centralize authorization logic

2. **Input Sanitization**
   - Sanitize extra column names
   - Validate hex colors more strictly
   - Add rate limiting for bulk operations

3. **Audit Logging**
   - Log all sheet/entry modifications
   - Track who made changes and when
   - Implement soft deletes for recovery
