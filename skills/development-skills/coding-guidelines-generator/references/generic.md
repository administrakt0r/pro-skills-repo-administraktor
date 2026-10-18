# General Engineering Guidelines

> Verified: 2026-10-18, Portable Engineering Standard
> Note: Applied for unmapped or generic tech stacks. Follow the repository's existing conventions.

## Code Conventions & Changes
- **Smallest Complete Change**: Implement the minimal, cohesive change that satisfies requirements. Avoid speculative abstractions or tangential refactorings.
- **Convention Adherence**: Follow existing project naming, module layout, and file organization. If unsure, match neighboring files.

## Error Handling & Boundaries
- **Explicit Failures**: Handle and propagate errors explicitly. Fail with actionable error context; do not swallow exceptions silently with empty handlers.
- **Input Validation**: Validate external data, file inputs, and environment configurations at boundaries before processing.

## Verification
- Identify the repository's test runner and linting commands from manifests or documentation. Run checks and report verified results.
