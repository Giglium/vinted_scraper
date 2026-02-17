# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.x.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please send an email to the maintainers. You can find the contact information in the [pyproject.toml](pyproject.toml) file or on the [GitHub repository](https://github.com/Giglium/vinted_scraper).

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

We will acknowledge your email within 48 hours and send a more detailed response within 7 days indicating the next steps in handling your report.

## Security Update Process

1. The security report is received and assigned to a primary handler
2. The problem is confirmed and affected versions are determined
3. Code is audited to find any similar problems
4. Fixes are prepared for all supported versions
5. New versions are released and announced

## Security Best Practices

When using this library:

- Always use the latest stable version
- Never commit credentials or API keys to version control
- Be cautious when scraping and respect rate limits
- Review the code before using in production environments
- Keep dependencies up to date

## Disclosure Policy

When we receive a security bug report, we will:

- Confirm the problem and determine affected versions
- Audit code to find similar problems
- Prepare fixes for all supported versions
- Release new versions as soon as possible

## Comments on This Policy

If you have suggestions on how this process could be improved, please submit a pull request.
