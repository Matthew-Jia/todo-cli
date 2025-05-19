"""Tests for the CLI interface."""
import os
import tempfile
import unittest
from unittest.mock import patch
from click.testing import CliRunner

from todo.cli import cli  # Import the cli group instead of individual functions
from todo.models import Todo, TodoStore, Priority, Status


class TestCli(unittest.TestCase):
    def setUp(self):
        """Set up a test environment."""
        # Create a temporary file for the todo store
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Create a CLI runner
        self.runner = CliRunner()
        
        # Patch the TodoStore to use our temporary file
        self.patcher = patch('todo.cli.store', TodoStore(self.temp_file.name))
        self.mock_store = self.patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        os.unlink(self.temp_file.name)
    
    def test_add_todo(self):
        """Test adding a todo."""
        result = self.runner.invoke(cli, ['a', 'Test todo'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Added todo', result.output)
        
        # Check with priority and file
        result = self.runner.invoke(cli, ['a', 'Test with options', '-p', 'high', '-f', 'test.py'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Added todo', result.output)
        
        # Verify todos were added by listing them
        result = self.runner.invoke(cli, ['l'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Test todo', result.output)
        self.assertIn('Test with options', result.output)
        self.assertIn('high', result.output)
        self.assertIn('test.py', result.output)
    
    def test_list_todos(self):
        """Test listing todos with different filters."""
        # Add some test todos
        self.mock_store.add(Todo(description="Pending task 1"))
        self.mock_store.add(Todo(description="Pending task 2", file_path="file.py"))
        
        completed = Todo(description="Completed task")
        completed.mark_complete()
        self.mock_store.add(completed)
        
        # Test basic listing
        result = self.runner.invoke(cli, ['l'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Pending task 1', result.output)
        self.assertIn('Pending task 2', result.output)
        self.assertIn('Completed task', result.output)
        
        # Test filtering by status
        result = self.runner.invoke(cli, ['l', '--completed'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn('Pending task', result.output)
        self.assertIn('Completed task', result.output)
        
        result = self.runner.invoke(cli, ['l', '--pending'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Pending task', result.output)
        self.assertNotIn('Completed task', result.output)
        
        # Test filtering by file
        result = self.runner.invoke(cli, ['l', '--file', 'file.py'])
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn('Pending task 1', result.output)
        self.assertIn('Pending task 2', result.output)
        self.assertNotIn('Completed task', result.output)
    
    def test_complete_todo(self):
        """Test completing a todo."""
        todo = self.mock_store.add(Todo(description="Task to complete"))
        
        result = self.runner.invoke(cli, ['c', todo.id])
        self.assertEqual(result.exit_code, 0)
        # Check for partial string matches instead of exact match
        self.assertIn('Completed', result.output)
        self.assertIn('Task to complete', result.output)
        
        # Verify it's marked as completed
        result = self.runner.invoke(cli, ['l', '--completed'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Task to complete', result.output)
        
        # Test completing non-existent todo
        result = self.runner.invoke(cli, ['c', 'non-existent-id'])
        self.assertNotEqual(result.exit_code, 0)  # Should exit with error
        self.assertIn('not found', result.output)
    
    def test_mark_pending_todo(self):
        """Test marking a todo as pending."""
        # First add and complete a todo
        todo = self.mock_store.add(Todo(description="Task to mark pending"))
        self.mock_store.mark_complete(todo.id)
        
        # Verify it's completed
        result = self.runner.invoke(cli, ['l', '--completed'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Task to mark pending', result.output)
        
        # Mark as pending
        result = self.runner.invoke(cli, ['p', todo.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('pending', result.output.lower())
        self.assertIn('Task to mark pending', result.output)
        
        # Verify it's now pending
        result = self.runner.invoke(cli, ['l', '--pending'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Task to mark pending', result.output)
        
        # Test marking a non-completed todo as pending
        todo2 = self.mock_store.add(Todo(description="Already pending task"))
        result = self.runner.invoke(cli, ['p', todo2.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('already pending', result.output.lower())
        
        # Test marking non-existent todo as pending
        result = self.runner.invoke(cli, ['p', 'non-existent-id'])
        self.assertNotEqual(result.exit_code, 0)  # Should exit with error
        self.assertIn('not found', result.output)
    
    # Removed test_remove_todo as the 'r' command has been removed
    # The erase command (e) now covers this functionality
    
    def test_show_todo(self):
        """Test showing todo details."""
        todo = self.mock_store.add(Todo(
            description="Detailed task",
            priority=Priority.HIGH,
            file_path="important.py"
        ))
        
        result = self.runner.invoke(cli, ['s', todo.id])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Detailed task', result.output)
        self.assertIn('high', result.output)
        self.assertIn('important.py', result.output)
        
        # Test showing non-existent todo
        result = self.runner.invoke(cli, ['s', 'non-existent-id'])
        self.assertNotEqual(result.exit_code, 0)  # Should exit with error
        self.assertIn('not found', result.output)
    
    def test_erase_todo(self):
        """Test erasing a todo."""
        todo = self.mock_store.add(Todo(description="Task to erase"))
        
        # Test with confirmation (automatically saying yes)
        result = self.runner.invoke(cli, ['e', todo.id], input='y\n')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Erased', result.output)
        self.assertIn('Task to erase', result.output)
        
        # Verify it's gone
        result = self.runner.invoke(cli, ['l'])
        self.assertNotIn('Task to erase', result.output)
        
        # Test erasing all todos
        self.mock_store.add(Todo(description="Todo 1"))
        self.mock_store.add(Todo(description="Todo 2"))
        
        result = self.runner.invoke(cli, ['e', '--all', '--force'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Erased', result.output)
        
        # Verify all todos are gone
        result = self.runner.invoke(cli, ['l'])
        self.assertIn('No todos found', result.output)


if __name__ == "__main__":
    unittest.main()
