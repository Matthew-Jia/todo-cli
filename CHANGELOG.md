# Changelog

All notable changes to the Todo CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-06-18
### Added
- Support for completing multiple todos at once by specifying multiple IDs (`todo c 1 2 3`)
- Support for marking multiple todos as pending by specifying multiple IDs (`todo p 1 2 3`)
- `--all` flag for completing all pending todos at once (`todo c --all`)
- `--all` flag for marking all completed todos as pending at once (`todo p --all`)
- Enhanced error handling for mixed valid/invalid todo IDs
- Helpful guidance messages when no arguments are provided to complete/pending commands

### Changed
- Complete and pending commands now accept variable number of todo IDs
- Improved user feedback with detailed success messages showing affected todos
- Enhanced command help text to reflect new multiple ID and --all flag options

### Fixed
- Better error reporting when some todo IDs are invalid while others are valid

## [1.1.0] - 2025-06-17
### Added
- Support for shorthand priority options (h, m, l) in addition to full words (high, medium, low)

### Changed
- Removed confirmation requirement for modifying todo priorities
- Improved README documentation with clearer examples
- Enhanced command syntax documentation showing both short and long option formats

## [1.0.0] - 2025-05-22
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

## [0.1.0] - 2025-05-19
- Initial release
- Add todos with descriptions, priorities, and file associations
- List todos sorted by priority
- Complete and mark todos as pending
- Erase todos (single or in bulk)
- Color-coded priorities and status indicators
- Associate todos with specific files in your project
- Simple numeric IDs (0-99) for easy reference

[Unreleased]: https://github.com/Matthew-Jia/todo-cli/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/Matthew-Jia/todo-cli/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Matthew-Jia/todo-cli/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Matthew-Jia/todo-cli/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/Matthew-Jia/todo-cli/releases/tag/v0.1.0
