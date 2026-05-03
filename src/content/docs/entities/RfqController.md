---
aliases: []
tags: [laravel, backend, auto-generated]
title: "RfqController"
---
# RfqController

The RfqController handles HTTP requests for RFQ operations from the buyer perspective. Located at `app/Http/Controllers/Buyer/RfqController.php`.

## Current Architecture & Flow

### Endpoints

#### RFQ Management
- `GET /api/buyer/rfqs` - List buyer's RFQs with pagination and filters
- `POST /api/buyer/rfqs` - Create new RFQ
- `GET /api/buyer/rfqs/{rfq}` - Get specific RFQ details
- `PUT /api/buyer/rfqs/{rfq}` - Update RFQ (public only)
- `DELETE /api/buyer/rfqs/{rfq}` - Delete RFQ

#### Public RFQs
- `GET /api/public-rfqs` - Get public RFQs for buyer's projects

#### Private RFQs
- `GET /api/buyer/private-rfqs` - List private RFQs
- `POST /api/buyer/private-rfqs` - Create private RFQ

#### RFQ Actions
- `POST /api/buyer/rfqs/{rfq}/reject` - Reject RFQ and all quotations

### Authorization
- Only buyers can access RFQ endpoints
- Only RFQ owner can update/delete
- Public RFQs can be viewed by vendors
- Private RFQs restricted to assigned vendor

### Request Validation
- Uses [StoreRfqRequest](StoreRfqRequest.md) for creation
- Uses [UpdateRfqRequest](UpdateRfqRequest.md) for updates
- Uses [PrivateRfqRequest](PrivateRfqRequest.md) for private RFQ creation

## Dependencies & Graph Links

- Uses [RfqService](RfqService.md) for all business logic
- Returns [RfqResource](RfqResource.md), [PublicRfqResource](PublicRfqResource.md), [PrivateRfqResource](PrivateRfqResource.md)
- Extends [BaseController](BaseController.md)

## Red Flags & Tech Debt

### Fat Controller
- **613 lines** - too much logic in controller
- **Inline authorization checks** repeated across methods:
  ```php
  if (! $user->buyer_id) {
      return $this->error('Only buyers can access RFQs', [], 403);
  }
  ```

### Code Quality Issues
- **Mixed concerns**: authorization, validation, business logic
- **Inconsistent error handling** patterns
- **Duplicate authorization logic** in multiple methods
- **No middleware** for common authorization checks

### Business Logic in Controller
- Status checks in controller instead of service:
  ```php
  if ($rfq->status === 'completed' || $rfq->status === 'cancelled') {
      return $this->error('You are not authorized to update this RFQ', [], 403);
  }
  ```

### API Design Issues
- Inconsistent response formats
- No rate limiting
- No request throttling

## Future Upgrades (Postgres & Scalability)

### Controller Refactoring
1. **Extract authorization to middleware**:
   ```php
   class BuyerOnlyMiddleware
   {
       public function handle(Request $request, Closure $next)
       {
           if (! $request->user()?->buyer_id) {
               return response()->json(['error' => 'Only buyers can access'], 403);
           }
           return $next($request);
       }
   }
   ```

2. **Extract to policies**:
   ```php
   class RfqPolicy
   {
       public function view(User $user, Rfq $rfq): bool
       public function update(User $user, Rfq $rfq): bool
       public function delete(User $user, Rfq $rfq): bool
   }
   ```

3. **Use form requests** for all validation

### API Improvements
1. Add rate limiting middleware
2. Add request throttling
3. Standardize response formats
4. Add API versioning
5. Add OpenAPI documentation

### Performance
- Add caching for public RFQ listings
- Use pagination for all list endpoints
- Add query optimization for large datasets
