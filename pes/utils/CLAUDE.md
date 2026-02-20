# CLAUDE.md - Utilities

## Scope

Shared utility functions used across modules.

## Status

**TODO** - Not yet implemented.

Utilities currently inline in individual modules.

## Candidate Functions

When implementing, consider consolidating:

- Token counting/estimation
- Text truncation with budget
- Progress display helpers
- File path utilities
- Retry decorators
- Timing utilities

## Guidelines

- Only add utilities used by 2+ modules
- Keep functions pure where possible
- No module-specific logic
- Comprehensive docstrings
- Unit tests for each utility
