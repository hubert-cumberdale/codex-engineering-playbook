# Risks

- **Doc drift:** release notes or governance language could misstate enforcement or artifacts.
  - Mitigation: cross-check against deterministic review runner, pre-push hook, and CI workflow behavior.
- **Version mismatch:** release notes version could conflict with tags or naming conventions.
  - Mitigation: derive the next minor version from the latest `v*` tag and existing `docs/releases` patterns.
