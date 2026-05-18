---
name: QuotationService
description: Laravel service class for Quotation business logic - handles vendor quotation submission, management, and buyer acceptance
type: entity
title: "QuotationService"
---

# QuotationService

## Architectural Purpose

...

## Service Dependencies

```php
use App\Http\Requests\UpdateQuotationRequest;
use App\Http\Resources\QuotationResource;
use App\Models\Buyer;
use App\Models\Document;
use App\Models\Product;
use App\Models\Quotation;
use App\Models\QutationService;
use App\Models\Rfq;
use App\Models\Vendor;
use App\Notifications\QuotationSubmittedNotification;
use App\Notifications\QuotationUpdatedNotification;
use App\Traits\ServiceResponder;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;
```

- **ServiceResponder**: Trait for standardized API responses
- **QuotationResource**: API resource for serialization
- **QutationService**: Line items for quotation breakdown
- **DB**: Database facade for transactions
- **Storage**: File storage for documents and images
- **Log**: Laravel logging facade

...

## Tech Debt Summary

| Issue | Severity | Impact | Recommended Action |
|-------|----------|--------|-------------------|
| N+1 query in `getStatusCounts()` | HIGH | Performance issue | Use single query with GROUP BY |
| N+1 query in `getBuyerStatusCounts()` | HIGH | Performance issue | Use single query with GROUP BY |
| Excessive logging in `createQuotation()` | MEDIUM | Performance impact | Remove or reduce logging |
| Commented code throughout | MEDIUM | Code confusion | Remove or document |
| Service deletion in `updateQuotation()` | MEDIUM | Performance issue | Use update instead of delete |
| Incomplete `createPrivateQuotation()` | MEDIUM | Functionality incomplete | Complete implementation |
| No validation on service data | LOW | Data integrity risk | Add validation rules |
| No file size validation | LOW | Security risk | Add file size limits |
| No error handling in `handleDocumentUploads()` | LOW | Silent failures | Add error handling |

## Cross-References

- [Quotation-Model](/entities/quotation-model) - Data model for quotations
- [QutationService-Model](/entities/qutationservice-model) - Line items for quotations
- [Rfq-Model](/entities/rfq-model) - Parent RFQ for quotations
- [QuotationController](/entities/quotationcontroller) - Controller that uses this service
- [QuotationResource](/entities/quotationresource) - API resource for serialization

## Usage Examples

...
