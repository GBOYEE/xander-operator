# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- LLM integration with caching (OpenAI and Ollama support)
- HTML reporter via Jinja2 with summary and task details
- New detectors: input validation and safety checks
- Expanded test suite (pytest)
- CLI flag `--report` to generate HTML reports after execution
- automatic log rotation by date

### Changed
- Version bumped to 1.1.0 (development)
- Upgraded dependencies in requirements.txt and pyproject.toml
- README updated with new features and usage

## [1.0.1] - 2026-03-27

### Added
- Initial public release with Playwright browser automation
- Human approval gates for sensitive actions
- Optional vector memory (Chroma/FAISS)
- Structured daily logs in Markdown
- CLI for task queue and vector search

[1.0.1]: https://github.com/GBOYEE/xander-operator/releases/tag/v1.0.1
