# Contributing to Todo CLI

Thank you for considering contributing to Todo CLI! This document provides guidelines and instructions to help you get started.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/Matthew-Jia/todo-cli/issues)
- If not, create a new issue using the bug report template
- Include as much detail as possible: steps to reproduce, expected behavior, actual behavior, and your environment

### Suggesting Features

- Check if the feature has already been suggested in the [Issues](https://github.com/Matthew-Jia/todo-cli/issues)
- If not, create a new issue using the feature request template
- Describe the feature in detail and explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix: `git checkout -b feature/your-feature-name` or `git checkout -b fix/your-bugfix-name`
3. Make your changes
4. Add or update tests as needed
5. Run the tests to make sure everything passes: `python -m unittest discover tests`
6. Commit your changes with a descriptive commit message
7. Push to your fork
8. Create a pull request to the `main` branch of the original repository

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Matthew-Jia/todo-cli.git
cd todo-cli

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Testing

Run all tests:
```bash
python -m unittest discover tests
```

Or use the provided script:
```bash
./run_tests.py
```

## Style Guidelines

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused on a single responsibility

## Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
