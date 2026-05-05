---
aliases: [Boq-Domain, BoqSheet-Domain]
tags: [laravel, backend, auto-generated, boq, god-node]
title: "BOQ (Bill of Quantities) Domain"
---

# BOQ (Bill of Quantities) Domain

## Overview

The BOQ (Bill of Quantities) domain is the central ledger for project materials, serving as the bridge between project requirements, vendor quotations, and final procurement. It represents one of the most complex subsystems in the application, implementing dynamic "Excel-like" behavior within a relational database. It is deeply integrated with the **[Project-Domain](./Project-Domain.md)**, **[RFQ-Quotation-Domain](./RFQ-Quotation-Domain.md)**, and **[PurchaseList-Domain](./PurchaseList-Domain.md)**.

## Current Architecture & Flow

### Core Components

#### Models

- **[Boq](./Boq Model.md)** - The root entity binding sheets to a project. A very thin wrapper model.
- **[BoqSheet](./BoqSheet Model.md)** - Represents a single sheet (page) of a BOQ. Contains dynamic "Extra Columns" configured per sheet.
- **[BoqEntry](./BoqEntryModel.md)** - Represents an individual line item. Stores dynamic cell values (`dynamic_values`) and UI properties (`cell_colors`) in JSON fields.
- **[BoqSheetMerge](./BoqSheetMergeModel.md)** - Manages visual "merged cells" across rows and columns using coordinate-style mapping.

#### Services

- **[BoqSheetService](./BoqSheetService.md)** - Manages sheet metadata and the fragile dynamic schema logic (adding, renaming, deleting extra columns). It handles cascading key renaming inside `BoqEntry` JSON fields.
- **[BoqSheetEntryService](./BoqSheetEntryService.md)** - Orchestrates the lifecycle of entries. It acts as the bridge that converts a vendor's Quotation into an actionable BOQ line item, automatically creating downstream PurchaseList records.
- **[BoqSheetMergeService](./BoqSheetMergeService.md)** - Handles coordinate overlap detection and validation for merged cells.

#### Controllers

- **[BoqController](./BoqSheetController.md)** - Basic CRUD for the root BOQ entity. (Note: Using BoqSheetController as closest match if BoqController is missing)
- **[BoqSheetController](./BoqSheetController.md)** - Manages sheets and the dynamic extra columns endpoints.
- **[BoqEntryController](./BoqEntryController.md)** - Handles entry modifications, deletions, and entry shifting.

#### Resources

- **[BoqSheetResource](./BoqSheetResource.md)**, **[BoqEntryResource](./BoqEntryResource.md)**, **[BoqSheetMergeResource](./BoqSheetMergeResource.md)**, **BoqDetails** - Transforms dynamic JSON payloads and normalizes coordinate tracking for the frontend grid rendering.


### The BOQ Lifecycle Flow

#### 1. BOQ Initialization & Schema Definition
1. A **Project** creates a root `Boq` and an initial `BoqSheet`.
2. The user adds "Extra Columns" (e.g., 'Color', 'Material Grade'). 
3. `BoqSheetService::addExtraColumns()` appends these to the `extra_columns` comma-separated string on the `BoqSheet` model.

#### 2. Entry Ingestion (The RFQ Bridge)
Entries enter the BOQ primarily via accepted Quotations.
1. The buyer accepts a vendor quote. `BoqSheetEntryService::addEntryToBoqSheet()` is invoked.
2. The quotation status is updated to `accepted`. Competing quotes are rejected.
3. A new `BoqEntry` is created, inheriting `unit_price`, `tax_amount`, `shipping_amount`, and calculated `total_amount` from the quote.
4. **Procurement Trigger**: The service immediately calls `PurchaseListService::addToPurchaseListFromQuotation()` to stage the item for a Purchase Order.

#### 3. Dynamic Cell Formatting & Merging
1. The user inputs custom data into the dynamic columns. `BoqSheetEntryService::storeOrUpdate()` validates the keys against `BoqSheet->extra_columns` and saves them to `dynamic_values` JSON.
2. The user highlights cells. Colors are mapped to `cell_colors` JSON.
3. The user merges cells. `BoqSheetMergeService::store()` verifies no coordinate overlaps (`entryId:columnName`) and persists the `BoqSheetMerge` record.

#### 4. Entry Re-ordering & Deletion
1. When an entry is deleted, `BoqSheetEntryService::deleteEntryFromBoqSheet()` executes a heavy cascade.
2. It cancels the associated `PurchaseList` and recalculates the `PurchaseOrder`.
3. It performs a mass `decrement('entry_order')` on all entries below the deleted one to close the gap.

## Dependencies & Graph Links

### Direct Dependencies
- **[Project-Domain](./Project-Domain.md)** - A BOQ cannot exist without a parent project.
- **[PurchaseList-Domain](./PurchaseList-Domain.md)** - `BoqSheetEntryService` intimately drives `PurchaseListService` state.
- **[RFQ-Quotation-Domain](./RFQ-Quotation-Domain.md)** - Quotations act as the primary data source for BOQ Entries.


## Red Flags & Tech Debt

### 1. Fragile Dynamic Schema (Schema-on-Write Anti-Pattern)
**Location**: `app/Models/BoqSheet.php`, `app/Service/BoqSheetService.php`

**Issue**: 
- `extra_columns` is a comma-separated string.
- If a column is renamed, `updateExtraColumnName` uses a massive PHP O(N) loop to load every `BoqEntry` and `BoqSheetMerge`, rewrite the JSON array keys in memory, and save them back one by one.
- **Risk**: Memory exhaustion, timeout on large sheets, and severe database thrashing.

### 2. Missing Database Transactions
**Location**: `app/Service/BoqSheetService.php:125-200`

**Issue**: 
- The column renaming logic performs hundreds of related updates but lacks an overarching `DB::beginTransaction()`.
- **Risk**: If the script times out halfway, the sheet is left in an unrecoverable corrupted state (some rows have the new column key, others have the old one).

### 3. Race Condition in Entry Ordering
**Location**: `app/Service/BoqSheetEntryService.php:400-410`

**Issue**: 
- `BoqEntry::query()->where('entry_order', '>', $deletedOrder)->decrement('entry_order');`
- **Risk**: Without a pessimistic lock (`lockForUpdate()`), concurrent deletions or insertions by multiple project managers will lead to duplicate or skipped `entry_order` numbers, breaking the UI sequence.

### 4. In-Memory Overlap Check for Merged Cells
**Location**: `app/Service/BoqSheetMergeService.php:hasOverlapWithExisting()`

**Issue**: 
- Overlap validation loads all merges for a sheet and performs coordinate mapping in PHP.
- **Risk**: Scales poorly as the number of merges increases, creating a CPU bottleneck on save operations.

### 5. Deep Coupling with Procurement
**Location**: `app/Service/BoqSheetEntryService.php`

**Issue**: 
- Deleting a BOQ Entry reaches deep into `PurchaseOrder` costing recalculations and `Quotation` status resets. 
- **Risk**: Domain Boundary violation. The BOQ domain should dispatch a `BoqEntryDeleted` event, and the PurchaseList domain should listen and react, rather than hardcoding the logic here.

## Future Upgrades (Postgres & Scalability)

### 1. Migrate to Postgres JSONB
- **Action**: Convert `extra_columns` to a strict `JSONB` array. 
- **Benefit**: Instead of PHP loops, renaming a column across 10,000 entries can be done instantly with a single SQL query using `jsonb_set()`.

### 2. Implement Database-Level Exclusion Constraints
- **Action**: Use Postgres GIST indexes with exclusion constraints for `BoqSheetMerge`.
- **Benefit**: Prevent overlapping merged cells with absolute mathematical certainty at the database level, removing the need for the brittle PHP checks.

### 3. Event-Driven Decoupling
- **Action**: Replace direct `PurchaseListService` calls in `deleteEntryFromBoqSheet` with `event(new BoqEntryRemoved($entry))`.
- **Benefit**: Isolates domain failures and makes the codebase easier to test.

### 4. Precision Financials
- **Action**: While `bcmul` is used in the service, ensure the database schema for `total_amount`, `vat_tax`, and `services_charge` uses strict `DECIMAL(15,4)` types to prevent floating-point drift over time.
