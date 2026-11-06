# Changelog

This file records published versions and prepared release candidates of Prismo.
Pre-release entries describe experimental scope and retain support limitations.

## 0.1.0-alpha.3 — release candidate

- Plan Colors granularity through functional and evolution coverage, without a fixed
  number of steps, preserving justified component-specific colors.
- Add incremental coverage validation, alias traces and final sRGB perceptual reports;
  keep calculation, declared visual evidence and conformance separate.
- Add `palette --require-coverage`, stdin plans via `--plan -`, JSON contract help
  and field diagnostics while preserving legacy plans and foundations recovery.
- Require validated affected-use matrices before new color proposals in the guided
  workflow; preserve approval boundaries and prevent implicit migrations.
- Keep internal working plans local and preserve compact release evidence in docs.

The candidate remains experimental. Visual review, complete accessibility,
context-reading efficiency and broader conversational reliability remain limited.
No tag or GitHub Release has been created as part of this preparation.
See the [alpha.3 release notes](docs/experimental-release-notes-0.1.0-alpha.3.md).

## 0.1.0-alpha.2 — release candidate

- Add automatic, additive foundations execution with a persistent checklist,
  ordered stages, safe resume, conflict detection, and interrupted transaction recovery.
- Add optional recommended and custom token naming policies across the six operations,
  preserving existing names and behavior when no policy is configured.
- Block other foundations while an interrupted transaction is pending and recover
  the affected stage before other requested work.
- Document conversational coverage, legacy compatibility, and experimental limits.

The candidate remains experimental: DTCG and audit coverage are partial; visual,
accessibility, platform, and broader conversational validation remain necessary.
See the [alpha.2 release notes](docs/experimental-release-notes-0.1.0-alpha.2.md).

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
