# Security Policy

## Supported Versions

Security fixes are applied to the actively developed version on the `development` branch and to the latest stable release on `main`.

## Reporting a Vulnerability

Please do not publish credentials, tokens, private keys, or other sensitive data in a public issue.

Use a private GitHub security report when available. If private reporting is unavailable, open an issue containing only a minimal description and request a private contact channel.

## Repository Hygiene

Generated build artifacts and environment files should remain untracked. Do not commit secrets, credentials, personal data, or local machine configuration.

Removing a sensitive file from the current branch does not erase it from Git history. Any real credential that was ever committed must be revoked or rotated, and history should be rewritten when appropriate.
