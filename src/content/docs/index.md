---
title: "Wiki Index"
---
# Wiki Index

## Projects

- [Tech-Debt-Ledger](/ProqDocs-Web/01-projects/tech-debt-ledger/) - Master checklist of actionable bugs, raw SQL risks, missing indexes, and Postgres migration warnings

## Domains

- [Payment-Domain](/ProqDocs-Web/entities/payment-domain/) - Payment processing, SSL Commerce integration, offline payments
- [Product-Domain](/ProqDocs-Web/entities/product-domain/) - Product management, Elasticsearch indexing, Excel import/export
- [Vendor-Domain](/ProqDocs-Web/entities/vendor-domain/) - Vendor registration, verification, profile management
- [BoqEntry-BoqSheet-Domain](/ProqDocs-Web/entities/boq-entry-boq-sheet-domain/) - BOQ sheet management, dynamic columns, Excel-style merging, quotation integration
- [RFQ-Quotation-Domain](/ProqDocs-Web/entities/rfq-quotation-domain/) - Request for Quotation workflow, public/private RFQs, vendor quotation submission
- [PurchaseList-Domain](/ProqDocs-Web/entities/purchase-list-domain/) - Procurement cart management, RFQ/quotation/BOQ-based item accumulation, purchase order integration
- [PurchaseOrder-Domain](/ProqDocs-Web/entities/purchase-order-domain/) - Purchase order lifecycle management, PDF generation, payment tracking, delivery confirmation
- [Project-Domain](/ProqDocs-Web/entities/project-domain/) - Construction project management, BOQ sheet initialization, RFQ tracking
- [Delivery-Domain](/ProqDocs-Web/entities/delivery-domain/) - Shipment and delivery lifecycle management, delivery details, shipment items, financial calculations
- [Elasticsearch-Domain](/ProqDocs-Web/entities/elasticsearch-domain/) - Full-text search, filtering, sorting, subscription-based boost scoring for products and vendors

## Entities

### BOQ Domain
- [BoqSheetModel](/ProqDocs-Web/entities/boq-sheet-model/) - BOQ sheet within a project
- [BoqEntryModel](/ProqDocs-Web/entities/boq-entry-model/) - Individual line items within BOQ sheets
- [BoqSheetMergeModel](/ProqDocs-Web/entities/boq-sheet-merge-model/) - Excel-style merged cells for dynamic columns
- [BoqSheetController](/ProqDocs-Web/entities/boq-sheet-controller/) - BOQ sheet management endpoints
- [BoqEntryController](/ProqDocs-Web/entities/boq-entry-controller/) - BOQ entry management endpoints
- [BoqSheetService](/ProqDocs-Web/entities/boq-sheet-service/) - BOQ sheet business logic
- [BoqSheetEntryService](/ProqDocs-Web/entities/boq-sheet-entry-service/) - Entry operations with purchase list integration
- [BoqSheetMergeService](/ProqDocs-Web/entities/boq-sheet-merge-service/) - Cell merge management
- [BoqSheetResource](/ProqDocs-Web/entities/boq-sheet-resource/) - BOQ sheet API transformation
- [BoqEntryResource](/ProqDocs-Web/entities/boq-entry-resource/) - BOQ entry API transformation
- [BoqSheetMergeResource](/ProqDocs-Web/entities/boq-sheet-merge-resource/) - Merge API transformation

### RFQ/Quotation Domain
- [Rfq Model](/ProqDocs-Web/entities/rfq-model/) - Request for Quotation entity
- [Quotation Model](/ProqDocs-Web/entities/quotation-model/) - Vendor quotation response
- [Quotation Service Model](/ProqDocs-Web/entities/quotation-service-model/) - Quotation line items (Fixed typo)
- [RfqService](/ProqDocs-Web/entities/rfq-service/) - RFQ business logic (654 lines)
- [QuotationService](/ProqDocs-Web/entities/quotation-service/) - Quotation business logic (800 lines)
- [RfqController](/ProqDocs-Web/entities/rfq-controller/) - Buyer RFQ endpoints (613 lines)
- [QuotationController](/ProqDocs-Web/entities/quotation-controller/) - Vendor quotation endpoints (577 lines)
- [RfqResource](/ProqDocs-Web/entities/rfq-resource/) - RFQ API transformation
- [QuotationResource](/ProqDocs-Web/entities/quotation-resource/) - Quotation API transformation

## Logs

See [log.md](/ProqDocs-Web/log/) for documentation history.
