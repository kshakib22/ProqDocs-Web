---
aliases: []
tags: [laravel, backend, auto-generated]
title: "Project Domain"
---
# Project Domain

## Overview

The Project domain manages construction projects within the system. Projects are the central entity that ties together BOQ sheets, RFQs, purchase orders, and other procurement activities. Each project belongs to a buyer and can have an assigned project manager.

## Current Architecture & Flow

### Core Components

#### [Project Model](/ProqDocs-Web/entities/project-model/)
- **Location**: `app/Models/Project.php` (64 lines)
- **Relationships**:
  - `buyer()` - BelongsTo [Buyer Model](/ProqDocs-Web/entities/buyer-model/)
  - `projectManager()` - BelongsTo [User Model](/ProqDocs-Web/entities/user-model/)
  - `boqEntries()` - HasMany [BoqEntry Model](/ProqDocs-Web/entities/boq-entry-model/)
  - `boqSheets()` - HasMany [BoqSheet Model](/ProqDocs-Web/entities/boq-sheet-model/)
  - `rfqs()` - HasMany [Rfq Model](/ProqDocs-Web/entities/rfq-model/)
- **Features**: Soft deletes enabled

#### [ProjectService](/ProqDocs-Web/entities/projectservice/)
- **Location**: `app/Service/ProjectService.php` (183 lines)
- **Methods**:
  - `listProjects()` - Paginated listing with search, filters, and RFQ counts
  - `createProject()` - Creates project with default "Sheet 1" BOQ sheet
  - `getProject()` - Single project retrieval with ownership check
  - `updateProject()` - Updates project with ownership check
  - `deleteProject()` - Soft deletes project
  - `prepareData()` - Prepares data with auto-generated project codes
  - `generateUniqueProjectCode()` - Generates unique codes (PRJ-XXX-XXXXX)

#### [ProjectController](/ProqDocs-Web/entities/projectcontroller/)
- **Location**: `app/Http/Controllers/Buyer/ProjectController.php` (93 lines)
- **Endpoints**: index, store, show, update, destroy
- **Authentication**: Uses `JWTAuth::user()` for buyer resolution
- **Pattern**: Thin controller delegating to service layer

#### Resources
- `[ProjectResource](/ProqDocs-Web/entities/projectresource/)` - Basic project data (40 lines)
- `[ProjectResourceWithCompletion](/ProqDocs-Web/entities/projectresourcewithcompletion/)` - Includes RFQ counts (41 lines)

#### Validation
- `[ProjectRequest](/ProqDocs-Web/entities/projectrequest/)` - Form request with validation rules (93 lines)

### Database Schema

```php
// projects table
- id (primary)
- project_name (string)
- buyer_id (foreign, nullable, set null on delete)
- project_code (string, unique, nullable)
- address (string, nullable)
- city (string, nullable)
- state (string, nullable)
- country (string, default 'Bangladesh')
- boq_status (enum: pending, In Progress, approved, rejected, complete)
- progress_count (unsignedTinyInteger, default 0)
- total_budget (unsignedInteger, default 0)
- start_date (date, nullable)
- estimated_end_date (date, nullable)
- project_manager_id (foreign, nullable, set null on delete)
- softDeletes()
- timestamps()
```

### Key Flows

#### Project Creation
1. Buyer submits project data via `ProjectRequest`
2. `ProjectController::store()` validates and calls `ProjectService::createProject()`
3. `prepareData()` generates unique project code if not provided
4. Project created with default status 'pending', progress 0, budget 0
5. Default "Sheet 1" BOQ sheet automatically created

#### Project Listing
1. Buyer requests projects with optional filters
2. `ProjectService::listProjects()` applies filters:
   - Search across name, code, city, state
   - Filter by boq_status
   - Filter by project_manager_id
3. Loads projectManager relationship
4. Counts total RFQs and completed RFQs (via purchaseList.is_ordered)
5. Returns paginated results with metadata

#### Project Code Generation
- Format: `PRJ-{buyer_id:03d}-{random:5}`
- Generated via `generateUniqueProjectCode()` with do-while loop
- Checks for uniqueness in database
- Can be overridden by providing custom code

## Dependencies & Graph Links

### Community 11 (Cohesion: 0.07)
- [ProjectController](/ProqDocs-Web/entities/projectcontroller/)
- [PurchaseOrderController](/ProqDocs-Web/entities/purchaseordercontroller/)
- EnsureBoqSheetForProjects (Console Command)
- [Buyer Model](/ProqDocs-Web/entities/buyer-model/)
- [ProjectResourceWithCompletion](/ProqDocs-Web/entities/projectresourcewithcompletion/)
- [ProjectSeeder](/ProqDocs-Web/entities/projectseeder/)
- [ProjectService](/ProqDocs-Web/entities/projectservice/)

### External Connections
- Connects to [BoqSheet Model](/ProqDocs-Web/entities/boq-sheet-model/) via `boqSheets()` relationship
- Connects to [BoqEntry Model](/ProqDocs-Web/entities/boq-entry-model/) via `boqEntries()` relationship
- Connects to [Rfq Model](/ProqDocs-Web/entities/rfq-model/) via `rfqs()` relationship
- Connects to [PurchaseOrderController](/ProqDocs-Web/entities/purchaseordercontroller/) (cross-community bridge)

...