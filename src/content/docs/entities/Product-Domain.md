---
aliases: []
tags: [laravel, backend, auto-generated]
title: "Product Domain"
---
# Product Domain

## Overview

The Product domain is the second most interconnected domain in the application (26 edges in the knowledge graph), handling all product management for vendors including CRUD operations, Elasticsearch indexing, Excel import/export, and product favorites/comparisons for buyers.

## Current Architecture & Flow

### Core Components

#### Models

- **Product** - Core product model with soft deletes, status flags (active/draft/archived), and relationships to vendor, categories, variations, documents, and slide images.
- **ProductVariation** - Product variations (colors, sizes, etc.).
- **ProductFavorite** - User's favorite products.
- **ProductComparison** - User's product comparison list (max 3 products).
- **SlideImage** - Product gallery/slide images.
- **Document** - Product documents (PDFs, CAD files, etc.) via polymorphic relationship.

#### Services

- **ProductService** - Core product management service (1090 lines). Handles:
  - Product CRUD operations
  - File uploads (main image, specification file, slide images, documents)
  - Thumbnail generation using Intervention Image
  - Base64 file decoding
  - Chunked Excel upload for bulk import
  - Product status management (active/draft/archived)
  - Elasticsearch synchronization

- **ElasticService** - Elasticsearch integration (1012 lines). Handles:
  - Product indexing and search
  - Vendor indexing and search
  - Boost score management for subscription-based ranking
  - Cache invalidation for public catalog
  - Slot-based product indexing for architectural/interior subscriptions

- **ProductFavoriteComparisonService** - Buyer favorites and comparison management (98 lines).

#### Controllers

- **Vendor/ProductController** - Vendor-facing product endpoints (587 lines):
  - `index()` - List products with filtering and search
  - `store()` - Create new product
  - `show()` - Get specific product
  - `update()` - Update product
  - `destroy()` - Delete product (soft delete)
  - `setArchive()`, `setDraft()`, `setActive()` - Status management
  - `removeImage()`, `removeSpecificationFile()`, `removeDocument()` - File removal
  - `importProducts()`, `uploadImportChunk()` - Chunked Excel import
  - `downloadImportTemplate()` - Download Excel template
  - `checkUniqueSKU()` - Validate SKU uniqueness

- **Buyer/ProductFavoriteComparisonController** - Buyer favorites and comparison endpoints (91 lines).

#### Resources

- **ProductResource** - Full product details with vendor, categories, documents, and favorite status.
- **ShortProductResource** - Minimal product representation.
- **ProductShow** - Product display resource.

#### Jobs

- **ImportProductsJob** - Background job for Excel product import.

#### Imports/Exports

- **ProductImport** - Excel import with image extraction from cells (739 lines).
- **ProductTemplateExport** - Excel template export.


### Product Flow

#### Product Creation

1. **Validation**: `ProductService::validator()` validates all fields including:
   - Required fields: name, unit, status, vat_rate
   - Optional fields: product_code, sku, description, dimensions, material
   - File uploads: main_image, specification_file, slide_images, documents

2. **File Processing**: `ProductService::handleFileUploads()` handles:
   - Regular file uploads via `UploadedFile`
   - Base64 encoded files (data URLs or plain base64)
   - Thumbnail generation from main image
   - Slide image array processing

3. **Database Creation**:
   - Generates unique slug
   - Maps status to flags (is_published, is_draft, is_archived)
   - Creates product record
   - Syncs categories
   - Creates slide images
   - Creates documents

4. **Elasticsearch Sync**: `ElasticService::syncProductToIndex()` indexes product for search.

#### Product Update

Similar to creation but:
- Deletes old files when new ones uploaded
- Updates existing records instead of creating
- Re-syncs to Elasticsearch

#### Product Deletion

- Soft deletes product
- Removes from Elasticsearch
- Cleans up favorites and comparisons
- Sets SKU to null to free up for reuse

#### Excel Import

1. **Chunked Upload**:
   - `initChunkedUploadExcel()` - Creates upload session with UUID
   - `uploadChunkExcel()` - Uploads individual chunks (5MB max)
   - Auto-finalizes when all chunks received
   - `finalizeChunkedUploadExcel()` - Combines chunks and queues import job

2. **Import Processing** (`ImportProductsJob`):
   - Extracts images from Excel cells (Drawing and MemoryDrawing)
   - Validates each row
   - Creates or updates products by SKU
   - Syncs to Elasticsearch
   - Returns success/failure counts

#### Elasticsearch Integration

1. **Indexing**:
   - `indexProduct()` - Indexes single product with boost score
   - `indexAllProducts()` - Bulk indexes all products
   - `rebuildAllProductsIndex()` - Deletes and recreates index

2. **Search**:
   - `searchProductsForPublicCatalog()` - Public catalog search with:
     - Multi-field search (name^2, vendor_name, sku, product_code)
     - Category filtering
     - Vendor filtering
     - Sorting by boost_score, created_at, unit_price
     - Page 1 caching (120s TTL)

3. **Boost Score**:
   - Default: 5
   - Subscription-based ranking applied via `resolveBoostScore`
   - Used for primary sort in search results

### Status Management

Products have three status states with corresponding flags:

| Status | is_published | is_draft | is_archived |
|--------|--------------|----------|--------------|
| active | true | false | false |
| draft | false | true | false |
| archived | true | false | true |

Model methods: `scopeSetActive()`, `scopeSetDraft()`, `scopeSetArchive()`

## Dependencies & Graph Links

### Direct Dependencies

- **[Vendor](/ProqDocs-Web/entities/vendor-domain/)** - Products belong to vendors
- **Category** - Products have many-to-many relationship with categories
- **Unit** - Products have a unit (kg, pcs, box, etc.)
- **Subscription** - Products can be featured in subscription slots
- **Elasticsearch** - Products are indexed for search

### Cross-Domain Connections

- **Document** - Polymorphic relationship for product documents
- **User** - Favorites and comparisons are user-specific
- **Notification** - Product upload completion notifications


## Red Flags & Tech Debt

...