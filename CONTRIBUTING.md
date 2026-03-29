# Contributing to Xander Operator

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/xander-operator.git`
3. Create a branch: `git checkout -b my-feature-branch`
4. Make changes and test
5. Commit: `git commit -am 'Add some feature'`
6. Push: `git push origin my-feature-branch`
7. Open a Pull Request

## Development Setup

- Install Python 3.11+
- Create virtual environment: `python -m venv .venv && source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Install dev dependencies: `pip install -e .[dev]` (if applicable)
- Copy `.env.example` to `.env` and configure as needed
- Run the operator: `python -m xander_operator` (or as documented)

## Code Style

- Follow PEP 8
- Use `black` for formatting
- Use `ruff` for linting
- Type hints encouraged

## Commit Messages

We follow conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.

## Pull Request Process

1. Ensure all tests pass (CI must be green)
2. Update documentation if needed
3. PR must be reviewed by at least one maintainer
4. Squash merge is preferred

## Branch Protection

The `main` branch is protected. Direct pushes are not allowed. All changes must go through PRs with required reviews and passing CI.

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Questions?

Open an issue with the "question" template or reach out via discussions.

---

Thank you for contributing!