---
aliases: []
tags: [laravel, backend, auto-generated]
title: "RfqResource"
---
# RfqResource

The RfqResource transforms RFQ models into API responses. Located at `app/Http/Resources/RfqResource.php`.

## Current Architecture & Flow

### Response Structure
- **Basic fields**: id, rfq_code, rfq_title, description, status, type, deadlines
- **Computed fields**: is_private, is_public, days_remaining, is_expired, total_value
- **Relationships**: buyer, vendor, project, product, category, documents, quotations

### Conditional Loading
Uses Laravel's `whenLoaded()` to avoid N+1 queries:
- `buyer` with nested `buyer.user`
- `vendor` with nested `vendor.user`
- `project`, `product`, `category`
- `documents` collection
- `quotations` collection (uses [ShortQuotationResource](ShortQuotationResource.md))

### Computed Fields
- `days_remaining`: Days until deadline (0 if expired)
- `is_expired`: Whether deadline has passed
- `total_value`: unit_price × estimated_quantity

### Image Handling
- Converts storage paths to full URLs
- Handles null values gracefully

## Dependencies & Graph Links

- Used by [RfqService](RfqService.md) for RFQ responses
- References [Buyer Model](Buyer Model.md), [Vendor Model](Vendor Model.md), [Project Model](Project Model.md), [Product Model](Product Model.md), [Category Model](Category Model.md)
- Uses [ShortQuotationResource](ShortQuotationResource.md) for nested quotations

## Red Flags & Tech Debt

### Performance Issues
- **Storage existence checks** in resource layer:
  ```php
  'product_image' => $this->product_image ? url('storage/'.$this->product_image) : null,
  ```
  Should validate at upload time, not on every read

- **No caching** for computed fields like `days_remaining`

### Code Quality
- **Nested conditional loading** could be simplified
- **Duplicate logic** for image URL generation

### Data Integrity
- No validation that `days_remaining` is non-negative
- No handling for deleted related models (except withTrashed)

## Future Upgrades (Postgres & Scalability)

### Resource Improvements
1. **Add caching** for computed fields:
   ```php
   protected $memoizedDaysRemaining;

   protected function getDaysRemainingAttribute()
   {
       return $this->memoizedDaysRemaining ??= $this->calculateDaysRemaining();
   }
   ```

2. **Extract image URL logic**:
   ```php
   trait HasImageUrls
   {
       protected function imageUrl(?string $path): ?string
       {
           return $path ? url('storage/'.$path) : null;
       }
   }
   ```

3. **Add versioning** for API responses

### Performance
- Use eager loading consistently
- Add caching for frequently accessed RFQs
- Consider using cursor-based pagination for large datasets

### Monitoring
- Track resource transformation time
- Monitor N+1 query issues
