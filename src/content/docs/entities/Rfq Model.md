---
aliases: [Rfq]
tags: [laravel, backend, auto-generated, model, rfq]
title: "Rfq Model"
---

# Rfq Model

Request for Quotation entity. It represents a buyer's request for products or services, which can be either public (visible to all vendors) or private (targeted at a specific vendor).

## Current Architecture & Flow

- **Table**: `rfqs`
- **Types**: `public` (open market) and `private` (direct negotiation).
- **Primary Relationships**:
	- `belongsTo` [[Buyer Model]]
	- `belongsTo` [[Project Model]]
	- `belongsTo` [[Product Model]] (optional, for private RFQs)
	- `hasMany` [Quotation Model](Quotation Model.md)
	- `morphMany` [[Document Model]]
- **Lifecycle Statuses**: `pending`, `active`, `closed`, `cancelled`, `accepted`.

## Dependencies & Graph Links

- [RfqService](RfqService.md) - Manages RFQ creation, updates, and filtering.
- [RfqController](RfqController.md) - API endpoints for buyers.
- [[PrivateRfqCreatedNotification]] - Notifies vendors of private requests.

## Red Flags & Tech Debt

- **Manual File Cleanup**: The `deleteRfq` method in [RfqService](RfqService.md) manually iterates through documents and deletes physical files from storage. This should ideally be handled by model observers or a dedicated media library.
- **UUID Generation**: Uses `Str::uuid()` in a loop to ensure uniqueness for `rfq_code`. While safe, it's performed in PHP rather than via DB constraints.

## Future Upgrades (Postgres & Scalability)

- **Elasticsearch Integration**: Public RFQs should be indexed in [Elasticsearch-Domain](Elasticsearch-Domain.md) for better vendor searchability.
- **State Machine**: Implement a proper state machine for status transitions to prevent invalid status hops.
