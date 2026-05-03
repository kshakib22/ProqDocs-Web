---
aliases: []
tags: [laravel, backend, auto-generated]
title: "QuotationController"
---
# QuotationController

The QuotationController handles HTTP requests for quotation operations from the vendor perspective. Located at `app/Http/Controllers/Vendor/QuotationController.php`.

## Current Architecture & Flow

### Endpoints

#### Quotation Management
- `GET /api/vendor/{vendor}/quotations` - List vendor's quotations
- `POST /api/vendor/{vendor}/quotations` - Create new quotation
- `GET /api/vendor/{vendor}/quotations/{quotation}` - Get specific quotation
- `PUT /api/vendor/{vendor}/quotations/{quotation}` - Update quotation
- `DELETE /api/vendor/{vendor}/quotations/{quotation}` - Delete quotation

#### Private Quotations
- `POST /api/vendor/{vendor}/private-quotations` - Create private quotation

#### RFQ Discovery
- `GET /api/vendor/{vendor}/public-rfqs` - Get public RFQs available for quoting
- `GET /api/vendor/{vendor}/private-rfqs` - Get private RFQs assigned to vendor
- `GET /api/vendor/{vendor}/rfqs/{rfq}` - Get specific RFQ details

#### Document Management
- `DELETE /api/vendor/{vendor}/quotations/{quotation}/documents/{document}` - Remove document

#### Product Quotations
- `GET /api/vendor/{vendor}/product-quotations/{category_id}` - Get products by category

### Authorization
- Only vendors can access quotation endpoints
- Only quotation owner can update/delete
- Private RFQs restricted to assigned vendor
- Public RFQs available to all vendors

### Request Validation
- Uses [StoreQuotationRequest](StoreQuotationRequest.md) for creation
- Uses [UpdateQuotationRequest](UpdateQuotationRequest.md) for updates

## Dependencies & Graph Links

- Uses [QuotationService](QuotationService.md) for all business logic
- Returns [QuotationResource](QuotationResource.md), [PublicRfqResource](PublicRfqResource.md), [PrivateRfqResource](PrivateRfqResource.md)
- Extends [BaseController](BaseController.md)

## Red Flags & Tech Debt

### Fat Controller
- **577 lines** - too much logic in controller
- **Inline authorization checks** repeated across methods
- **Mixed concerns**: authorization, validation, business logic

### Code Quality Issues
- **Inconsistent authentication**:
  - Uses `Auth::user()` in some methods
  - Uses `JWTAuth::user()` in others
  - Should standardize on one approach

- **Duplicate authorization logic**:
  ```php
  if (! $user->vendor_id || $user->vendor_id !== $vendor->id) {
      return $this->error('Only the vendor can access their quotations', [], 403);
  }
  ```

### Business Logic in Controller
- Image validation in controller:
  ```php
  if (!$firstQuotationImage || !str_starts_with((string) $firstQuotationImage->getMimeType(), 'image/')) {
      return $this->error('First quotation image file is required...', [], 400);
  }
  ```

### API Design Issues
- Inconsistent response formats
- No rate limiting
- No request throttling
- Mixed REST patterns

## Future Upgrades (Postgres & Scalability)

### Controller Refactoring
1. **Extract authorization to middleware**:
   ```php
   class VendorOnlyMiddleware
   {
       public function handle(Request $request, Closure $next)
       {
           if (! $request->user()?->vendor_id) {
               return response()->json(['error' => 'Only vendors can access'], 403);
           }
           return $next($request);
       }
   }
   ```

2. **Extract to policies**:
   ```php
   class QuotationPolicy
   {
       public function view(User $user, Quotation $quotation): bool
       public function update(User $user, Quotation $quotation): bool
       public function delete(User $user, Quotation $quotation): bool
   }
   ```

3. **Standardize authentication** - choose either Auth or JWTAuth

### API Improvements
1. Add rate limiting middleware
2. Add request throttling
3. Standardize response formats
4. Add API versioning
5. Add OpenAPI documentation
6. Use resource collections consistently

### Performance
- Add caching for public RFQ listings
- Use pagination for all list endpoints
- Add query optimization for large datasets
- Consider using cursor-based pagination for large result sets
