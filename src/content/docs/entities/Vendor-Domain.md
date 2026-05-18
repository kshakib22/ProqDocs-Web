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

- **[Vendor](/entities/vendor-model)** - Core vendor model with soft deletes, verification status, profile completion tracking, and relationships to user, products, categories, vendor types, certificates, contacts, reviews, RFQs, quotations, catalogues, and purchase orders.
- **[VendorType](/entities/vendortype-model)** - Vendor types (e.g., Manufacturer, Distributor, Wholesaler).
- **[FavoriteVendor](/entities/favoritevendor-model)** - Buyer's favorite vendors.

#### Controllers

- **[Admin/VendorController](/entities/adminvendorcontroller)** - Admin-facing vendor management (203 lines):
  - `index()` - List vendors with filtering and search
  - `approveVendor()` - Approve vendor registration
  - `rejectVendor()` - Reject vendor registration with reason
  - `show()` - Get vendor details

- **[Vendor/VendorDashBoardController](/entities/vendordashboardcontroller)** - Vendor dashboard (93 lines):
  - `__invoke()` - Get vendor dashboard with RFQ counts, product counts, quotations

#### Resources

- **[VendorResource](/entities/vendorresource)** - Full vendor details for admin listing.
- **[VendorProfileResource](/entities/vendorprofileresource)** - Detailed vendor profile with scores and documents.
- **[PublicVendorResource](/entities/publicvendorresource)** - Public vendor profile (similar to profile but without sensitive data).
- **[NewVendorResource](/entities/newvendorresource)** - Minimal vendor resource for new registrations.
- **[ShortVendorResource](/entities/shortvendorresource)** - Minimal vendor representation (id, name, logo).
- **[FavoriteVendorResource](/entities/favoritevendorresource)** - Favorite vendor with purchase order summary.

#### Policies

- **[VendorProfilePolicy](/entities/vendorprofilepolicy)** - Vendor profile access control (93 lines):
  - `create()`, `update()`, `view()` - Vendor can only access their own profile
  - `updateContacts()`, `updateCertificates()`, `updateTypesAndCategories()` - Section-specific updates
  - `deleteContact()`, `deleteCertificates()` - Delete permissions

#### Middleware

- **[VendorVerified](/entities/vendorverified-middleware)** - Middleware to ensure vendor is verified and not rejected.

#### Notifications

- **[VendorApproveNotification](/entities/vendorapprovenotification)** - Sent to vendor on approval (mail + database).
- **[VendorRejectedNotification](/entities/vendorrejectednotification)** - Sent to vendor on rejection (mail + database).
- **[VendorRegistrationNotification](/entities/vendorregistrationnotification)** - Sent to vendor on registration (mail + database).
- **[AdminVendorApprovedNotification](/entities/adminvendorapprovednotification)** - Sent to admins on vendor approval (database only).
- **[AdminVendorRejectedNotification](/entities/adminvendorrejectednotification)** - Sent to admins on vendor rejection (database only).
- **[AdminVendorRegistrationNotification](/entities/adminvendorregistrationnotification)** - Sent to admins on new vendor registration (database only).

#### Mail

- **[VendorWelcome](/entities/vendorwelcome-mail)** - Welcome email for new vendor registration.
- **[VendorVerified](/entities/vendorverified-mail)** - Verification email for approved vendors.

...

## Dependencies & Graph Links

### Direct Dependencies

- **[User](/entities/user-model)** - Vendors belong to users
- **[Category](/entities/category-model)** - Vendors have many-to-many relationship with categories
- **[VendorType](/entities/vendortype-model)** - Vendors have many-to-many relationship with vendor types
- **[Product](/entities/product-domain)** - Vendors have many products
- **[Subscription](/entities/subscription-model)** - Vendors can have subscriptions for boost scores

### Cross-Domain Connections

- **[Document](/entities/document-model)** - Polymorphic relationship for vendor documents
- **[Certificate](/entities/certificate-model)** - Polymorphic relationship for vendor certificates
- **[ContactPerson](/entities/contactperson-model)** - Polymorphic relationship for vendor contacts
- **[Review](/entities/review-model)** - Polymorphic relationship for vendor reviews
- **[Rfq](/entities/rfq-model)** - Vendors receive RFQs
- **Quotation** - Vendors submit quotations
- **[PurchaseOrder](/entities/purchaseorder-domain)** - Vendors receive purchase orders
- **[Notification](/entities/notification-domain)** - Vendor registration, approval, rejection notifications

...