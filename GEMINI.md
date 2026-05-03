# System Instructions: Markdown Documentation Maintenance

## Overview

This document outlines the strict processing rules for editing, creating, and maintaining Markdown files in this repository. Ensure all automated edits adhere to the following standards.

## 1. Link Resolution and Formatting

- **Prohibited Format**: Do not use Obsidian-style wiki links (e.g., `[[Filename]]`).
- **Required Format**: Use standard Markdown relative paths (e.g., `[Link Text](path/to/file.md)`).
- **Validation**: When parsing existing files, convert all identified wiki links to standard Markdown links.
- **Accuracy**: Ensure relative paths and case sensitivity exactly match the target file structure.

## 2. YAML Frontmatter Standards

- **Requirement**: Every Markdown file must contain a valid YAML frontmatter block at the top of the file.
- **Minimum Fields**: If frontmatter is missing, generate it. It must include a `title` field derived from the target file name or the primary Level 1 heading (`#`).
- **Format**:
  ````yaml
  ---
  title: "Document Title"
  ---
  ```
  ````
- **Preservation**: Retain all existing frontmatter fields (e.g., tags, descriptions, aliases) during document modifications.

## 3. Scope of Modifications

- **Formatting Only**: Restrict edits strictly to link formatting, frontmatter generation, and markdown syntax correction.
- **Content Integrity**: Do not modify, summarize, or alter the core text, context, or intent of the source notes.
