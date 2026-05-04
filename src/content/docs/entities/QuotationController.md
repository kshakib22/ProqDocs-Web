---
name: QuotationController
description: Laravel HTTP controller for Quotation management - handles all HTTP requests for vendor and buyer quotation operations
type: entity
title: "QuotationController"
---

# QuotationController

## Architectural Purpose

`QuotationController` (located in `App\Http\Controllers\Vendor\`) is the primary HTTP endpoint handler for all Quotation operations for vendors. This controller serves as the API gateway for:

- **Quotation CRUD**: Create, read, update, and delete quotations
- **Vendor Engagement**: Managing vendor quotation submissions
- **Buyer Review**: Enabling buyers to review and accept/reject quotes
- **Status Management**: Handling quotation status transitions
- **Document Management**: Handling quotation document uploads
- **RFQ Integration**: Linking quotations to parent RFQs

This controller delegates business logic to [QuotationService](QuotationService.md), following the thin controller pattern. It enforces strict authorization rules to ensure only authorized vendors can access their quotations.

## Controller Dependencies

```php
use App\Http\Controllers\BaseController;
use App\Http\Requests\StoreQuotationRequest;
use App\Http\Requests\UpdateQuotationRequest;
use App\Http\Resources\PrivateRfqResource;
use App\Http\Resources\ProductResource;
use App\Http\Resources\PublicRfqResource;
use App\Http\Resources\RfqResource;
use App\Models\Document;
use App\Models\Product;
use App\Models\Quotation;
use App\Models\Rfq;
use App\Models\Vendor;
use App\Service\QuotationService;
use Illuminate\Foundation\Auth\Access\AuthorizesRequests;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Tymon\JWTAuth\Facades\JWTAuth;
```

- **QuotationService**: Handles all quotation business logic
- **BaseController**: Provides common controller functionality
- **AuthorizesRequests**: Enables authorization middleware

## API Endpoints

### `GET /api/vendor/{vendor}/quotations` - `index()`

**Purpose:** Get all quotations for the authenticated vendor.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Behavior:**
1. Validates vendor ownership
2. Delegates to `QuotationService::getQuotationsForVendor()`
3. Returns paginated results with status counts

**Response:**
```json
{
  "status": "success",
  "message": "Quotations fetched successfully",
  "data": {
    "quotations": [ /* QuotationResource collection */ ],
    "total": 50,
    "per_page": 15,
    "current_page": 1,
    "last_page": 4,
    "next_page_url": "https://api.example.com/api/vendor/1/quotations?page=2",
    "prev_page_url": null,
    "status_counts": {
      "total": 50,
      "in_review": 25,
      "accepted": 15,
      "rejected": 10
    }
  }
}
```

### `POST /api/vendor/{vendor}/quotations` - `store()`

**Purpose:** Create a new quotation for an RFQ.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Request Body:**
```json
{
  "rfq_id": 1,
  "unit_price": 50.00,
  "total_amount": 1050.00,
  "quotation_date": "2024-01-15",
  "validity_period": 30
}
```

**Validation:**
- `rfq_id`: Required, exists in rfqs
- `unit_price`: Required, numeric, min 0
- `total_amount`: Required, numeric, min 0
- `quotation_date`: Required, date format
- `validity_period`: Required, integer, min 1

**Behavior:**
1. Validates vendor ownership
2. Validates RFQ deadline not passed
3. Checks for existing quotation
4. Validates public RFQ requires image
5. Delegates to `QuotationService::createQuotation()`
6. Returns created quotation with 201 status

**Response:**
```json
{
  "status": "success",
  "message": "Quotation created successfully",
  "data": { /* QuotationResource */ },
  "code": 201
}
```

### `GET /api/vendor/{vendor}/quotations/{quotation}` - `show()`

**Purpose:** Get a specific quotation with full details.

**Authorization:** Requires authenticated vendor who owns the quotation.

**Behavior:**
1. Validates vendor ownership
2. Delegates to `QuotationService::getQuotation()`
3. Returns quotation resource

**Response:**
```json
{
  "status": "success",
  "message": "Quotation fetched successfully",
  "data": { /* QuotationResource */ }
}
```

### `PUT /api/vendor/{vendor}/quotations/{quotation}` - `update()`

**Purpose:** Update an existing quotation.

**Authorization:** Requires authenticated vendor who created the quotation.

**Request Body:**
```json
{
  "product_id": 1,
  "unit_price": 60.00,
  "total_amount": 1200.00,
  "tax_amount": 60.00,
  "shipping_amount": 30.00,
  "quotation_date": "2024-01-16",
  "validity_period": 45
}
```

**Validation:**
- `product_id`: Nullable, exists in products
- `unit_price`: Nullable, numeric, min 0
- `total_amount`: Nullable, numeric, min 0
- `tax_amount`: Nullable, numeric, min 0
- `shipping_amount`: Nullable, numeric, min 0
- `quotation_date`: Nullable, date format
- `validity_period`: Nullable, integer, min 1

**Behavior:**
1. Validates vendor ownership
2. Validates status is 'in_review'
3. Delegates to `QuotationService::updateQuotation()`
4. Returns updated quotation

**Response:**
```json
{
  "status": "success",
  "message": "Quotation updated successfully",
  "data": { /* QuotationResource */ }
}
```

### `DELETE /api/vendor/{vendor}/quotations/{quotation}` - `destroy()`

**Purpose:** Delete a quotation.

**Authorization:** Requires authenticated vendor who created the quotation.

**Behavior:**
1. Validates vendor ownership
2. Validates status is 'in_review'
3. Delegates to `QuotationService::deleteQuotation()`
4. Returns success

**Response:**
```json
{
  "status": "success",
  "message": "Quotation deleted successfully"
}
```

### `GET /api/vendor/{vendor}/quotations/{rfq}` - `getRfq()`

**Purpose:** Get RFQ details for a vendor's quotation.

**Authorization:** Requires authenticated vendor who owns the quotation.

**Behavior:**
1. Validates vendor ownership
2. Loads RFQ with relationships
3. Returns RFQ resource

**Response:**
```json
{
  "status": "success",
  "message": "RFQ fetched successfully",
  "data": { /* PrivateRfqResource */ }
}
```

### `GET /api/vendor/{vendor}/quotations/{rfq}` - `getProductQuotations()`

**Purpose:** Get product-based quotations for a vendor.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Behavior:**
1. Validates vendor ownership
2. Filters products by category
3. Returns products with quotations

**Response:**
```json
{
  "status": "success",
  "message": "Products fetched successfully",
  "data": [ /* ProductResource collection */ ]
}
```

### `GET /api/vendor/{vendor}/public-rfqs` - `getPublicRfqs()`

**Purpose:** Get public RFQs available for quoting.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Behavior:**
1. Validates vendor ownership
2. Filters by category if provided
3. Filters to RFQs without vendor quotations
4. Filters to active RFQs
5. Returns paginated results

**Response:**
```json
{
  "status": "success",
  "message": "Public RFQs fetched successfully",
  "data": {
    "rfqs": [ /* RfqResource collection */ ],
    "total": 50,
    "per_page": 10,
    "current_page": 1,
    "last_page": 4,
    "next_page_url": "https://api.example.com/api/vendor/1/public-rfqs?page=2",
    "prev_page_url": null
  }
}
```

### `GET /api/vendor/{vendor}/private-rfqs` - `getPrivateRfqs()`

**Purpose:** Get private RFQs sent to this vendor.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Behavior:**
1. Validates vendor ownership
2. Filters to private RFQs for this vendor
3. Applies sorting options
4. Filters by status if provided
5. Returns paginated results

**Sorting Options:**
- `newest`: Sort by created_at DESC
- `oldest`: Sort by created_at ASC
- `price_low_to_high`: Sort by budget_min ASC
- `price_high_to_low`: Sort by budget_min DESC

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
    "next_page_url": "https://api.example.com/api/vendor/1/private-rfqs?page=2",
    "prev_page_url": null
  }
}
```

### `DELETE /api/vendor/{vendor}/quotations/{quotation}/documents/{document}` - `removeDocument()`

**Purpose:** Remove a document from a quotation.

**Authorization:** Requires authenticated vendor who owns the quotation.

**Behavior:**
1. Validates document ownership
2. Delegates to `QuotationService::removeDocument()`
3. Returns success

**Response:**
```json
{
  "status": "success",
  "message": "Document removed successfully",
  "data": { /* Document */ }
}
```

## Authorization Pattern

All methods follow this authorization pattern:

```php
$user = Auth::user();
if (! $user->vendor_id || $vendor->id !== $user->vendor_id) {
    return $this->error('Only the vendor can access their quotations', [], 403);
}
```

**Helper Method:**
```php
// Uses Auth facade for authentication
// Uses JWTAuth for vendor authentication
```

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No transaction in `rejectRfq()` | MEDIUM | Partial updates on failure | Wrap in `DB::transaction()` |
| Commented code in `getPrivateRfqs()` | LOW | Code confusion | Remove or document |
| No rate limiting | LOW | Potential abuse | Add rate limiting middleware |
| No input sanitization | LOW | XSS risk | Add sanitization middleware |

## Cross-References

- [QuotationService](QuotationService.md) - Business logic for quotation operations
- [Quotation-Model](Quotation-Model.md) - Data model for quotations
- [Rfq-Model](Rfq-Model.md) - Parent RFQ for quotations
- [QuotationResource](QuotationResource.md) - API resource for serialization
- [[PrivateRfqResource]] - API resource for private RFQs

## Usage Examples

### Getting all quotations for vendor

```bash
GET /api/vendor/1/quotations
Authorization: Bearer {jwt_token}
```

### Creating a quotation

```bash
POST /api/vendor/1/quotations
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "rfq_id": 1,
  "unit_price": 50.00,
  "total_amount": 1050.00,
  "quotation_date": "2024-01-15",
  "validity_period": 30
}
```

### Updating a quotation

```bash
PUT /api/vendor/1/quotations/1
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "unit_price": 60.00,
  "total_amount": 1200.00,
  "quotation_date": "2024-01-16",
  "validity_period": 45
}
```

### Deleting a quotation

```bash
DELETE /api/vendor/1/quotations/1
Authorization: Bearer {jwt_token}
```

### Getting public RFQs

```bash
GET /api/vendor/1/public-rfqs
Authorization: Bearer {jwt_token}
```

### Getting private RFQs

```bash
GET /api/vendor/1/private-rfqs
Authorization: Bearer {jwt_token}
```

### Getting RFQ details

```bash
GET /api/vendor/1/quotations/1/rfq
Authorization: Bearer {jwt_token}
```
