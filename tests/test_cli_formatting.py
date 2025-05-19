"""Tests for the CLI formatting functionality."""
import os
import tempfile
import unittest
from unittest.mock import patch
from click.testing import CliRunner

from todo.cli import cli
from todo.models import Todo, TodoStore, Priority, Status


class TestCliFormatting(unittest.TestCase):
    def setUp(self):
        """Set up a test environment."""
        # Create a temporary file for the todo store
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Create a CLI runner
        self.runner = CliRunner()
        
        # Patch the TodoStore to use our temporary file
        self.store_patcher = patch('todo.cli.store', TodoStore(self.temp_file.name))
        self.mock_store = self.store_patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.store_patcher.stop()
        os.unlink(self.temp_file.name)
    
    def test_list_formatting(self):
        """Test that list_todos formats output correctly."""
        # Add some test todos
        self.mock_store.add(Todo(
            description="High priority task",
            priority=Priority.HIGH
        ))
        self.mock_store.add(Todo(
            description="Medium priority task",
            priority=Priority.MEDIUM,
            file_path="test.py"
        ))
        completed = Todo(
            description="Completed low priority task",
            priority=Priority.LOW
        )
        completed.mark_complete()
        self.mock_store.add(completed)
        
        # Call the command
        result = self.runner.invoke(cli, ['l'])
        
        # Check output
        self.assertEqual(result.exit_code, 0)
        output = result.output
        
        # Verify all todos are listed
        self.assertIn("High priority task", output)
        self.assertIn("Medium priority task", output)
        self.assertIn("Completed low priority task", output)
        
        # Verify priority indicators are present (may not see actual emoji in test output)
        self.assertIn("high", output)
        self.assertIn("medium", output)
        self.assertIn("low", output)
        
        # Verify file path is shown
        self.assertIn("test.py", output)
    
    def test_show_formatting(self):
        """Test that show formats output correctly."""
        # Add a test todo
        todo = self.mock_store.add(Todo(
            description="Detailed task view",
            priority=Priority.HIGH,
            file_path="important.py"
        ))
        
        # Call the command
        result = self.runner.invoke(cli, ['s', todo.id])
        
        # Check output
        self.assertEqual(result.exit_code, 0)
        output = result.output
        
        # Verify todo details are shown
        self.assertIn("Detailed task view", output)
        self.assertIn("high", output)
        self.assertIn("important.py", output)
        self.assertIn("Todo Details", output)  # Panel title
    
    def test_truncation(self):
        """Test that long descriptions are truncated in list view."""
        # Add a todo with a very long description
        long_desc = "This is a very long description that should be truncated in the list view " * 10
        self.mock_store.add(Todo(description=long_desc))
        
        # Call the command
        result = self.runner.invoke(cli, ['l'])
        
        # Check output
        self.assertEqual(result.exit_code, 0)
        output = result.output
        
        # Verify the description is truncated
        self.assertIn("...", output)
        # The full description should not appear in the output
        self.assertNotIn(long_desc, output)
    
    def test_empty_list(self):
        """Test formatting when no todos are found."""
        # Call the command with an empty store
        result = self.runner.invoke(cli, ['l'])
        
        # Check output
        self.assertEqual(result.exit_code, 0)
        output = result.output
        
        # Verify the "no todos" message
        self.assertIn("No todos found", output)


if __name__ == "__main__":
    unittest.main()
