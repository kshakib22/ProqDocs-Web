---
aliases: [Boq]
tags: [laravel, backend, auto-generated, model, boq]
title: "Boq Model"
---

# Boq Model

The root entity for a Bill of Quantities. It belongs to a [Project Model](/entities/project-domain) and serves as a container for multiple [BoqSheet Model](/entities/boqsheet-model) instances.

## Current Architecture & Flow

- **Table**: `boqs`
- **Relationships**:
	- `belongsTo` [Project Model](/entities/project-domain)
	- `hasMany` [BoqSheet Model](/entities/boqsheet-model)

## Dependencies & Graph Links

- [Project Model](/entities/project-domain)
- [BoqSheet Model](/entities/boqsheet-model)

## Red Flags & Tech Debt

- **Limited Utility**: Currently acts as a simple wrapper. Most logic resides at the Sheet and Entry levels.
