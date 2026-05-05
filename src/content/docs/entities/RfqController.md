---
name: RfqController
description: Laravel HTTP controller for RFQ (Request for Quotation) management - handles all HTTP requests for RFQ operations for buyers
type: entity
title: "RfqController"
---

# RfqController

## Architectural Purpose

`RfqController` (located in `App\Http\Controllers\Buyer\`) is the primary HTTP endpoint handler for all RFQ operations for buyers. This controller serves as the API gateway for:

- **RFQ CRUD**: Create, read, update, and delete RFQs
- **RFQ Types**: Manage both public and private RFQs
- **Vendor Engagement**: Manage private RFQs sent to specific vendors
- **RFQ Visibility**: Control public vs private RFQ access
- **Status Management**: Handle RFQ lifecycle and status transitions
- **Document Handling**: Handle RFQ document uploads
- **Image Management**: Handle product images for RFQs

This controller delegates business logic to [RfqService](./RfqService.md), following the thin controller pattern. It enforces strict authorization rules to ensure only authorized buyers can access their RFQs.

## Controller Dependencies

```php
use App\Http\Controllers\BaseController;
use App\Http\Requests\PrivateRfqRequest;
use App\Http\Requests\StoreRfqRequest;
use App\Http\Requests\UpdateRfqRequest;
use App\Models\Buyer;
use App\Models\Rfq;
use App\Models\Vendor;
use App\Service\RfqService;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
```

- **RfqService**: Handles all RFQ business logic
- **BaseController**: Provides common controller functionality
- **AuthorizesRequests**: Enables authorization middleware

## API Endpoints

### `GET /api/buyer/rfqs` - `index()`

**Purpose:** Get all RFQs for the authenticated buyer.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::getRfqsForBuyer()`
3. Returns paginated results with status counts

**Response:**
```json
{
  "status": "success",
  "message": "RFQs fetched successfully",
  "data": {
    "rfqs": [ /* RfqResource collection */ ],
    "total": 50,
    "per_page": 15,
    "current_page": 1,
    "last_page": 4,
    "next_page_url": "https://api.example.com/api/buyer/rfqs?page=2",
    "prev_page_url": null,
    "status_counts": {
      "total": 50,
      "pending": 25,
      "active": 15,
      "closed": 8,
      "cancelled": 2
    }
  }
}
```

### `POST /api/buyer/rfqs` - `store()`

**Purpose:** Create a new RFQ.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Request Body:**
```json
{
  "rfq_title": "Office Furniture Requirement",
  "description": "Need office chairs and desks for new office setup",
  "project_id": 1,
  "product_id": 1,
  "vendor_id": 1,
  "category_id": 5,
  "type": "public",
  "dead_line_date": "2024-01-15",
  "unit": "pieces",
  "estimated_quantity": 150.5,
  "urgency": "high",
  "detailed_requirement": "Please provide ergonomic chairs with adjustable height",
  "budget_min": 50000,
  "budget_max": 150000,
  "product_image": "rfq/product-images/sample.jpg"
}
```

**Validation:**
- `rfq_title`: Required, string, max 255
- `dead_line_date`: Required, date format
- `type`: Required, enum: `public` or `private`
- `urgency`: Required, enum: `low`, `medium`, `high`

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::createRfq()`
3. Returns created RFQ with 201 status

**Response:**
```json
{
  "status": "success",
  "message": "RFQ created successfully",
  "data": { /* RfqResource */ },
  "code": 201
}
```

### `GET /api/buyer/rfqs/{rfq}` - `show()`

**Purpose:** Get a specific RFQ with full details.

**Authorization:** Requires authenticated buyer with ownership or public access.

**Behavior:**
1. Validates buyer ownership or public access
2. Delegates to `RfqService::getRfq()`
3. Returns RFQ resource

**Response:**
```json
{
  "status": "success",
  "message": "RFQ fetched successfully",
  "data": { /* RfqResource */ }
}
```

### `PUT /api/buyer/rfqs/{rfq}` - `update()`

**Purpose:** Update an existing RFQ.

**Authorization:** Requires authenticated buyer who created the RFQ.

**Request Body:**
```json
{
  "rfq_title": "Updated Office Furniture Requirement",
  "description": "Updated requirement details",
  "project_id": 1,
  "product_id": 1,
  "vendor_id": 1,
  "category_id": 5,
  "type": "private",
  "dead_line_date": "2024-02-15",
  "unit": "pieces",
  "estimated_quantity": 200,
  "urgency": "medium",
  "detailed_requirement": "Updated requirement details",
  "budget_min": 60000,
  "budget_max": 180000,
  "status": "in_progress"
}
```

**Validation:**
- `rfq_title`: Required, string, max 255
- `dead_line_date`: Required, date format
- `type`: Required, enum: `public` or `private`
- `urgency`: Required, enum: `low`, `medium`, `high`
- `status`: Required, enum: `pending`, `in_progress`, `completed`, `cancelled`

**Behavior:**
1. Validates buyer ownership
2. Validates status is not terminal
3. Validates type is not private
4. Delegates to `RfqService::updateRfq()`
5. Returns updated RFQ

**Response:**
```json
{
  "status": "success",
  "message": "RFQ updated successfully",
  "data": { /* RfqResource */ }
}
```

### `DELETE /api/buyer/rfqs/{rfq}` - `destroy()`

**Purpose:** Delete an RFQ.

**Authorization:** Requires authenticated buyer who created the RFQ.

**Behavior:**
1. Validates buyer ownership
2. Delegates to `RfqService::deleteRfq()`
3. Returns success

**Response:**
```json
{
  "status": "success",
  "message": "RFQ deleted successfully"
}
```

### `GET /api/public-rfqs` - `getPublicRfqsForBuyer()`

**Purpose:** Get public RFQs for a buyer.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::getPublicRfqsForBuyer()`
3. Returns paginated results

**Response:**
```json
{
  "status": "success",
  "message": "Public RFQs fetched successfully",
  "data": {
    "rfqs": [ /* RfqResource collection */ ],
    "total": 50,
    "per_page": 15,
    "current_page": 1,
    "last_page": 4,
    "next_page_url": "https://api.example.com/api/buyer/rfqs?page=2",
    "prev_page_url": null
  }
}
```

### `GET /api/buyer/rfqs/private` - `getPrivateRfqs()`

**Purpose:** Get private RFQs for a buyer.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::getPrivateRfqsForBuyer()`
3. Returns paginated results

**Response:**
```json
{
  "status": "success",
  "message": "Private RFQs fetched successfully",
  "data": {
    "rfqs": [ /* PrivateRfqResource collection */ ],
    "total": 50,
    "per_page": 10,
    "current_page": 1,
    "last_page": 4,
    "next_page_url": "https://api.example.com/api/buyer/rfqs/private?page=2",
    "prev_page_url": null
  }
}
```

### `POST /api/buyer/rfqs/private` - `createPrivateRfq()`

**Purpose:** Create a private RFQ for a specific vendor.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Request Body:**
```json
{
  "product_id": 1,
  "vendor_id": 1,
  "project_id": 1,
  "estimated_quantity": 100
}
```

**Validation:**
- `product_id`: Required, exists in products
- `vendor_id`: Required, exists in vendors
- `project_id`: Required, exists in projects
- `estimated_quantity`: Required, numeric, min 0

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::createPrivateRfq()`
3. Returns created RFQ with notification to vendor

**Response:**
```json
{
  "status": "success",
  "message": "Private RFQ created successfully",
  "data": { /* RfqResource */ }
}
```

### `POST /api/buyer/rfqs/{rfq}/reject` - `rejectRfq()`

**Purpose:** Reject an RFQ and all its quotations.

**Authorization:** Requires authenticated buyer who owns the RFQ.

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates buyer ownership
3. Sets RFQ status to 'rejected'
4. Rejects all associated quotations
5. Returns success

**Transaction Scope:**
```php
DB::transaction(function () use ($rfq) {
    $rfq->status = 'rejected';
    $rfq->save();
    $rfq->quotations()->update(['status' => 'rejected']);
});
});
```

**Response:**
```json
{
  "status": "success",
  "message": "RFQ rejected successfully"
}
```

## Authorization Pattern

All methods follow this authorization pattern:

```php
$user = Auth::user();
if (!$user->buyer_id) {
    return $this->error('Only buyers can access RFQs', [], 403);
}

$buyer = Buyer::find($user->buyer_id);
if (!$buyer) {
    return $this->error('Buyer profile not found', [], 404);
}

// Additional ownership checks based on method
```

**Helper Method:**
```php
// Uses Auth facade for authentication
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No transaction in `rejectRfq()` | MEDIUM | Partial updates on failure | Wrap in `DB::transaction()` |
| Commented code in `getPrivateRfqs()` | LOW | Code confusion | Remove or document |
| No rate limiting | LOW | Potential abuse | Add rate limiting middleware |
| No input sanitization | LOW | XSS risk | Add sanitization middleware |

## Cross-References

- [RfqService](./RfqService.md) - Business logic for RFQ operations
- [Rfq-Model](./Rfq-Model.md) - Data model for RFQs
- [Quotation-Model](./Quotation-Model.md) - Vendor responses to RFQs
- [RfqResource](./RfqResource.md) - API resource for serialization
- PrivateRfqResource - API resource for private RFQs

## Usage Examples

### Getting all RFQs for buyer

```bash
GET /api/buyer/rfqs
Authorization: Bearer {jwt_token}
```

### Creating a public RFQ

```bash
POST /api/buyer/rfqs
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "rfq_title": "Office Furniture Requirement",
  "type": "public",
  "dead_line_date": "2024-01-15",
  "urgency": "high"
}
```

### Creating a private RFQ

```bash
POST /api/buyer/rfqs/private
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "product_id": 1,
  "vendor_id": 1,
  "project_id": 1,
  "estimated_quantity": 100
}
```

### Updating an RFQ

```bash
PUT /api/buyer/rfqs/1
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "rfq_title": "Updated Office Furniture Requirement",
  "urgency": "medium",
  "status": "in_progress"
}
```

### Deleting an RFQ

```bash
DELETE /api/buyer/rfqs/1
Authorization: Bearer {jwt_token}
```

### Getting public RFQs

```bash
GET /api/buyer/rfqs/public
Authorization: Bearer {jwt_token}
```

### Getting private RFQs

```bash
GET /api/buyer/rfqs/private
Authorization: Bearer {jwt_token}
```

### Rejecting an RFQ

```bash
POST /api/buyer/rfqs/1/reject
Authorization: Bearer {jwt_token}
```
