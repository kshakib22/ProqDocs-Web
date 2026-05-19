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

- **[Vendor](/ProqDocs-Web/entities/vendor-model/)** - Core vendor model with soft deletes, verification status, profile completion tracking, and relationships to user, products, categories, vendor types, certificates, contacts, reviews, RFQs, quotations, catalogues, and purchase orders.
- **[VendorType](/ProqDocs-Web/entities/vendortype-model/)** - Vendor types (e.g., Manufacturer, Distributor, Wholesaler).
- **[FavoriteVendor](/ProqDocs-Web/entities/favoritevendor-model/)** - Buyer's favorite vendors.

#### Controllers

- **[Admin/VendorController](/ProqDocs-Web/entities/adminvendorcontroller/)** - Admin-facing vendor management (203 lines):
  - `index()` - List vendors with filtering and search
  - `approveVendor()` - Approve vendor registration
  - `rejectVendor()` - Reject vendor registration with reason
  - `show()` - Get vendor details

- **[Vendor/VendorDashBoardController](/ProqDocs-Web/entities/vendordashboardcontroller/)** - Vendor dashboard (93 lines):
  - `__invoke()` - Get vendor dashboard with RFQ counts, product counts, quotations

#### Resources

- **[VendorResource](/ProqDocs-Web/entities/vendorresource/)** - Full vendor details for admin listing.
- **[VendorProfileResource](/ProqDocs-Web/entities/vendorprofileresource/)** - Detailed vendor profile with scores and documents.
- **[PublicVendorResource](/ProqDocs-Web/entities/publicvendorresource/)** - Public vendor profile (similar to profile but without sensitive data).
- **[NewVendorResource](/ProqDocs-Web/entities/newvendorresource/)** - Minimal vendor resource for new registrations.
- **[ShortVendorResource](/ProqDocs-Web/entities/shortvendorresource/)** - Minimal vendor representation (id, name, logo).
- **[FavoriteVendorResource](/ProqDocs-Web/entities/favoritevendorresource/)** - Favorite vendor with purchase order summary.

#### Policies

- **[VendorProfilePolicy](/ProqDocs-Web/entities/vendorprofilepolicy/)** - Vendor profile access control (93 lines):
  - `create()`, `update()`, `view()` - Vendor can only access their own profile
  - `updateContacts()`, `updateCertificates()`, `updateTypesAndCategories()` - Section-specific updates
  - `deleteContact()`, `deleteCertificates()` - Delete permissions

#### Middleware

- **[VendorVerified](/ProqDocs-Web/entities/vendorverified-middleware/)** - Middleware to ensure vendor is verified and not rejected.

#### Notifications

- **[VendorApproveNotification](/ProqDocs-Web/entities/vendorapprovenotification/)** - Sent to vendor on approval (mail + database).
- **[VendorRejectedNotification](/ProqDocs-Web/entities/vendorrejectednotification/)** - Sent to vendor on rejection (mail + database).
- **[VendorRegistrationNotification](/ProqDocs-Web/entities/vendorregistrationnotification/)** - Sent to vendor on registration (mail + database).
- **[AdminVendorApprovedNotification](/ProqDocs-Web/entities/adminvendorapprovednotification/)** - Sent to admins on vendor approval (database only).
- **[AdminVendorRejectedNotification](/ProqDocs-Web/entities/adminvendorrejectednotification/)** - Sent to admins on vendor rejection (database only).
- **[AdminVendorRegistrationNotification](/ProqDocs-Web/entities/adminvendorregistrationnotification/)** - Sent to admins on new vendor registration (database only).

#### Mail

- **[VendorWelcome](/ProqDocs-Web/entities/vendorwelcome-mail/)** - Welcome email for new vendor registration.
- **[VendorVerified](/ProqDocs-Web/entities/vendorverified-mail/)** - Verification email for approved vendors.

...

## Dependencies & Graph Links

### Direct Dependencies

- **[User](/ProqDocs-Web/entities/user-model/)** - Vendors belong to users
- **[Category](/ProqDocs-Web/entities/category-model/)** - Vendors have many-to-many relationship with categories
- **[VendorType](/ProqDocs-Web/entities/vendortype-model/)** - Vendors have many-to-many relationship with vendor types
- **[Product](/ProqDocs-Web/entities/product-domain/)** - Vendors have many products
- **[Subscription](/ProqDocs-Web/entities/subscription-model/)** - Vendors can have subscriptions for boost scores

### Cross-Domain Connections

- **[Document](/ProqDocs-Web/entities/document-model/)** - Polymorphic relationship for vendor documents
- **[Certificate](/ProqDocs-Web/entities/certificate-model/)** - Polymorphic relationship for vendor certificates
- **[ContactPerson](/ProqDocs-Web/entities/contactperson-model/)** - Polymorphic relationship for vendor contacts
- **[Review](/ProqDocs-Web/entities/review-model/)** - Polymorphic relationship for vendor reviews
- **[Rfq](/ProqDocs-Web/entities/rfq-model/)** - Vendors receive RFQs
- **Quotation** - Vendors submit quotations
- **[PurchaseOrder](/ProqDocs-Web/entities/purchase-order-domain/)** - Vendors receive purchase orders
- **[Notification](/ProqDocs-Web/entities/notification-domain/)** - Vendor registration, approval, rejection notifications

...