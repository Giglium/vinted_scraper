---
name: Bug report
about: Create a report
title: ""
labels: bug
assignees: ""
---

## Describe the bug

Description of the bug. Provide any additional information you think might be relevant.

## Steps to reproduce

1. ...
2. ...
3. ...

## Expected behavior

A clear and concise description of what you expected to happen.

## Example

Provide a minimal, copy-pastable example.

```python
    # Your code here
```

## Debug logs

Please enable debug logging and include the complete output. See the [Debugging section in readme](../../README.md) for detailed instructions.

```python
import logging

# Configure logging BEFORE importing vinted_scraper
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s"
)

from vinted_scraper import VintedScraper

# Your code here
```

<details>
<summary>Debug output (click to expand)</summary>
```
# Paste the COMPLETE debug output here
# Include everything from initialization to the error
```
</details>

## Tell us about your environment

- OS: [e.g. Windows, Ubuntu]
- OS Version [e.g. 22]
- Python version [e.g 3.8]

## Other information

[e.g. detailed explanation, stacktraces, related issues, suggestions how to fix, links for us to have context, etc]
