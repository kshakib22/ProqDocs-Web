---
name: Rfq-Model
description: Laravel Eloquent model for RFQ (Request for Quotation) - the central entity in the procurement workflow
type: entity
title: "Rfq Model"
---

# Rfq Model

## Architectural Purpose

`Rfq` (Request for Quotation) is the central entity in the procurement workflow. It represents a buyer's request for product quotes from vendors, serving as the foundation for the entire quotation and purchasing process. This model is the starting point for:

- **Vendor engagement**: Public and private RFQs for soliciting quotes
- **Price discovery**: Establishing market rates through competitive bidding
- **Procurement tracking**: Managing the lifecycle from request to purchase
- **Budget management**: Setting price range expectations
- **Project coordination**: Linking RFQs to specific projects and categories

## Database Schema

...

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| No check constraint on `dead_line_date` | MEDIUM | Invalid dates possible | Add `CHECK (dead_line_date >= created_at)` |
| No unique constraint on `rfq_code` | MEDIUM | Duplicate codes possible | Add unique index |
| No FK cascade for soft-deleted records | MEDIUM | Orphaned data | Add cascade handling |
| No status transition validation | LOW | Invalid state transitions | Add validation rules |
| Naming inconsistency with quantity | LOW | Confusion | Standardize on `quantity` |

## Cross-References

- [Quotation-Model](/entities/quotation-model) - Vendor responses to this RFQ
- [RfqService](/entities/rfqservice) - Business logic for RFQ operations
- [RfqController](/entities/rfqcontroller) - HTTP endpoint handler
- [RfqResource](/entities/rfqresource) - API resource for serialization
- PurchaseList - Downstream purchase order

...
