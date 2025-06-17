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
        
        # Test erasing multiple todos at once
        todo1 = self.mock_store.add(Todo(description="Todo 1"))
        todo2 = self.mock_store.add(Todo(description="Todo 2"))
        todo3 = self.mock_store.add(Todo(description="Todo 3"))
        
        # Erase two of them
        result = self.runner.invoke(cli, ['e', todo1.id, todo2.id, '--force'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Erased', result.output)
        self.assertIn('2', result.output)
        self.assertIn('todos', result.output)
        
        # Verify only todo3 remains
        result = self.runner.invoke(cli, ['l'])
        self.assertNotIn('Todo 1', result.output)
        self.assertNotIn('Todo 2', result.output)
        self.assertIn('Todo 3', result.output)
        
        # Test erasing all todos
        result = self.runner.invoke(cli, ['e', '--all', '--force'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Erased', result.output)
        
        # Verify all todos are gone
        result = self.runner.invoke(cli, ['l'])
        self.assertIn('No todos found', result.output)


    def test_modify_priority(self):
        """Test modifying todo priorities."""
        # Add some test todos
        self.runner.invoke(cli, ['a', 'Todo 1', '-p', 'low'])
        self.runner.invoke(cli, ['a', 'Todo 2', '-p', 'medium'])
        self.runner.invoke(cli, ['a', 'Todo 3', '-p', 'high'])
        
        # List todos to get their IDs
        list_result = self.runner.invoke(cli, ['l'])
        self.assertEqual(list_result.exit_code, 0)
        
        # Modify a single todo's priority
        result = self.runner.invoke(cli, ['m', '0', '-p', 'high'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Updated priority to high', result.output)
        
        # Verify the priority was changed
        show_result = self.runner.invoke(cli, ['s', '0'])
        self.assertEqual(show_result.exit_code, 0)
        self.assertIn('Priority: high', show_result.output)
        
        # Modify multiple todos at once
        result = self.runner.invoke(cli, ['m', '1', '2', '-p', 'low'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Updated priority to low for 2 todos', result.output)
        
        # Verify all priorities were changed
        show_result = self.runner.invoke(cli, ['s', '1'])
        self.assertEqual(show_result.exit_code, 0)
        self.assertIn('Priority: low', show_result.output)
        
        show_result = self.runner.invoke(cli, ['s', '2'])
        self.assertEqual(show_result.exit_code, 0)
        self.assertIn('Priority: low', show_result.output)
        
        # Test modifying all todos
        result = self.runner.invoke(cli, ['m', '-a', '-p', 'medium'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Updated priority to medium for', result.output)
        
        # Verify all priorities were changed to medium
        list_result = self.runner.invoke(cli, ['l'])
        self.assertEqual(list_result.exit_code, 0)
        self.assertNotIn('high', list_result.output)
        self.assertNotIn('low', list_result.output)
        
    def test_shorthand_priority(self):
        """Test using shorthand priority options (h, m, l)."""
        # Test adding with shorthand priorities
        result = self.runner.invoke(cli, ['a', 'High priority todo', '-p', 'h'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Added todo', result.output)
        self.assertIn('high', result.output)
        
        result = self.runner.invoke(cli, ['a', 'Medium priority todo', '-p', 'm'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Added todo', result.output)
        self.assertIn('medium', result.output)
        
        result = self.runner.invoke(cli, ['a', 'Low priority todo', '-p', 'l'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Added todo', result.output)
        self.assertIn('low', result.output)
        
        # Test modifying with shorthand priorities
        # First, get the IDs
        list_result = self.runner.invoke(cli, ['l'])
        self.assertEqual(list_result.exit_code, 0)
        
        # Modify a todo from high to low using shorthand
        result = self.runner.invoke(cli, ['m', '0', '-p', 'l'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Updated priority to low', result.output)
        
        # Verify the change
        show_result = self.runner.invoke(cli, ['s', '0'])
        self.assertEqual(show_result.exit_code, 0)
        self.assertIn('Priority: low', show_result.output)

if __name__ == "__main__":
    unittest.main()
