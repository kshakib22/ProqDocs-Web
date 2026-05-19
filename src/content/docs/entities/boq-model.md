---
aliases: [Boq]
tags: [laravel, backend, auto-generated, model, boq]
title: "Boq Model"
---

# Boq Model

The root entity for a Bill of Quantities. It belongs to a [Project Model](/ProqDocs-Web/entities/project-domain/) and serves as a container for multiple [BoqSheet Model](/ProqDocs-Web/entities/boq-sheet-model/) instances.

## Current Architecture & Flow

- **Table**: `boqs`
- **Relationships**:
	- `belongsTo` [Project Model](/ProqDocs-Web/entities/project-domain/)
	- `hasMany` [BoqSheet Model](/ProqDocs-Web/entities/boq-sheet-model/)

## Dependencies & Graph Links

- [Project Model](/ProqDocs-Web/entities/project-domain/)
- [BoqSheet Model](/ProqDocs-Web/entities/boq-sheet-model/)

## Red Flags & Tech Debt

- **Limited Utility**: Currently acts as a simple wrapper. Most logic resides at the Sheet and Entry levels.
