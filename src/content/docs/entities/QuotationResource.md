---
aliases: []
tags: [laravel, backend, auto-generated]
title: "QuotationResource"
---
# QuotationResource

The QuotationResource transforms quotation models into API responses. Located at `app/Http/Resources/QuotationResource.php`.

## Current Architecture & Flow

### Response Structure
- **Basic fields**: id, quotation_number, quotation_date, status, pricing details
- **Pricing fields**: unit_count, unit_price, sub_amount, services_charge, total_amount
- **Additional charges**: vat_rate, tax_amount, shipping_amount, loading_charge
- **Terms**: validity_period
- **Computed fields**: is_valid, days_until_expiry, subtotal

### Conditional Loading
Uses Laravel's `whenLoaded()` to avoid N+1 queries:
- `rfq` (withTrashed)
- `vendor` with nested `vendor.user`
- `buyer` with nested `buyer.user`
- `project` (withTrashed)
- `product` (withTrashed)
- `category` (withTrashed)
- `documents` collection
- `quotationServices` collection

### Computed Fields
- `is_valid`: Whether quotation is still within validity period
- `days_until_expiry`: Days until quotation expires (0 if expired)
- `subtotal`: Alias for sub_amount

### Image Handling
- Checks storage existence before generating URLs
- Handles null values gracefully
- Uses `Storage::disk('public')->exists()` for validation

### Soft Delete Handling
- All related models use `withTrashed()` to preserve data
- Adds `is_deleted` flag to indicate soft-deleted status

## Dependencies & Graph Links

- Used by [QuotationService](QuotationService.md) for quotation responses
- References [Rfq Model](Rfq Model.md), [Vendor Model](Vendor Model.md), [Buyer Model](Buyer Model.md), [Project Model](Project Model.md), [Product Model](Product Model.md), [Category Model](Category Model.md)
- References [QutationService Model](QutationService Model.md) for quotation services

## Red Flags & Tech Debt

### Performance Issues
- **Storage existence checks** in resource layer:
  ```php
  'quotation_image' => $this->quotation_image && Storage::disk('public')->exists($this->quotation_image)
      ? url('storage/'.$this->quotation_image) : null,
  ```
  This adds I/O overhead on every response. Should validate at upload time.

- **No caching** for computed fields like `days_until_expiry`

### Code Quality
- **Duplicate image URL logic** (appears twice in resource)
- **Nested null checks** could be simplified
- **Inconsistent rounding** - some fields use `round()`, others don't

### Data Integrity
- No validation that pricing calculations are correct
- No handling for negative values
- No validation that `days_until_expiry` is non-negative

## Future Upgrades (Postgres & Scalability)

### Resource Improvements
1. **Add caching** for computed fields:
   ```php
   protected $memoizedDaysUntilExpiry;

   protected function getDaysUntilExpiryAttribute()
   {
       return $this->memoizedDaysUntilExpiry ??= $this->calculateDaysUntilExpiry();
   }
   ```

2. **Extract image URL logic**:
   ```php
   trait HasImageUrls
   {
       protected function imageUrl(?string $path): ?string
       {
           if (!$path) return null;
           return Storage::disk('public')->exists($path)
               ? url('storage/'.$path)
               : null;
       }
   }
   ```

3. **Add validation** for pricing calculations

### Performance
- Remove storage existence checks from resource layer
- Add caching for frequently accessed quotations
- Consider using cursor-based pagination for large datasets
- Add database-level computed columns for expensive calculations

### Monitoring
- Track resource transformation time
- Monitor N+1 query issues
- Track storage I/O operations
