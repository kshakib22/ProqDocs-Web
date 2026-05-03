---
title: "Wiki Index"
---

## Projects

- [Tech-Debt-Ledger](./01-projects/tech-debt-ledger/) - Master checklist of actionable bugs, raw SQL risks, missing indexes, and Postgres migration warnings

## Domains

- [Payment-Domain](./entities/payment-domain/) - Payment processing, SSL Commerce integration, offline payments
- [Product-Domain](./entities/product-domain/) - Product management, Elasticsearch indexing, Excel import/export
- [Vendor-Domain](./entities/vendor-domain/) - Vendor registration, verification, profile management
- [BoqEntry-BoqSheet-Domain](./entities/boqentry-boqsheet-domain/) - BOQ sheet management, dynamic columns, Excel-style merging, quotation integration
- [RFQ-Quotation-Domain](./entities/rfq-quotation-domain/) - Request for Quotation workflow, public/private RFQs, vendor quotation submission
- [PurchaseList-Domain](./entities/purchaselist-domain/) - Procurement cart management, RFQ/quotation/BOQ-based item accumulation, purchase order integration
- [PurchaseOrder-Domain](./entities/purchaseorder-domain/) - Purchase order lifecycle management, PDF generation, payment tracking, delivery confirmation
- [Project-Domain](./entities/project-domain/) - Construction project management, BOQ sheet initialization, RFQ tracking
- [Delivery-Domain](./entities/delivery-domain/) - Shipment and delivery lifecycle management, delivery details, shipment items, financial calculations
- [Elasticsearch-Domain](./entities/elasticsearch-domain/) - Full-text search, filtering, sorting, subscription-based boost scoring for products and vendors

## Entities

### BOQ Domain
- [BoqSheet Model](./entities/boqsheet-model/) - BOQ sheet within a project
- [BoqEntry Model](./entities/boqentry-model/) - Individual line items within BOQ sheets
- [BoqSheetMerge Model](./entities/boqsheetmerge-model/) - Excel-style merged cells for dynamic columns
- [BoqSheetController](./entities/boqsheetcontroller/) - BOQ sheet management endpoints
- [BoqEntryController](./entities/boqentrycontroller/) - BOQ entry management endpoints
- [BoqSheetService](./entities/boqsheetservice/) - BOQ sheet business logic
- [BoqSheetEntryService](./entities/boqsheetentryservice/) - Entry operations with purchase list integration
- [BoqSheetMergeService](./entities/boqsheetmergeservice/) - Cell merge management
- [BoqSheetResource](./entities/boqsheetresource/) - BOQ sheet API transformation
- [BoqEntryResource](./entities/boqentryresource/) - BOQ entry API transformation
- [BoqSheetMergeResource](./entities/boqsheetmergeresource/) - Merge API transformation

### RFQ/Quotation Domain
- [Rfq Model](./entities/rfq-model/) - Request for Quotation entity
- [Quotation Model](./entities/quotation-model/) - Vendor quotation response
- [QuotationService Model](./entities/qutationservice-model/) - Quotation line items (note: typo in class name)
- [RfqService](./entities/rfqservice/) - RFQ business logic (654 lines)
- [QuotationService](./entities/quotationservice/) - Quotation business logic (800 lines)
- [RfqController](./entities/rfqcontroller/) - Buyer RFQ endpoints (613 lines)
- [QuotationController](./entities/quotationcontroller/) - Vendor quotation endpoints (577 lines)
- [RfqResource](./entities/rfqresource/) - RFQ API transformation
- [QuotationResource](./entities/quotationresource/) - Quotation API transformation

## Logs

See [Logs](./log/) for documentation history.
