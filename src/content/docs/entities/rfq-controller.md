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

This controller delegates business logic to [RfqService](/ProqDocs-Web/entities/rfq-service/), following the thin controller pattern. It enforces strict authorization rules to ensure only authorized buyers can access their RFQs.

## Controller Dependencies

...

## API Endpoints

### `GET /api/buyer/rfqs` - `index()`

**Purpose:** Get all RFQs for the authenticated buyer.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::getRfqsForBuyer()`
3. Returns paginated results with status counts

...

### `POST /api/buyer/rfqs` - `store()`

**Purpose:** Create a new RFQ.

**Authorization:** Requires authenticated buyer with valid buyer profile.

...

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::createRfq()`
3. Returns created RFQ with 201 status

...

### `GET /api/buyer/rfqs/{rfq}` - `show()`

**Purpose:** Get a specific RFQ with full details.

**Authorization:** Requires authenticated buyer with ownership or public access.

**Behavior:**
1. Validates buyer ownership or public access
2. Delegates to `RfqService::getRfq()`
3. Returns RFQ resource

...

### `PUT /api/buyer/rfqs/{rfq}` - `update()`

**Purpose:** Update an existing RFQ.

**Authorization:** Requires authenticated buyer who created the RFQ.

...

**Behavior:**
1. Validates buyer ownership
2. Validates status is not terminal
3. Validates type is not private
4. Delegates to `RfqService::updateRfq()`
5. Returns updated RFQ

...

### `DELETE /api/buyer/rfqs/{rfq}` - `destroy()`

**Purpose:** Delete an RFQ.

**Authorization:** Requires authenticated buyer who created the RFQ.

**Behavior:**
1. Validates buyer ownership
2. Delegates to `RfqService::deleteRfq()`
3. Returns success

...

### `GET /api/public-rfqs` - `getPublicRfqsForBuyer()`

**Purpose:** Get public RFQs for a buyer.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::getPublicRfqsForBuyer()`
3. Returns paginated results

...

### `GET /api/buyer/rfqs/private` - `getPrivateRfqs()`

**Purpose:** Get private RFQs for a buyer.

**Authorization:** Requires authenticated buyer with valid buyer profile.

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::getPrivateRfqsForBuyer()`
3. Returns paginated results

...

### `POST /api/buyer/rfqs/private` - `createPrivateRfq()`

**Purpose:** Create a private RFQ for a specific vendor.

**Authorization:** Requires authenticated buyer with valid buyer profile.

...

**Behavior:**
1. Validates buyer profile exists
2. Delegates to `RfqService::createPrivateRfq()`
3. Returns created RFQ with notification to vendor

...

### `POST /api/buyer/rfqs/{rfq}/reject` - `rejectRfq()`

**Purpose:** Reject an RFQ and all its quotations.

**Authorization:** Requires authenticated buyer who owns the RFQ.

**Behavior:**
1. **Uses transaction** for data consistency
2. Validates buyer ownership
3. Sets RFQ status to 'rejected'
4. Rejects all associated quotations
5. Returns success

...

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

- [RfqService](/ProqDocs-Web/entities/rfq-service/) - Business logic for RFQ operations
- [Rfq-Model](/ProqDocs-Web/entities/rfq-model/) - Data model for RFQs
- [Quotation-Model](/ProqDocs-Web/entities/quotation-model/) - Vendor responses to RFQs
- [RfqResource](/ProqDocs-Web/entities/rfq-resource/) - API resource for serialization
- PrivateRfqResource - API resource for private RFQs

...