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

#### [Project Model](./Project Model.md)
- **Location**: `app/Models/Project.php` (64 lines)
- **Relationships**:
  - `buyer()` - BelongsTo [Buyer Model](./Buyer Model.md)
  - `projectManager()` - BelongsTo [User Model](./User Model.md)
  - `boqEntries()` - HasMany [BoqEntry Model](./BoqEntry Model.md)
  - `boqSheets()` - HasMany [BoqSheet Model](./BoqSheet Model.md)
  - `rfqs()` - HasMany [Rfq Model](./Rfq Model.md)
- **Features**: Soft deletes enabled

#### [ProjectService](./ProjectService.md)
- **Location**: `app/Service/ProjectService.php` (183 lines)
- **Methods**:
  - `listProjects()` - Paginated listing with search, filters, and RFQ counts
  - `createProject()` - Creates project with default "Sheet 1" BOQ sheet
  - `getProject()` - Single project retrieval with ownership check
  - `updateProject()` - Updates project with ownership check
  - `deleteProject()` - Soft deletes project
  - `prepareData()` - Prepares data with auto-generated project codes
  - `generateUniqueProjectCode()` - Generates unique codes (PRJ-XXX-XXXXX)

#### [ProjectController](./ProjectController.md)
- **Location**: `app/Http/Controllers/Buyer/ProjectController.php` (93 lines)
- **Endpoints**: index, store, show, update, destroy
- **Authentication**: Uses `JWTAuth::user()` for buyer resolution
- **Pattern**: Thin controller delegating to service layer

#### Resources
- `[ProjectResource](./ProjectResource.md)` - Basic project data (40 lines)
- `[ProjectResourceWithCompletion](./ProjectResourceWithCompletion.md)` - Includes RFQ counts (41 lines)

#### Validation
- `[ProjectRequest](./ProjectRequest.md)` - Form request with validation rules (93 lines)

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
- [ProjectController](./ProjectController.md)
- [PurchaseOrderController](./PurchaseOrderController.md)
- EnsureBoqSheetForProjects (Console Command)
- [Buyer Model](./Buyer Model.md)
- [ProjectResourceWithCompletion](./ProjectResourceWithCompletion.md)
- [ProjectSeeder](./ProjectSeeder.md)
- [ProjectService](./ProjectService.md)

### External Connections
- Connects to [BoqSheet Model](./BoqSheet Model.md) via `boqSheets()` relationship
- Connects to [BoqEntry Model](./BoqEntry Model.md) via `boqEntries()` relationship
- Connects to [Rfq Model](./Rfq Model.md) via `rfqs()` relationship
- Connects to [PurchaseOrderController](./PurchaseOrderController.md) (cross-community bridge)

## Red Flags & Tech Debt

### Race Conditions
1. **Project Code Generation Race** (`ProjectService::generateUniqueProjectCode()`, lines 170-181)
   - do-while loop without database locking
   - Two concurrent requests could generate same code
   - **Fix**: Use `SELECT FOR UPDATE` or unique constraint with retry logic

### Code Quality Issues
1. **Commented-Out Dead Code** (`ProjectService.php`, lines 52-54)
   ```php
   // ->withCount('completed_rfqs'=>function($query){
   //     $query->where('status', 'completed');
   // })
   ```
   - Should be removed or properly documented

2. **Commented-Out Resource Fields** (`ProjectResource.php`, line 31)
   ```php
   // 'project_manager' => new UserResource($this->whenLoaded('projectManager')),
   ```
   - Same in `ProjectResourceWithCompletion.php`, line 31
   - Inconsistent with buyer relationship being loaded

### Query Performance
1. **N+1 Query Risk** (`ProjectService::listProjects()`, lines 45-51)
   - `withCount` with nested `whereHas` on purchaseList
   - Could be slow with many RFQs per project
   - **Fix**: Consider caching or denormalizing completion counts

2. **Missing Database Indexes**
   - `buyer_id` - frequently filtered
   - `boq_status` - frequently filtered
   - `project_manager_id` - frequently filtered
   - `created_at` - used for ordering

### Data Integrity
1. **No Check Constraints**
   - `progress_count` should be 0-100 (only validated in request)
   - `total_budget` should be >= 0 (only validated in request)
   - `estimated_end_date` should be >= `start_date` (only validated in request)

2. **Soft Delete Cascade Issues**
   - Projects soft-deleted but related records (BOQ sheets, RFQs) remain
   - No cleanup strategy for orphaned records
   - **Fix**: Implement cascade soft deletes or cleanup jobs

### Security & Authorization
1. **Manual Authorization Checks**
   - Ownership checks in service layer (`buyer_id !== $buyer->id`)
   - Should use Laravel Policies instead
   - `ProjectPolicy` exists but not used

2. **No Rate Limiting**
   - Project creation/update endpoints have no rate limits
   - Could be abused for spam

### Caching
1. **No Caching Strategy**
   - Project listings fetched fresh every time
   - RFQ counts recalculated on every request
   - **Fix**: Cache project listings and counts

## Future Upgrades (Postgres & Scalability)

### Database Improvements
1. **Add Missing Indexes**
   ```sql
   CREATE INDEX idx_projects_buyer_id ON projects(buyer_id);
   CREATE INDEX idx_projects_boq_status ON projects(boq_status);
   CREATE INDEX idx_projects_project_manager_id ON projects(project_manager_id);
   CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
   ```

2. **Add Check Constraints**
   ```sql
   ALTER TABLE projects ADD CONSTRAINT chk_progress_count
     CHECK (progress_count >= 0 AND progress_count <= 100);
   ALTER TABLE projects ADD CONSTRAINT chk_total_budget
     CHECK (total_budget >= 0);
   ```

3. **Use Generated Columns for Computed Values**
   - Store RFQ counts as generated columns
   - Eliminate need for complex withCount queries

4. **Implement Cascade Soft Deletes**
   - Use Laravel's soft delete cascade feature
   - Or implement cleanup jobs

### Performance Improvements
1. **Add Caching Layer**
   - Cache project listings by buyer
   - Cache RFQ completion counts
   - Invalidate on project/RFQ changes

2. **Optimize Project Code Generation**
   - Use database sequence or UUID
   - Eliminate race condition risk

3. **Add Database-Level Triggers**
   - Auto-update progress_count based on BOQ completion
   - Auto-update boq_status based on workflow

### Architecture Improvements
1. **Use Laravel Policies**
   - Move authorization to `ProjectPolicy`
   - Remove manual checks from service layer

2. **Add Rate Limiting**
   - Implement rate limiting on project endpoints
   - Prevent abuse

3. **Add Event System**
   - Dispatch events on project lifecycle changes
   - Enable listeners for notifications, audits

4. **Add API Resource Versioning**
   - Prepare for future API changes
   - Maintain backward compatibility

### Monitoring & Observability
1. **Add Logging**
   - Log project creation/update/deletion
   - Track project code generation attempts

2. **Add Metrics**
   - Track project creation rate
   - Monitor RFQ completion rates
   - Alert on unusual activity

## Related Entities
- Buyer Model - Project owner
- User Model - Project manager
- [BoqSheet Model](./BoqSheet Model.md) - Project BOQ sheets
- BoqEntry Model - Project BOQ entries
- [Rfq Model](./Rfq Model.md) - Project RFQs
- [PurchaseOrderController](./PurchaseOrderController.md) - Related purchase orders
hase orders
rs
