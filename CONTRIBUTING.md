# Contributing to Vinted Scraper

Contributing to Vinted Scraper

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved.
The community looks forward to your contributions. 🎉

## Table of Contents

- [Contributing to Vinted Scraper](#contributing-to-vinted-scraper)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [I Have a Question](#i-have-a-question)
  - [I Want To Contribute](#i-want-to-contribute)
    - [Legal Notice](#legal-notice)
    - [Reporting Bugs](#reporting-bugs)
      - [Before Submitting a Bug Report](#before-submitting-a-bug-report)
      - [How Do I Submit a Good Bug Report?](#how-do-i-submit-a-good-bug-report)
    - [Suggesting Enhancements](#suggesting-enhancements)
      - [Before Submitting an Enhancement](#before-submitting-an-enhancement)
      - [How Do I Submit a Good Enhancement Suggestion?](#how-do-i-submit-a-good-enhancement-suggestion)
    - [Your First Code Contribution](#your-first-code-contribution)
      - [Prerequisites](#prerequisites)
      - [Submitting a Changes](#submitting-a-changes)
      - [Makefile](#makefile)
        - [GitHub Actions (Local Testing with act)](#github-actions-local-testing-with-act)
  - [Attribution](#attribution)

## Code of Conduct

This project and everyone participating in it is governed by the
[Vinted Scraper Code of Conduct](https://github.com/Giglium/vinted_scraper/blob/main/CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to <>.

## I Have a Question

> If you want to ask a question, we assume that you have read the available [Documentation](https://giglium.github.io/vinted_scraper/vinted_scraper.html).

Before you ask a question, it is best to search for existing [Issues](https://github.com/Giglium/vinted_scraper/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/Giglium/vinted_scraper/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (Python, uv, etc), depending on what seems relevant.

We will then take care of the issue as soon as possible.

## I Want To Contribute

### Legal Notice

When contributing to this project, you must agree that you have authored 100% of the content, that you have the necessary rights to the content and that the content you contribute may be provided under the project licence.

### Reporting Bugs

#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment components/versions (Make sure that you have read the [documentation](https://giglium.github.io/vinted_scraper/vinted_scraper.html). If you are looking for support, you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/Giglium/vinted_scraper/issues?q=label%3Abug).
- Also make sure to search the internet (including Stack Overflow) to see if users outside of the GitHub community have discussed the issue.
- Collect information about the bug:
  - Stack trace (Traceback)
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
  - Version of the interpreter, compiler, SDK, runtime environment, package manager, depending on what seems relevant.
  - Possibly your input and the output
  - Can you reliably reproduce the issue? And can you also reproduce it with older versions?

#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](https://github.com/Giglium/vinted_scraper/issues/new). (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the _reproduction steps_ that someone else can follow to recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Relevant code snippets or error messages

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Vinted Scraper, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation](https://giglium.github.io/vinted_scraper/vinted_scraper.html) carefully and find out if the functionality is already covered, maybe by an individual configuration.
- Perform a [search](https://github.com/Giglium/vinted_scraper/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset. If you're just targeting a minority of users, consider writing an add-on/plugin library.

#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/Giglium/vinted_scraper/issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- **Explain why this enhancement would be useful** to most Vinted Scraper users. You may also want to point out the other projects that solved it better and which could serve as inspiration.

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- Clear description of the proposed feature
- Use case and motivation
- Possible implementation approach (optional)

### Your First Code Contribution

#### Prerequisites

- Python 3.14
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Docker (optional, but recommended)
- [act](https://github.com/nektos/act) (optional, for testing GitHub Actions locally)

#### Submitting a Changes

- Fork the repository on GitHub
- Clone your fork locally
  ```bash
  git clone https://github.com/Giglium/vinted_scraper.git
  cd vinted_scraper
  ```
- Set up your development environment
  ```bash
  uv sync
  ```

> This will install all project dependencies including development dependencies defined in `pyproject.toml`.

- Create a new branch for your changes
- Make your changes and test them
- Submit a pull request

#### Makefile

The project uses a Makefile to simplify common development tasks. Here are the available commands:

- **`make help`** - Show basic command help
- **`make test`** - Run all unit tests
- **`make coverage`** - Run tests with coverage report (generates HTML report in `htmlcov/`)
- **`make quickstarts`** - Run example scripts that interact directly with the Vinted API
- **`make fmt`** - Format Python code using `black`, `isort`, and `no_implicit_optional`
- **`make lint`** - Run Super Linter (requires Docker) for comprehensive code analysis

##### GitHub Actions (Local Testing with act)

- **`make act.test`** - Run test workflow locally
- **`make act.coverage`** - Run coverage workflow locally
- **`make act.lint`** - Run linter workflow locally
- **`make act.quickstarts`** - Run quickstarts workflow locally
- **`make act.build`** - Run release workflow locally
- **`make act.docs`** - Run docs workflow locally

## Attribution

This guide is based on the [contributing.md](https://contributing.md/generator)!
