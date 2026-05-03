---
aliases: []
tags: [laravel, backend, auto-generated]
title: "Vendor Domain"
---
# Vendor Domain

## Overview

The Vendor domain is the third most interconnected domain in the application (22 edges in the knowledge graph), handling vendor registration, verification, profile management, and vendor-specific operations including products, quotations, RFQs, and purchase orders.

## Current Architecture & Flow

### Core Components

#### Models

- **[Vendor](Vendor.md)** - Core vendor model with soft deletes, verification status, profile completion tracking, and relationships to user, products, categories, vendor types, certificates, contacts, reviews, RFQs, quotations, catalogues, and purchase orders.
- **[VendorType](VendorType.md)** - Vendor types (e.g., Manufacturer, Distributor, Wholesaler).
- **[FavoriteVendor](FavoriteVendor.md)** - Buyer's favorite vendors.

#### Controllers

- **[Admin/VendorController](Admin/VendorController.md)** - Admin-facing vendor management (203 lines):
  - `index()` - List vendors with filtering and search
  - `approveVendor()` - Approve vendor registration
  - `rejectVendor()` - Reject vendor registration with reason
  - `show()` - Get vendor details

- **[Vendor/VendorDashBoardController](Vendor/VendorDashBoardController.md)** - Vendor dashboard (93 lines):
  - `__invoke()` - Get vendor dashboard with RFQ counts, product counts, quotations

#### Resources

- **[VendorResource](VendorResource.md)** - Full vendor details for admin listing.
- **[VendorProfileResource](VendorProfileResource.md)** - Detailed vendor profile with scores and documents.
- **[PublicVendorResource](PublicVendorResource.md)** - Public vendor profile (similar to profile but without sensitive data).
- **[NewVendorResource](NewVendorResource.md)** - Minimal vendor resource for new registrations.
- **[ShortVendorResource](ShortVendorResource.md)** - Minimal vendor representation (id, name, logo).
- **[FavoriteVendorResource](FavoriteVendorResource.md)** - Favorite vendor with purchase order summary.

#### Policies

- **[VendorProfilePolicy](VendorProfilePolicy.md)** - Vendor profile access control (93 lines):
  - `create()`, `update()`, `view()` - Vendor can only access their own profile
  - `updateContacts()`, `updateCertificates()`, `updateTypesAndCategories()` - Section-specific updates
  - `deleteContact()`, `deleteCertificates()` - Delete permissions

#### Middleware

- **[VendorVerified](VendorVerified.md)** - Middleware to ensure vendor is verified and not rejected.

#### Notifications

- **[VendorApproveNotification](VendorApproveNotification.md)** - Sent to vendor on approval (mail + database).
- **[VendorRejectedNotification](VendorRejectedNotification.md)** - Sent to vendor on rejection (mail + database).
- **[VendorRegistrationNotification](VendorRegistrationNotification.md)** - Sent to vendor on registration (mail + database).
- **[AdminVendorApprovedNotification](AdminVendorApprovedNotification.md)** - Sent to admins on vendor approval (database only).
- **[AdminVendorRejectedNotification](AdminVendorRejectedNotification.md)** - Sent to admins on vendor rejection (database only).
- **[AdminVendorRegistrationNotification](AdminVendorRegistrationNotification.md)** - Sent to admins on new vendor registration (database only).

#### Mail

- **[VendorWelcome](VendorWelcome.md)** - Welcome email for new vendor registration.
- **[VendorVerified](VendorVerified.md)** - Verification email for approved vendors.

### Vendor Flow

#### Vendor Registration

1. **Registration**: User creates vendor profile with:
   - Company info (name, legal name, logo, description, established year, address, website)
   - Tax documents (TIN, BIN, trade license, NID)
   - Business profile (vendor types, categories)
   - Contact details
   - Certificates

2. **Initial Status**: Vendor created with:
   - `is_verified = false`
   - `is_rejected = false`
   - Status: "pending"

3. **Notification**: `VendorRegistrationNotification` sent to user and admins.

#### Vendor Verification

1. **Admin Review**: Admin reviews vendor profile via `Admin/VendorController::show()`

2. **Approval** (`approveVendor()`):
   - Sets `is_verified = true`, `is_rejected = false`
   - Sends `VendorApproveNotification` to vendor (mail + database)
   - Sends `AdminVendorApprovedNotification` to all admins (database)

3. **Rejection** (`rejectVendor()`):
   - Sets `is_verified = false`, `is_rejected = true`
   - Stores `reject_reason`
   - Sends `VendorRejectedNotification` to vendor (mail + database)
   - Sends `AdminVendorRejectedNotification` to all admins (database)

#### Profile Completion

Vendor model calculates profile completion scores via appends:

- **`profile_complete`** (0-100): Overall completion score
  - TIN number: 10%
  - License number: 10%
  - Address: 10%
  - City: 10%
  - Logo: 20%
  - Vendor types: 10%
  - Categories: 10%
  - Contacts: 10%
  - Certificates: 10%

- **`company_info_complete`** (boolean): Company info section complete (≥40%)
- **`business_profile_complete`** (boolean): Business profile section complete (≥20%)
- **`contacts_complete`** (boolean): Contacts section complete (≥10%)
- **`certificates_complete`** (boolean): Certificates section complete (≥10%)

#### Vendor Dashboard

`VendorDashBoardController::__invoke()` provides:

- **Dashboard Matrix**:
  - RFQ count
  - Active products count
  - Response time (hardcoded: "2.3 hours")
  - Quotations submitted count
  - Product views (hardcoded: 1247)
  - Buyer enquiries (hardcoded: 24)
  - Win rate (hardcoded: 25)
  - Profile score

- **RFQ Lists**:
  - Submitted private RFQs (last 5)
  - Submitted public RFQs (where vendor has quotations)
  - Unsubmitted public RFQs (where vendor hasn't quoted)

#### Vendor Relationships

- **Products**: `hasMany(Product::class)` - Vendor's products
- **Categories**: `belongsToMany(Category::class)` - Vendor's business categories
- **Vendor Types**: `belongsToMany(VendorType::class)` - Vendor types (manufacturer, distributor, etc.)
- **Contacts**: `morphMany(ContactPerson::class)` - Contact persons
- **Certificates**: `morphMany(Certificate::class)` - Business certificates
- **Documents**: `morphMany(Document::class)` - General documents
- **Reviews**: `morphMany(Review::class)` - Vendor reviews
- **RFQs**: `hasMany(Rfq::class)` - Request for quotations
- **Quotations**: `hasMany(Quotation::class)` - Vendor's quotations
- **Catalogues**: `hasMany(Catalogue::class)` - Vendor's catalogues
- **Purchase Orders**: `hasMany(PurchaseOrder::class)` - Vendor's purchase orders

#### Vendor Status States

| Status | is_verified | is_rejected | Description |
|--------|-------------|-------------|-------------|
| pending | false | false | Awaiting admin review |
| verified | true | false | Approved and active |
| rejected | false | true | Rejected by admin |

Model scope: `scopeVerified()` - filters for verified vendors

## Dependencies & Graph Links

### Direct Dependencies

- **[User](User.md)** - Vendors belong to users
- **[Category](Category.md)** - Vendors have many-to-many relationship with categories
- **[VendorType](VendorType.md)** - Vendors have many-to-many relationship with vendor types
- **[Product](Product.md)** - Vendors have many products
- **[Subscription](Subscription.md)** - Vendors can have subscriptions for boost scores

### Cross-Domain Connections

- **[Document](Document.md)** - Polymorphic relationship for vendor documents
- **[Certificate](Certificate.md)** - Polymorphic relationship for vendor certificates
- **[ContactPerson](ContactPerson.md)** - Polymorphic relationship for vendor contacts
- **[Review](Review.md)** - Polymorphic relationship for vendor reviews
- **[Rfq](Rfq.md)** - Vendors receive RFQs
- **[Quotation](Quotation.md)** - Vendors submit quotations
- **[PurchaseOrder](PurchaseOrder.md)** - Vendors receive purchase orders
- **[Notification](Notification.md)** - Vendor registration, approval, rejection notifications

## Red Flags & Tech Debt

### 1. Hardcoded Dashboard Metrics

**Location**: `Vendor/VendorDashBoardController.php:75-80`

**Issues**:
- Dashboard metrics are hardcoded instead of calculated
- `response_time`, `product_views`, `buyer_enquiries`, `win_rate` are static values
- No real-time data for vendor performance tracking

```php
'response_time' => '2.3 hours',
'product_views' => 1247,
'buyer_enquiries' => 24,
'win_rate' => 25,
```

**Recommendation**: Calculate these metrics from actual data:
- Response time: Average time from RFQ to quotation
- Product views: Track product view events
- Buyer enquiries: Count RFQs sent to vendor
- Win rate: (Purchase orders / Quotations) * 100

### 2. Commented Out Code

**Location**: `Vendor/VendorDashBoardController.php:23-49`

**Issues**:
- Cache logic is commented out
- Unsubmitted RFQ query is commented out
- No explanation for why caching was disabled

```php
//Cache::remember("vendor:{$vendor->id}:submitted_rfq_count", $cacheTtl, function () use ($vendor) {
  //  return 
```

**Recommendation**: Either enable caching or remove commented code with explanation.

### 3. N+1 Query in VendorResource

**Location**: `VendorResource.php:45-46`

**Issues**:
- `$this->products->count()` causes N+1 query in vendor lists
- No eager loading of products count

**Recommendation**: Use `withCount('products')` in query.

### 4. N+1 Query in FavoriteVendorResource

**Location**: `FavoriteVendorResource.php:42-51`

**Issues**:
- `$this->purchaseOrders->map()` causes N+1 queries
- No eager loading of purchase orders

**Recommendation**: Use `with('purchaseOrders')` in query.

### 5. Profile Completion Calculation Inefficiency

**Location**: `Vendor.php:95-224`

**Issues**:
- Profile completion scores are calculated on every access
- Multiple database queries for each score calculation
- No caching of completion scores
- Called via appends on every vendor load

**Recommendation**:
- Cache completion scores in database
- Update scores on profile changes
- Use computed columns or triggers

### 6. Missing Database Indexes

**Location**: Migration files

**Issues**:
- No indexes on frequently queried fields
- `user_id`, `is_verified`, `is_rejected`, `city`, `state` lack indexes
- Will cause slow queries as data grows

**Migration**: `2025_10_09_100124_create_vendors_table.php`

**Recommendation**: Add indexes:
```sql
CREATE INDEX idx_vendors_user_id ON vendors(user_id);
CREATE INDEX idx_vendors_is_verified ON vendors(is_verified);
CREATE INDEX idx_vendors_is_rejected ON vendors(is_rejected);
CREATE INDEX idx_vendors_city ON vendors(city);
CREATE INDEX idx_vendors_state ON vendors(state);
CREATE INDEX idx_vendors_composite ON vendors(is_verified, is_rejected);
```

### 7. Duplicate Code in Resources

**Location**: `VendorProfileResource.php:17-34`, `PublicVendorResource.php:18-34`

**Issues**:
- Document files reduction logic is duplicated
- File existence checks are repeated
- No abstraction for document file handling

**Recommendation**: Extract to `VendorDocumentService` or trait.

### 8. Inconsistent Status Handling

**Location**: `VendorResource.php:17-22`

**Issues**:
- Status is calculated from `is_verified` and `is_rejected` flags
- No enum for vendor status
- Inconsistent with database `status` enum field

```php
$status = '';
if (! $this->is_rejected) {
    $status = $this->is_verified ? 'verified' : 'pending';
} else {
    $status = 'rejected';
}
```

**Recommendation**: Create `VendorStatus` enum and use consistently.

### 9. No File Validation on Update

**Location**: Not found in code

**Issues**:
- No validation on file uploads during profile update
- Could upload larger files than allowed
- No validation on file types

**Recommendation**: Add file size and type validation in update methods.

### 10. Admin Notification Loop

**Location**: `Admin/VendorController.php:114-120, 152-158`

**Issues**:
- Loops through all admins to send notifications
- Could be slow with many admins
- No batching or queueing for admin notifications

**Recommendation**: Use notification channel or batch notifications.

### 11. Missing Error Handling

**Location**: `Admin/VendorController.php:90-92`

**Issues**:
- Generic error handling catches all exceptions
- No specific error messages for different failure scenarios
- Logs not structured

**Recommendation**: Add specific error handling for different scenarios.

### 12. No Vendor Deletion

**Location**: `Admin/VendorController.php:198-201`

**Issues**:
- `destroy()` method is empty
- No way to delete vendors
- Soft delete exists but not used

**Recommendation**: Implement vendor deletion with proper cleanup.

### 13. Profile Completion Score Logic Issues

**Location**: `Vendor.php:95-145`

**Issues**:
- Logo counts as 20% but other fields count as 10%
- No validation that score doesn't exceed 100
- No minimum score requirements for verification

**Recommendation**:
- Standardize scoring weights
- Add validation for score bounds
- Define minimum score for verification

### 14. No Vendor Search in Admin Controller

**Location**: `Admin/VendorController.php:28-30`

**Issues**:
- Search only checks `name` field
- No search by email, phone, or company name
- No full-text search

**Recommendation**: Add multi-field search with full-text support.

### 15. Dashboard RFQ Query Inefficiency

**Location**: `Vendor/VendorDashBoardController.php:34-40`

**Issues**:
- `whereNUll('vendor_id')` typo (should be `whereNull`)
- No eager loading for related data
- Could cause N+1 queries

**Recommendation**: Fix typo and add eager loading.

## Future Upgrades (Postgres & Scalability)

### Database Schema Improvements

1. **Add Indexes**:
   ```sql
   CREATE INDEX idx_vendors_user_id ON vendors(user_id);
   CREATE INDEX idx_vendors_is_verified ON vendors(is_verified);
   CREATE INDEX idx_vendors_is_rejected ON vendors(is_rejected);
   CREATE INDEX idx_vendors_city ON vendors(city);
   CREATE INDEX idx_vendors_state ON vendors(state);
   CREATE INDEX idx_vendors_composite ON vendors(is_verified, is_rejected);
   CREATE INDEX idx_vendors_created_at ON vendors(created_at DESC);
   ```

2. **Add Computed Columns**:
   ```sql
   ALTER TABLE vendors
   ADD COLUMN profile_complete_score INTEGER
   GENERATED ALWAYS AS (
       (CASE WHEN tin_number IS NOT NULL THEN 10 ELSE 0 END) +
       (CASE WHEN license_number IS NOT NULL THEN 10 ELSE 0 END) +
       (CASE WHEN address IS NOT NULL THEN 10 ELSE 0 END) +
       (CASE WHEN city IS NOT NULL THEN 10 ELSE 0 END) +
       (CASE WHEN logo IS NOT NULL THEN 20 ELSE 0 END) +
       (CASE WHEN EXISTS (SELECT 1 FROM vendor_vendor_type WHERE vendor_id = vendors.id) THEN 10 ELSE 0 END) +
       (CASE WHEN EXISTS (SELECT 1 FROM category_vendor WHERE vendor_id = vendors.id) THEN 10 ELSE 0 END) +
       (CASE WHEN EXISTS (SELECT 1 FROM contact_people WHERE contactable_type = 'App\\Models\\Vendor' AND contactable_id = vendors.id) THEN 10 ELSE 0 END) +
       (CASE WHEN EXISTS (SELECT 1 FROM certificates WHERE certificateable_type = 'App\\Models\\Vendor' AND certificateable_id = vendors.id) THEN 10 ELSE 0 END)
   ) STORED;
   ```

3. **Add Constraints**:
   ```sql
   ALTER TABLE vendors
   ADD CONSTRAINT check_verified_rejected_mutually_exclusive
   CHECK (NOT (is_verified = true AND is_rejected = true));
   ```

4. **Use Postgres JSONB**:
   - Add JSONB column for flexible vendor metadata

5. **Add Full-Text Search**:
   ```sql
   CREATE INDEX idx_vendors_name_fts ON vendors USING gin(to_tsvector('english', name));
   CREATE INDEX idx_vendors_legal_name_fts ON vendors USING gin(to_tsvector('english', legal_name));
   ```

### Architecture Improvements

1. **Event-Driven Architecture**:
   - Dispatch events on vendor approval/rejection
   - Allow multiple listeners (email, SMS, analytics, notifications)

2. **Queue Notifications**:
   - Move all notifications to background queue
   - Implement retry logic for failed notifications
   - Batch admin notifications

3. **Profile Completion Service**:
   - Extract profile completion logic to dedicated service
   - Implement caching for completion scores
   - Update scores asynchronously

4. **Dashboard Metrics Service**:
   - Extract dashboard metrics to dedicated service
   - Calculate metrics from actual data
   - Implement caching for dashboard data

5. **Vendor Search Service**:
   - Implement multi-field search
   - Add full-text search support
   - Implement faceted search

### Performance Optimizations

1. **Caching**:
   - Cache vendor profile data
   - Cache dashboard metrics
   - Implement cache warming for popular vendors

2. **Batch Processing**:
   - Batch vendor status updates
   - Batch notification dispatch
   - Batch profile score calculations

3. **Read Replicas**:
   - Route vendor listing queries to read replicas
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
   - Rate limit vendor registration endpoints
   - Rate limit profile update endpoints
   - Prevent abuse

3. **Access Control**:
   - Implement row-level security for multi-tenant access
   - Add audit logging for vendor modifications
   - Implement data retention policies

### Monitoring Improvements

1. **Metrics**:
   - Track vendor registration rates
   - Monitor verification times
   - Track profile completion rates

2. **Alerting**:
   - Alert on high rejection rates
   - Alert on verification backlog
   - Alert on storage exhaustion

3. **Logging**:
   - Structured logging for all operations
   - Correlation IDs for request tracing
   - Performance logging for slow queries

## Related Files

### Models
- `app/Models/Vendor.php`
- `app/Models/VendorType.php`
- `app/Models/FavoriteVendor.php`

### Controllers
- `app/Http/Controllers/Admin/VendorController.php`
- `app/Http/Controllers/Vendor/VendorDashBoardController.php`

### Resources
- `app/Http/Resources/VendorResource.php`
- `app/Http/Resources/VendorProfileResource.php`
- `app/Http/Resources/PublicVendorResource.php`
- `app/Http/Resources/NewVendorResource.php`
- `app/Http/Resources/ShortVendorResource.php`
- `app/Http/Resources/FavoriteVendorResource.php`

### Policies
- `app/Policies/VendorProfilePolicy.php`

### Middleware
- `app/Http/Middleware/VendorVerified.php`

### Notifications
- `app/Notifications/VendorApproveNotification.php`
- `app/Notifications/VendorRejectedNotification.php`
- `app/Notifications/VendorRegistrationNotification.php`
- `app/Notifications/AdminVendorApprovedNotification.php`
- `app/Notifications/AdminVendorRejectedNotification.php`
- `app/Notifications/AdminVendorRegistrationNotification.php`

### Mail
- `app/Mail/VendorWelcome.php`
- `app/Mail/VendorVerified.php`

### Migrations
- `database/migrations/2025_10_09_100124_create_vendors_table.php`
- `database/migrations/2025_10_09_094332_create_vendor_types_table.php`
- `database/migrations/2025_10_09_100125_vendor_vendor_type.php`
- `database/migrations/2025_11_03_050335_create_category_vendor.php`
- `database/migrations/2026_04_28_133008_add_boost_score_to_vendors.php`
- `database/migrations/Favorite/2025_12_23_112417_create_favorite_vendors_table.php`
