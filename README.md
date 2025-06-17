# Todo CLI

A simple, beautiful command-line todo application for developers.

## Features

- ✅ Add todos with descriptions, priorities, and file associations
- 📋 List todos sorted by priority
- ✓ Complete and mark todos as pending
- 🔄 Modify priority of multiple todos at once
- ✨ Erase todos (single or in bulk)
- 🎨 Color-coded priorities and status indicators
- 📁 Associate todos with specific files in your project
- 🔢 Simple numeric IDs (0-99) for easy reference

## Installation

### Using pip

```bash
# Install directly from GitHub
pip install git+https://github.com/Matthew-Jia/todo-cli.git
```

### Development Installation

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

### Homebrew Installation (macOS)

The `homebrew` directory contains a formula for installing via Homebrew:

```bash
# After the project is published to GitHub with a release
brew tap Matthew-Jia/todo-cli
brew install todo-cli
```

## Usage

### Adding a Todo

```bash
todo a "Fix login bug" -p high -f auth.js
```

Options:
- `-p, --priority [high|medium|low|h|m|l]`: Set priority (default: medium)
- `-f, --file PATH`: Associate with a file path

Shorthand priority examples:
```bash
todo a "Fix login bug" -p h     # high priority
todo a "Update docs" -p m       # medium priority
todo a "Minor tweak" -p l       # low priority
```

### Listing Todos

List all todos (sorted by priority):
```bash
todo l
```

List only completed todos:
```bash
todo l -c
# or
todo l --completed
```

List only pending todos:
```bash
todo l -p
# or
todo l --pending
```

Filter by file path (supports partial matching):
```bash
todo l -f auth      # Shows todos with 'auth' in the file path
todo l -f src       # Shows todos in the 'src' directory
todo l -f .js       # Shows todos with JavaScript files
```

Combine filters:
```bash
todo l -p -f src    # Pending todos in src directory
todo l -c -f auth   # Completed todos related to auth
```

### Completing a Todo

```bash
todo c <id>
```

### Marking a Todo as Pending

```bash
todo p <id>
```

### Modifying Todo Priorities

Modify priority of a single todo:
```bash
todo m <id> -p high    # or -p h for short
```

Modify priority of multiple todos at once:
```bash
todo m <id1> <id2> <id3> -p low    # or -p l for short
```

Modify all todos:
```bash
todo m -a -p medium    # or -p m for short
# or
todo m --all --priority medium
```

### Erasing Todos

Erase a single todo (complete and remove):
```bash
todo e <id>
```

Erase multiple todos at once:
```bash
todo e <id1> <id2> <id3>
```

Erase all todos:
```bash
todo e -a
# or
todo e --all
```

Erase all completed todos:
```bash
todo e -c
# or
todo e --completed
```

Erase all pending todos:
```bash
todo e -p
# or
todo e --pending
```

With force (no confirmation):
```bash
todo e -a -f
# or
todo e --all --force
todo e <id1> <id2> <id3> -f
```

### Showing Todo Details

```bash
todo s <id>
```

## Data Storage

Todo data is stored in `~/.todo/todos.json` and is independent of the installation location.

## Running Tests

```bash
# Activate your virtual environment first
source venv/bin/activate

# Run all tests
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
