# Branching Policy

WeaR Lang uses a simple two-tier integration model.

- `main` — stable/release branch. Do not use it for active compiler experimentation.
- `development` — active integration branch for engineering changes.
- `feature/*` — short-lived branches created from `development` for isolated work.

All feature pull requests target `development`. A change reaches `main` only after it has been integrated into `development`, validated, and intentionally promoted as a stable release.
