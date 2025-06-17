# Changelog

All notable changes to the Todo CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for erasing multiple todos at once with a single command
- Short command flags as alternatives to long options (e.g., `-c` for `--completed`, `-p` for `--pending`, `-a` for `--all`)
- Force flag (`-f`) for erasing todos without confirmation

### Changed
- Improved README documentation with clearer examples
- Enhanced command syntax documentation showing both short and long option formats
- Updated example commands for better clarity

### Fixed
- Fixed file path filtering in list command

## [1.0.0] - 2025-05-22
- Initial release
- Add todos with descriptions, priorities, and file associations
- List todos sorted by priority
- Complete and mark todos as pending
- Erase todos (single or in bulk)
- Color-coded priorities and status indicators
- Associate todos with specific files in your project
- Simple numeric IDs (0-99) for easy reference

[Unreleased]: https://github.com/Matthew-Jia/todo-cli/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Matthew-Jia/todo-cli/releases/tag/v1.0.0
