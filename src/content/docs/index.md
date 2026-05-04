# Wiki Index

## Projects

- [[Tech-Debt-Ledger]] - Master checklist of actionable bugs, raw SQL risks, missing indexes, and Postgres migration warnings

## Domains

- [[Payment-Domain]] - Payment processing, SSL Commerce integration, offline payments
- [[Product-Domain]] - Product management, Elasticsearch indexing, Excel import/export
- [[Vendor-Domain]] - Vendor registration, verification, profile management
- [[BoqEntry-BoqSheet-Domain]] - BOQ sheet management, dynamic columns, Excel-style merging, quotation integration
- [[RFQ-Quotation-Domain]] - Request for Quotation workflow, public/private RFQs, vendor quotation submission
- [[PurchaseList-Domain]] - Procurement cart management, RFQ/quotation/BOQ-based item accumulation, purchase order integration
- [[PurchaseOrder-Domain]] - Purchase order lifecycle management, PDF generation, payment tracking, delivery confirmation
- [[Project-Domain]] - Construction project management, BOQ sheet initialization, RFQ tracking
- [[Delivery-Domain]] - Shipment and delivery lifecycle management, delivery details, shipment items, financial calculations
- [[Elasticsearch-Domain]] - Full-text search, filtering, sorting, subscription-based boost scoring for products and vendors

## Entities

### BOQ Domain
- [[BoqSheetModel]] - BOQ sheet within a project
- [[BoqEntryModel]] - Individual line items within BOQ sheets
- [[BoqSheetMergeModel]] - Excel-style merged cells for dynamic columns
- [[BoqSheetController]] - BOQ sheet management endpoints
- [[BoqEntryController]] - BOQ entry management endpoints
- [[BoqSheetService]] - BOQ sheet business logic
- [[BoqSheetEntryService]] - Entry operations with purchase list integration
- [[BoqSheetMergeService]] - Cell merge management
- [[BoqSheetResource]] - BOQ sheet API transformation
- [[BoqEntryResource]] - BOQ entry API transformation
- [[BoqSheetMergeResource]] - Merge API transformation

### RFQ/Quotation Domain
- [[Rfq Model]] - Request for Quotation entity
- [[Quotation Model]] - Vendor quotation response
- [[QutationService Model]] - Quotation line items (note: typo in class name)
- [[RfqService]] - RFQ business logic (654 lines)
- [[QuotationService]] - Quotation business logic (800 lines)
- [[RfqController]] - Buyer RFQ endpoints (613 lines)
- [[QuotationController]] - Vendor quotation endpoints (577 lines)
- [[RfqResource]] - RFQ API transformation
- [[QuotationResource]] - Quotation API transformation

## Logs

See [[log.md]] for documentation history.
