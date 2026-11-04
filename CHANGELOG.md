# Changelog

This file records published versions of Prismo. Pre-release entries describe
experimental releases and retain their documented support limitations.

## 0.1.0-alpha.1 — 2026-11-04

Initial experimental release prepared from the stabilized, previously unversioned
project. This baseline represents the complete approved initial state; it does not
reconstruct an artificial development history.

- Include the six operations: init, foundations, tokens, create, document, and audit.
- Include deterministic helpers for Colors, Typography, Spacing, Borders, and
  Elevation, plus Storybook renderers and Docusaurus documentation templates.
- Preserve existing-project compatibility, preview/approval boundaries, and
  read-only audit behavior.
- Include reproducible development dependencies, the distribution smoke test,
  installer tests, and the test runner's explicit TAP reporter.
- Establish Conventional Commits with required explanatory bodies, authorized AI
  coauthor trailers, and preservation of the user's Git author identity.

Validation before version metadata: 236 Python tests, 53 JavaScript tests, clean
npm ci with esbuild lifecycle, distribution smoke, installer, and Skill validator.
Release-candidate checks are recorded separately before publication.

See the [experimental release notes](docs/experimental-release-notes.md) for
requirements, supported scope, and known limitations. Linux is the validated
platform; DTCG support is partial and visual/accessibility, Flutter/device, and
complete conversational validation remain limited.
