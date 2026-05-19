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

This controller delegates business logic to [QuotationService](/ProqDocs-Web/entities/quotation-service/), following the thin controller pattern. It enforces strict authorization rules to ensure only authorized vendors can access their quotations.

## Controller Dependencies

...

## API Endpoints

### `GET /api/vendor/{vendor}/quotations` - `index()`

**Purpose:** Get all quotations for the authenticated vendor.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Behavior:**
1. Validates vendor ownership
2. Delegates to `QuotationService::getQuotationsForVendor()`
3. Returns paginated results with status counts

...

### `POST /api/vendor/{vendor}/quotations` - `store()`

**Purpose:** Create a new quotation for an RFQ.

**Authorization:** Requires authenticated vendor with valid vendor profile.

**Request Body:**
...

**Behavior:**
1. Validates vendor ownership
2. Validates RFQ deadline not passed
3. Checks for existing quotation
4. Validates public RFQ requires image
5. Delegates to `QuotationService::createQuotation()`
6. Returns created quotation with 201 status

...

### `GET /api/vendor/{vendor}/quotations/{quotation}` - `show()`

**Purpose:** Get a specific quotation with full details.

**Authorization:** Requires authenticated vendor who owns the quotation.

**Behavior:**
1. Validates vendor ownership
2. Delegates to `QuotationService::getQuotation()`
3. Returns quotation resource

...

### `PUT /api/vendor/{vendor}/quotations/{quotation}` - `update()`

**Purpose:** Update an existing quotation.

**Authorization:** Requires authenticated vendor who created the quotation.

**Request Body:**
...

**Behavior:**
1. Validates vendor ownership
2. Validates status is 'in_review'
3. Delegates to `QuotationService::updateQuotation()`
4. Returns updated quotation

...

### `DELETE /api/vendor/{vendor}/quotations/{quotation}` - `destroy()`

**Purpose:** Delete a quotation.

**Authorization:** Requires authenticated vendor who created the quotation.

**Behavior:**
1. Validates vendor ownership
2. Validates status is 'in_review'
3. Delegates to `QuotationService::deleteQuotation()`
4. Returns success

...

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

...

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

...

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No transaction in `rejectRfq()` | MEDIUM | Partial updates on failure | Wrap in `DB::transaction()` |
| Commented code in `getPrivateRfqs()` | LOW | Code confusion | Remove or document |
| No rate limiting | LOW | Potential abuse | Add rate limiting middleware |
| No input sanitization | LOW | XSS risk | Add sanitization middleware |

## Cross-References

- [QuotationService](/ProqDocs-Web/entities/quotation-service/) - Business logic for quotation operations
- [Quotation-Model](/ProqDocs-Web/entities/quotation-model/) - Data model for quotations
- [Rfq-Model](/ProqDocs-Web/entities/rfq-model/) - Parent RFQ for quotations
- [QuotationResource](/ProqDocs-Web/entities/quotation-resource/) - API resource for serialization
- PrivateRfqResource - API resource for private RFQs

...