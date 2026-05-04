---
title: "Wiki Index"
---
# Wiki Index

## Projects

- [Tech-Debt-Ledger](01-Projects/Tech-Debt-Ledger.md) - Master checklist of actionable bugs, raw SQL risks, missing indexes, and Postgres migration warnings

## Domains

- [Payment-Domain](entities/Payment-Domain.md) - Payment processing, SSL Commerce integration, offline payments
- [Product-Domain](entities/Product-Domain.md) - Product management, Elasticsearch indexing, Excel import/export
- [Vendor-Domain](entities/Vendor-Domain.md) - Vendor registration, verification, profile management
- [BoqEntry-BoqSheet-Domain](entities/BoqEntry-BoqSheet-Domain.md) - BOQ sheet management, dynamic columns, Excel-style merging, quotation integration
- [RFQ-Quotation-Domain](entities/RFQ-Quotation-Domain.md) - Request for Quotation workflow, public/private RFQs, vendor quotation submission
- [PurchaseList-Domain](entities/PurchaseList-Domain.md) - Procurement cart management, RFQ/quotation/BOQ-based item accumulation, purchase order integration
- [PurchaseOrder-Domain](entities/PurchaseOrder-Domain.md) - Purchase order lifecycle management, PDF generation, payment tracking, delivery confirmation
- [Project-Domain](entities/Project-Domain.md) - Construction project management, BOQ sheet initialization, RFQ tracking
- [Delivery-Domain](entities/Delivery-Domain.md) - Shipment and delivery lifecycle management, delivery details, shipment items, financial calculations
- [Elasticsearch-Domain](entities/Elasticsearch-Domain.md) - Full-text search, filtering, sorting, subscription-based boost scoring for products and vendors

## Entities

### BOQ Domain
- [BoqSheetModel](entities/BoqSheetModel.md) - BOQ sheet within a project
- [BoqEntryModel](entities/BoqEntryModel.md) - Individual line items within BOQ sheets
- [BoqSheetMergeModel](entities/BoqSheetMergeModel.md) - Excel-style merged cells for dynamic columns
- [BoqSheetController](entities/BoqSheetController.md) - BOQ sheet management endpoints
- [BoqEntryController](entities/BoqEntryController.md) - BOQ entry management endpoints
- [BoqSheetService](entities/BoqSheetService.md) - BOQ sheet business logic
- [BoqSheetEntryService](entities/BoqSheetEntryService.md) - Entry operations with purchase list integration
- [BoqSheetMergeService](entities/BoqSheetMergeService.md) - Cell merge management
- [BoqSheetResource](entities/BoqSheetResource.md) - BOQ sheet API transformation
- [BoqEntryResource](entities/BoqEntryResource.md) - BOQ entry API transformation
- [BoqSheetMergeResource](entities/BoqSheetMergeResource.md) - Merge API transformation

### RFQ/Quotation Domain
- [Rfq Model](entities/Rfq Model.md) - Request for Quotation entity
- [Quotation Model](entities/Quotation Model.md) - Vendor quotation response
- [QutationService Model](entities/QutationService Model.md) - Quotation line items (note: typo in class name)
- [RfqService](entities/RfqService.md) - RFQ business logic (654 lines)
- [QuotationService](entities/QuotationService.md) - Quotation business logic (800 lines)
- [RfqController](entities/RfqController.md) - Buyer RFQ endpoints (613 lines)
- [QuotationController](entities/QuotationController.md) - Vendor quotation endpoints (577 lines)
- [RfqResource](entities/RfqResource.md) - RFQ API transformation
- [QuotationResource](entities/QuotationResource.md) - Quotation API transformation

## Logs

See [log.md](log.md) for documentation history.
