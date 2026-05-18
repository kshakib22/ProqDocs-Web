---
title: "RfqResource - RFQ API Transformation Layer"
---
# RfqResource - RFQ API Transformation Layer

**Entity**: `App\Http\Resources\RfqResource`
**Purpose**: Laravel JsonResource for serializing RFQ (Request for Quotation) models into API responses
**Version**: 1.0
**Last Updated**: 2026-05-04

---

...

## Relationship Serialization

### Buyer Relationship

**Condition**: `whenLoaded('buyer')`

**Fields**:
- `id` - Buyer profile ID
- `user_id` - Associated user ID
- `name` - Buyer name
- `user` (nested) - User details when `buyer.user` is loaded

**Nested User Fields**:
- `id` - User ID
- `name` - User name
- `email` - User email

**N+1 Risk**: HIGH - Requires `buyer` and `buyer.user` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with(['buyer.user'])->get();
```

---

### Vendor Relationship

**Condition**: `whenLoaded('vendor')`

**Fields**:
- `id` - Vendor profile ID
- `company_name` - Vendor company name
- `user_id` - Associated user ID
- `user` (nested) - User details when `vendor.user` is loaded

**Nested User Fields**:
- `id` - User ID
- `name` - User name
- `email` - User email

**N+1 Risk**: HIGH - Requires `vendor` and `vendor.user` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with(['vendor.user'])->get();
```

---

### Project Relationship

**Condition**: `whenLoaded('project')`

**Fields**:
- `id` - Project ID
- `name` - Project name (mapped from `project_name`)
- `location` - Concatenated city and country
- `description` - Project description
- `status` - Project status (mapped from `boq_status`)

**Field Remapping**:
- `project_name` → `name`
- `boq_status` → `status`

**N+1 Risk**: MEDIUM - Requires `project` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('project')->get();
```

---

### Product Relationship

**Condition**: `whenLoaded('product')`

**Fields**:
- `id` - Product ID
- `name` - Product name
- `description` - Product description
- `unit` - Unit of measurement
- `base_price` - Base price (coerced to float)
- `product_code` - Product code
- `product_image` - Full URL to product image

**URL Generation**:
```php
$productImage = $this->product->product_image ? url('storage/'.$this->product->product_image) : null;
```

**N+1 Risk**: MEDIUM - Requires `product` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('product')->get();
```

---

### Category Relationship

**Condition**: `whenLoaded('category')`

**Fields**:
- `id` - Category ID
- `name` - Category name
- `slug` - URL-friendly slug

**N+1 Risk**: LOW - Simple relationship, minimal data

**Eager Load Pattern**:
```php
Rfq::with('category')->get();
```

---

### Documents Relationship

**Condition**: `whenLoaded('documents')`

...

---

### Quotations Relationship

**Condition**: `whenLoaded('quotations')`

**Fields**: Delegated to `ShortQuotationResource`

**N+1 Risk**: HIGH - Requires `quotations` to be eager-loaded

**Eager Load Pattern**:
```php
Rfq::with('quotations')->get();
```

---

...

## Related Resources

### Direct Dependencies

- `ShortQuotationResource` - Used for nested quotation serialization

### Related Models

- `App\Models\Rfq` - The underlying model
- `App\Models\Buyer` - Buyer profile
- `App\Models\Vendor` - Vendor profile
- `App\Models\Project` - Project details
- `App\Models\Product` - Product details
- `App\Models\Category` - Category details
- `App\Models\Document` - Document attachments
- `App\Models\Quotation` - Quotation submissions

### Related Controllers

- `App\Http\Controllers\RfqController` - Primary controller
- `App\Http\Controllers\Api\RfqController` - API controller

### Related Resources

- `App\Http\Resources\ShortQuotationResource` - Quotation summary
- `App\Http\Resources\QuotationResource` - Full quotation details

---

...
