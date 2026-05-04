---
aliases: [Boq]
tags: [laravel, backend, auto-generated, model, boq]
---

# Boq Model

The root entity for a Bill of Quantities. It belongs to a [[Project Model]] and serves as a container for multiple [[BoqSheet Model]] instances.

## Current Architecture & Flow

- **Table**: `boqs`
- **Relationships**:
	- `belongsTo` [[Project Model]]
	- `hasMany` [[BoqSheet Model]]

## Dependencies & Graph Links

- [[Project Model]]
- [[BoqSheet Model]]

## Red Flags & Tech Debt

- **Limited Utility**: Currently acts as a simple wrapper. Most logic resides at the Sheet and Entry levels.
