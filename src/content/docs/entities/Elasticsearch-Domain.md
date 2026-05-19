---
aliases: []
tags: [laravel, backend, elasticsearch, search, auto-generated]
title: "Elasticsearch Domain"
---
# Elasticsearch Domain

## Overview

The Elasticsearch domain is the 5th most interconnected domain in the application (21 edges in the knowledge graph), handling all search functionality for products and vendors. It provides full-text search, filtering, sorting, and subscription-based boost scoring for the public catalog. The domain integrates with the Product and Vendor domains to index and search data efficiently.

## Current Architecture & Flow

### Core Components

#### Services

- **[ElasticService](/ProqDocs-Web/entities/elasticservice/)** - Core Elasticsearch service (1012 lines). Handles:
  - Index management (products, vendors, architectural/interior slot products)
  - Product and vendor indexing with boost scores
  - Public catalog search with filters, pagination, and sorting
  - Cache invalidation for search results
  - Slot-based product indexing for architectural/interior packages
  - Fallback to SQL when Elasticsearch fails

#### Controllers

- **[ElasticsearchHomeController](/ProqDocs-Web/entities/elasticsearchhomecontroller/)** - Public search endpoints (400 lines):
  - `getProducts()` - Search products with filters and sorting
  - `getVendors()` - Search vendors with filters and sorting
  - `getVendorProducts()` - Get products for a specific vendor
  - `getArchitecturalProducts()` - Get architectural slot products
  - `getInteriorProducts()` - Get interior slot products
  - `search()` - Combined search for products, vendors, and catalogues

#### Console Commands

- **[IndexSubscribedProductsToElasticsearch](/ProqDocs-Web/entities/indexsubscribedproductstoelasticsearch/)** - Index all products and vendors with subscription boost scores
- **[RebuildProjectElasticsearchIndexes](/ProqDocs-Web/entities/rebuildprojectelasticsearchindexes/)** - Rebuild all Elasticsearch indexes with environment-safe names

#### Tests

- **[ElasticsearchHomeControllerTest](/ProqDocs-Web/entities/elasticsearchhomecontrollertest/)** - Tests for Elasticsearch home controller endpoints
- **[ProductElasticsearchLifecycleTest](/ProqDocs-Web/entities/productelasticsearchlifecycletest/)** - Tests for product Elasticsearch sync lifecycle

### Index Structure

#### Products Index

```json
{
  "id": "integer",
  "name": "text",
  "slug": "keyword",
  "description": "text",
  "product_code": "keyword",
  "sku": "keyword",
  "status": "keyword",
  "brand": "text",
  "unit_price": "float",
  "unit": "keyword",
  "vat_rate": "float",
  "specifications": "object",
  "main_image": "text",
  "thumbnail": "text",
  "specification_file": "text",
  "vendor_id": "integer",
  "vendor_name": "text",
  "vendor_city": "keyword",
  "vendor_state": "keyword",
  "vendor_country": "keyword",
  "categories": "object",
  "vendor_types": "object",
  "height": "float",
  "width": "float",
  "length": "float",
  "dimension_unit": "keyword",
  "material": "text",
  "stock_availability": "keyword",
  "product_tier": "keyword",
  "origin": "keyword",
  "country_origin": "keyword",
  "warranty": "keyword",
  "delivery_time": "keyword",
  "delevary_time": "keyword",
  "created_at": "date",
  "boost_score": "integer",
  "entry_index": "integer"
}
```

#### Vendors Index

```json
{
  "id": "integer",
  "name": "text",
  "legal_name": "text",
  "email": "keyword",
  "city": "keyword",
  "state": "keyword",
  "country": "keyword",
  "logo": "text",
  "is_verified": "boolean",
  "is_active": "boolean",
  "created_at": "date",
  "categories": "object",
  "vendor_types": "object",
  "boost_score": "integer"
}
```

### Search Flow

#### Product Search

1. **Request**: `ElasticsearchHomeController::getProducts()`
   - Validates pagination parameters
   - Parses category IDs and vendor ID filters
   - Extracts search term and sort options

2. **Elasticsearch Query**: `ElasticService::searchProductsForPublicCatalog()`
   - Builds filter query for status, vendor, categories
   - Builds multi-match query for search term (name^2, vendor_name, sku, product_code)
   - Applies sorting: boost_score desc, then user-specified sort, then id asc
   - Caches page 1 results for 120 seconds (configurable)

3. **Fallback**: If Elasticsearch fails, falls back to SQL via `HomeController::getProducts()`

4. **Response**: Formats Elasticsearch results with favorite status for authenticated users

#### Vendor Search

1. **Request**: `ElasticsearchHomeController::getVendors()`
   - Validates pagination parameters
   - Parses category IDs, vendor type IDs, and location filters
   - Extracts search term and sort options

2. **Elasticsearch Query**: `ElasticService::searchVendorsForPublicCatalog()`
   - Builds filter query for is_verified, categories, vendor_types, locations
   - Builds multi-match query for search term (name^2, legal_name, email)
   - Applies sorting: boost_score desc, then user-specified sort, then id asc

3. **Fallback**: If Elasticsearch fails, falls back to SQL with default boost_score of 5

4. **Response**: Fetches full vendor details from database and applies boost scores from Elasticsearch

### Indexing Flow

#### Product Indexing

1. **Manual Indexing**: `ElasticService::indexProduct()`
   - Loads product with vendor, categories, vendor types, subscriptions
   - Calculates boost score (max 5, from subscription or default)
   - Indexes product document with all fields

2. **Sync on Changes**: `ElasticService::syncProductToIndex()`
   - Called by [ProductService](/ProqDocs-Web/entities/productservice/) on create/update
   - Loads missing relationships
   - Upserts product document

3. **Remove on Delete**: `ElasticService::removeProductFromIndex()`
   - Called by [ProductService](/ProqDocs-Web/entities/productservice/) on delete
   - Deletes product document (ignores 404)

4. **Bulk Indexing**: `ElasticService::indexAllProducts()`
   - Chunks products by 500 (configurable)
   - Indexes all products with error handling
   - Returns statistics (total, indexed, failed)

5. **Slot Indexing**: `ElasticService::rebuildSlotProductsIndex()`
   - Filters products by active subscription and package type
   - Orders by updated_at
   - Assigns entry_index for slot ordering
   - Rebuilds index from scratch

#### Vendor Indexing

1. **Manual Indexing**: `ElasticService::indexVendor()`
   - Loads vendor with user, categories, vendor types
   - Calculates boost score (max 5, from subscription or default)
   - Indexes vendor document with all fields

2. **Bulk Indexing**: `ElasticService::indexAllVendors()`
   - Chunks vendors by 500 (configurable)
   - Indexes all vendors with error handling
   - Returns statistics (total, indexed, failed)

### Cache Invalidation

- **Public Catalog Cache**: `ElasticService::invalidatePublicProductSearchCache()`
  - Increments cache version key
  - Invalidates all page 1 cached results
  - Called on product changes

### Boost Score Calculation

- **Products**: Derived from active subscription package (default 5)
- **Vendors**: Derived from vendor profile subscription (default 5)
- **Slot Products**: Based on subscription package and entry_index

## Dependencies & Graph Links

### Direct Dependencies

- **[Product](/ProqDocs-Web/entities/product/)** - Products are indexed and searched
- **Vendor** - Vendors are indexed and searched
- **[Category](/ProqDocs-Web/entities/category/)** - Used for filtering in search
- **[VendorType](/ProqDocs-Web/entities/vendortype/)** - Used for filtering in vendor search
- **[Subscription](/ProqDocs-Web/entities/subscription/)** - Provides boost scores for products and vendors
- **[Package](/ProqDocs-Web/entities/package/)** - Determines slot-based product indexing

### Cross-Domain Connections

- **[HomeController](/ProqDocs-Web/entities/homecontroller/)** - Fallback when Elasticsearch fails
- **[ProductService](/ProqDocs-Web/entities/productservice/)** - Triggers Elasticsearch sync on product changes
- **[SubscriptionSlotScoreService](/ProqDocs-Web/entities/subscriptionslotscoreservice/)** - Syncs boost scores before indexing

## Red Flags & Tech Debt

### 1. Fat Service Class (ElasticService: 1012 lines)

**Location**: `app/Service/ElasticService.php`

**Issues**:
- Single service handles index management, product indexing, vendor indexing, search, caching, and slot indexing
- Multiple responsibilities: Elasticsearch client management, index creation, document indexing, search queries, caching, fallback logic
- Difficult to test individual concerns in isolation
- High cyclomatic complexity

**Recommendation**: Split into:
- `ElasticIndexManager` - Index creation and management
- `ProductIndexer` - Product indexing operations
- `VendorIndexer` - Vendor indexing operations
- `ProductSearchService` - Product search queries
- `VendorSearchService` - Vendor search queries
- `ElasticCacheManager` - Cache invalidation

### 2. Typo in Field Name

**Location**: `app/Service/ElasticService.php:102`

**Issue**: `delevary_time` should be `delivery_time` (typo in index mapping and code).

**Recommendation**: Fix typo in index mapping and update all references.

### 3. Missing Error Handling in Indexing

**Location**: `app/Service/ElasticService.php:128-137`

**Issues**:
- Indexing errors are silently caught and counted
- No retry logic for transient failures
- No detailed error logging for failed documents

**Recommendation**: Add retry logic with exponential backoff and detailed error logging.

### 4. No Index Versioning

**Location**: `app/Service/ElasticService.php`

**Issues**:
- Index mappings are created on-the-fly without versioning
- No migration strategy for index schema changes
- Risk of data loss during index rebuilds

**Recommendation**: Implement index versioning with aliases for zero-downtime updates.

### 5. Cache Key Collision Risk

**Location**: `app/Service/ElasticService.php:499-508`

**Issues**:
- Cache key uses simple string concatenation
- No validation of cache key length
- Potential for cache key collisions with similar parameters

**Recommendation**: Use hash-based cache keys with proper validation.

### 6. Inconsistent Fallback Behavior

**Location**: `app/Http/Controllers/ElasticsearchHomeController.php:51-53, 96-113`

**Issues**:
- Product search falls back to parent controller
- Vendor search has custom fallback with default boost_score
- Inconsistent error handling between endpoints

**Recommendation**: Standardize fallback behavior across all endpoints.

### 7. No Search Result Caching Beyond Page 1

**Location**: `app/Service/ElasticService.php:497-513`

**Issues**:
- Only page 1 results are cached
- High-traffic searches on deeper pages hit Elasticsearch every time
- No cache warming for popular searches

**Recommendation**: Implement multi-page caching with cache warming for popular queries.

### 8. No Search Analytics

**Location**: Not found in code

**Issues**:
- No tracking of search terms
- No analytics for popular searches
- No monitoring for failed searches

**Recommendation**: Add search analytics tracking for optimization insights.

### 9. Duplicate Code in ElasticsearchHomeController

**Location**: `app/Http/Controllers/ElasticsearchHomeController.php:263-326, 332-347`

**Issues**:
- `formatElasticProductsForProductShow()` and `formatElasticProductsForShortResource()` have similar logic
- No abstraction for product formatting

**Recommendation**: Extract to `ElasticProductFormatter` service.

### 10. No Rate Limiting on Search Endpoints

**Location**: Not found in code

**Issues**:
- No rate limiting on search endpoints
- Vulnerable to search abuse
- Could cause Elasticsearch overload

**Recommendation**: Add rate limiting on all search endpoints.

### 11. No Search Query Validation

**Location**: `app/Http/Controllers/ElasticsearchHomeController.php:220-224`

**Issues**:
- Only basic validation on search term (min 2, max 255)
- No validation on special characters
- No protection against Elasticsearch query injection

**Recommendation**: Add comprehensive search query validation and sanitization.

### 12. No Index Health Monitoring

**Location**: Not found in code

**Issues**:
- No monitoring of index health
- No alerts for index failures
- No automatic recovery from index issues

**Recommendation**: Add index health monitoring with alerts and automatic recovery.

### 13. Incomplete Slot Indexing

**Location**: `app/Service/ElasticService.php:171-247`

**Issues**:
- Slot indexing only considers active subscriptions
- No handling of subscription expiration during slot display
- No refresh mechanism for slot products

**Recommendation**: Add subscription expiration handling and refresh mechanism.

### 14. No Bulk Delete Operations

**Location**: Not found in code

**Issues**:
- No bulk delete for products/vendors
- Individual delete operations are inefficient
- Could cause performance issues with large datasets

**Recommendation**: Add bulk delete operations with batch processing.

### 15. No Search Result Relevance Scoring

**Location**: `app/Service/ElasticService.php:402-412`

**Issues**:
- Search uses basic multi-match query
- No custom relevance scoring
- No learning from user behavior

**Recommendation**: Implement custom relevance scoring with machine learning.

## Future Upgrades (Postgres & Scalability)

...