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

- **[Vendor](./Vendor-Domain.md)** - Products belong to vendors
- **Category** - Products have many-to-many relationship with categories
- **Unit** - Products have a unit (kg, pcs, box, etc.)
- **Subscription** - Products can be featured in subscription slots
- **Elasticsearch** - Products are indexed for search

### Cross-Domain Connections

- **Document** - Polymorphic relationship for product documents
- **User** - Favorites and comparisons are user-specific
- **Notification** - Product upload completion notifications


## Red Flags & Tech Debt

### 1. Fat Service Classes

**Location**: `ProductService.php` (1090 lines), `ElasticService.php` (1012 lines)

**Issues**:
- `ProductService` handles CRUD, file uploads, validation, Excel import, and Elasticsearch sync
- `ElasticService` handles both products and vendors, search, indexing, and caching
- Difficult to test individual concerns
- High cyclomatic complexity

**Recommendation**: Split into:
- `ProductService` - Core CRUD operations
- `ProductFileService` - File upload and thumbnail generation
- `ProductImportService` - Excel import logic
- `ElasticProductService` - Product-specific Elasticsearch operations
- `ElasticVendorService` - Vendor-specific Elasticsearch operations

### 2. Duplicate Code in ProductController

**Location**: `Vendor/ProductController.php:471-502`

**Issues**:
- `setArchive()`, `setDraft()`, `setActive()` have nearly identical logic
- All check vendor ownership and call model methods

```php
// Repeated 3 times with minor variations
if ($product->vendor_id !== $vendor->id) {
    throw new ModelNotFoundException('Product not found for this vendor');
}
$product->setArchive(); // or setDraft() or setActive()
```

**Recommendation**: Extract to `ProductService::setStatus($vendor, $product, $status)` method.

### 3. Inconsistent Status Handling

**Location**: `ProductService.php:244-254`

**Issues**:
- Status mapping logic is duplicated in create and update
- Uses string comparison instead of enum
- Status enum values don't match flag names

```php
if ($validated['status'] === 'active') {
    $validated['status'] = 'active';
    $validated['is_published'] = true;
    $validated['is_draft'] = false;
} else { // draft
    $validated['status'] = 'draft';
    $validated['is_published'] = false;
    $validated['is_draft'] = true;
}
```

**Recommendation**: Create `ProductStatus` enum with `toFlags()` method.

### 4. Missing Database Indexes

**Location**: Migration file

**Issues**:
- No indexes on frequently queried fields
- `vendor_id`, `status`, `slug`, `sku` lack indexes
- Will cause slow queries as data grows

**Migration**: `2025_10_09_114049_create_products_table.php`

**Recommendation**: Add indexes:
```sql
CREATE INDEX idx_products_vendor_id ON products(vendor_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_composite ON products(vendor_id, status);
```

### 5. Race Condition in Slug Generation

**Location**: `ProductService.php:456-469`

**Issues**:
- `generateUniqueSlug()` uses `withTrashed()->exists()` without locking
- Concurrent requests could create duplicate slugs
- No retry mechanism for collision

**Recommendation**: Use database unique constraint with retry logic.

### 6. Excel Import Image Extraction Complexity

**Location**: `ProductImport.php:92-167`

**Issues**:
- Complex image extraction logic for Excel cells
- Handles both Drawing and MemoryDrawing
- No validation on image size during import
- Could cause memory issues with large Excel files

**Recommendation**:
- Add image size validation
- Process images in chunks
- Add progress reporting for large imports

### 7. Chunked Upload Security

**Location**: `ProductService.php:794-1021`

**Issues**:
- No cleanup of orphaned upload sessions
- No timeout for upload sessions
- No validation of total file size against declared size
- Could be abused for storage exhaustion

**Recommendation**:
- Add session timeout (e.g., 1 hour)
- Add cleanup job for orphaned sessions
- Validate actual file size matches declared size

### 8. Elasticsearch Search Fallback Not Implemented

**Location**: `ElasticService.php:544-551`

**Issues**:
- `searchProductsForPublicCatalog()` returns `null` on failure
- Caller must handle fallback to SQL
- No indication in response that search failed
- Could silently return no results

**Recommendation**:
- Implement automatic fallback to SQL search
- Add `search_fallback_used` flag in response
- Log failures for monitoring

### 9. Cache Incomplete

**Location**: `ElasticService.php:495-513`

**Issues**:
- Only page 1 is cached
- No cache invalidation on product updates
- Cache version increment could overflow
- No cache warming for popular searches

**Recommendation**:
- Cache top 5 pages
- Invalidate cache on product CRUD
- Use UUID for cache version instead of increment

### 10. Typo in Field Name

**Location**: `2025_10_09_114049_create_products_table.php:33`

**Issue**: `delevary_min_day` and `delevary_max_day` should be `delivery_min_day` and `delivery_max_day`.

Also in `ElasticService.php:102` - `delevary_time` should be `delivery_time`.

### 11. Commented Out Code

**Location**: Multiple files

**Issues**:
- `ProductService.php:270-280` - Commented out document upload loop
- `ProductImport.php:636` - Commented out vendor_id check
- Migration files have commented out fields

**Recommendation**: Remove or properly document why code is commented.

### 12. No File Size Validation on Update

**Location**: `ProductService.php:318-397`

**Issues**:
- Update doesn't validate file sizes
- Could upload larger files than allowed
- No validation on base64 file size

**Recommendation**: Add file size validation in update method.

### 13. Thumbnail Generation Error Suppression

**Location**: `ProductService.php:643-660`

**Issues**:
- Error reporting suppressed for libpng warnings
- Could hide real image processing errors
- Uses `ob_start()`/`ob_end_clean()` which is fragile

**Recommendation**:
- Log warnings instead of suppressing
- Use proper error handling
- Consider using a dedicated image processing service

### 14. Product Resource N+1 Query

**Location**: `ProductResource.php:18-28`

**Issues**:
- Checks `Auth::check()` and loads `favoriteProducts` for every product
- Could cause N+1 queries in product lists
- No eager loading of favorite status

**Recommendation**:
- Use eager loading with `with(['favoriteProducts' => function($q) { $q->where('user_id', Auth::id()); }])`
- Or use a separate endpoint for favorite status

## Future Upgrades (Postgres & Scalability)

### Database Schema Improvements

1. **Add Indexes**:
   ```sql
   CREATE INDEX idx_products_vendor_id ON products(vendor_id);
   CREATE INDEX idx_products_status ON products(status);
   CREATE INDEX idx_products_slug ON products(slug);
   CREATE INDEX idx_products_sku ON products(sku);
   CREATE INDEX idx_products_composite ON products(vendor_id, status);
   CREATE INDEX idx_products_created_at ON products(created_at DESC);
   CREATE INDEX idx_products_unit_price ON products(unit_price);
   ```

2. **Fix Typos**:
   ```sql
   ALTER TABLE products RENAME COLUMN delevary_min_day TO delivery_min_day;
   ALTER TABLE products RENAME COLUMN delevary_max_day TO delivery_max_day;
   ```

3. **Add Constraints**:
   ```sql
   ALTER TABLE products
   ADD CONSTRAINT check_unit_price_non_negative
   CHECK (unit_price >= 0);

   ALTER TABLE products
   ADD CONSTRAINT check_vat_rate_range
   CHECK (vat_rate >= 0 AND vat_rate <= 100);
   ```

4. **Use Postgres JSONB**:
   - Change `specifications` from JSON to JSONB for better query performance

5. **Add Full-Text Search**:
   ```sql
   CREATE INDEX idx_products_name_fts ON products USING gin(to_tsvector('english', name));
   CREATE INDEX idx_products_description_fts ON products USING gin(to_tsvector('english', description));
   ```

### Architecture Improvements

1. **Event-Driven Architecture**:
   - Dispatch events on product CRUD instead of direct Elasticsearch calls
   - Allow multiple listeners (cache invalidation, analytics, notifications)

2. **Queue Elasticsearch Operations**:
   - Move Elasticsearch sync to background queue
   - Prevent slow responses on product CRUD
   - Implement retry logic for failed operations

3. **File Storage Abstraction**:
   - Create `FileStorageInterface` for multiple storage backends
   - Support S3, Azure Blob, local storage
   - Implement CDN integration

4. **Image Processing Service**:
   - Extract image processing to dedicated service
   - Support multiple image formats and sizes
   - Implement lazy thumbnail generation

5. **Import Job Improvements**:
   - Add progress reporting via WebSocket
   - Implement partial import with error recovery
   - Add validation preview before import

### Performance Optimizations

1. **Caching**:
   - Cache product details for read-heavy endpoints
   - Cache category lists for product forms
   - Implement cache warming for popular products

2. **Batch Processing**:
   - Batch Elasticsearch index operations
   - Batch favorite/comparison status checks
   - Batch category queries

3. **Read Replicas**:
   - Route product listing queries to read replicas
   - Keep write operations on primary

4. **Pagination Optimization**:
   - Use cursor-based pagination for large datasets
   - Implement keyset pagination for better performance

### Security Improvements

1. **File Upload Security**:
   - Validate file contents, not just extensions
   - Scan uploaded files for malware
   - Implement file size quotas per vendor

2. **Rate Limiting**:
   - Rate limit product creation endpoints
   - Rate limit Excel import endpoints
   - Prevent abuse

3. **Access Control**:
   - Implement row-level security for multi-tenant access
   - Add audit logging for product modifications
   - Implement data retention policies

### Monitoring Improvements

1. **Metrics**:
   - Track product CRUD operations
   - Monitor Elasticsearch sync failures
   - Track import job success/failure rates

2. **Alerting**:
   - Alert on high error rates
   - Alert on Elasticsearch cluster issues
   - Alert on storage exhaustion

3. **Logging**:
   - Structured logging for all operations
   - Correlation IDs for request tracing
   - Performance logging for slow queries

## Related Files

### Models
- `app/Models/Product.php`
- `app/Models/ProductVariation.php`
- `app/Models/ProductFavorite.php`
- `app/Models/ProductComparison.php`
- `app/Models/SlideImage.php`
- `app/Models/Document.php`

### Services
- `app/Service/ProductService.php`
- `app/Service/ElasticService.php`
- `app/Service/ProductFavoriteComparisonService.php`

### Controllers
- `app/Http/Controllers/Vendor/ProductController.php`
- `app/Http/Controllers/Buyer/ProductFavoriteComparisonController.php`

### Resources
- `app/Http/Resources/ProductResource.php`
- `app/Http/Resources/ShortProductResource.php`
- `app/Http/Resources/ProductShow.php`

### Jobs
- `app/Jobs/ImportProductsJob.php`

### Imports/Exports
- `app/Imports/ProductImport.php`
- `app/Exports/ProductTemplateExport.php`

### Migrations
- `database/migrations/2025_10_09_114049_create_products_table.php`
- `database/migrations/2025_10_09_114057_create_product_variations_table.php`
- `database/migrations/2026_03_30_000001_create_product_favorites_table.php`
- `database/migrations/2026_03_30_000002_create_product_comparisons_table.php`
- `database/migrations/2026_02_10_000000_add_delivery_stock_origin_columns_to_products_table.php`
- `database/migrations/2026_04_28_131822_add_boost_score_to_products.php`
- `database/migrations/2026_01_18_111322_add_search_indexes_to_products_vendors_catalogues.php`
