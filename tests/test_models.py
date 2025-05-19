import os
import tempfile
import unittest
from datetime import datetime
from todo.models import Todo, TodoStore, Priority, Status


class TestTodo(unittest.TestCase):
    def test_todo_creation(self):
        """Test creating a Todo with default and custom values."""
        # Test with default values
        todo = Todo(description="Test todo")
        self.assertEqual(todo.description, "Test todo")
        self.assertEqual(todo.priority, Priority.MEDIUM)
        self.assertEqual(todo.status, Status.PENDING)
        self.assertIsNone(todo.file_path)
        self.assertIsNone(todo.completed_at)
        self.assertTrue(todo.id)  # ID should be generated
        
        # Test with custom values
        todo = Todo(
            description="Custom todo",
            priority=Priority.HIGH,
            file_path="test.py",
            id="custom-id"
        )
        self.assertEqual(todo.description, "Custom todo")
        self.assertEqual(todo.priority, Priority.HIGH)
        self.assertEqual(todo.file_path, "test.py")
        self.assertEqual(todo.id, "custom-id")

    def test_mark_complete(self):
        """Test marking a todo as completed."""
        todo = Todo(description="Test todo")
        self.assertEqual(todo.status, Status.PENDING)
        self.assertIsNone(todo.completed_at)
        
        todo.mark_complete()
        self.assertEqual(todo.status, Status.COMPLETED)
        self.assertIsNotNone(todo.completed_at)
        
        # Verify completed_at is a valid ISO format date
        try:
            datetime.fromisoformat(todo.completed_at)
        except ValueError:
            self.fail("completed_at is not a valid ISO format date")
            
    def test_mark_pending(self):
        """Test marking a todo as pending."""
        # First mark as completed
        todo = Todo(description="Test todo")
        todo.mark_complete()
        self.assertEqual(todo.status, Status.COMPLETED)
        self.assertIsNotNone(todo.completed_at)
        
        # Then mark as pending
        todo.mark_pending()
        self.assertEqual(todo.status, Status.PENDING)
        self.assertIsNone(todo.completed_at)

    def test_todo_serialization(self):
        """Test converting Todo to and from dict."""
        original = Todo(
            description="Serialize me",
            priority=Priority.LOW,
            file_path="data.json"
        )
        
        # Convert to dict
        todo_dict = original.to_dict()
        self.assertEqual(todo_dict["description"], "Serialize me")
        self.assertEqual(todo_dict["priority"], "low")
        self.assertEqual(todo_dict["file_path"], "data.json")
        
        # Convert back to Todo
        restored = Todo.from_dict(todo_dict)
        self.assertEqual(restored.description, original.description)
        self.assertEqual(restored.priority, original.priority)
        self.assertEqual(restored.file_path, original.file_path)
        self.assertEqual(restored.id, original.id)


class TestTodoStore(unittest.TestCase):
    def setUp(self):
        """Create a temporary file for testing storage."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = TodoStore(self.temp_file.name)

    def tearDown(self):
        """Clean up the temporary file."""
        os.unlink(self.temp_file.name)

    def test_add_and_get(self):
        """Test adding and retrieving todos."""
        todo = Todo(description="Test add")
        added = self.store.add(todo)
        
        # Test get by ID
        retrieved = self.store.get(todo.id)
        self.assertEqual(retrieved.description, "Test add")
        self.assertEqual(retrieved.id, todo.id)
        
        # Test get all
        all_todos = self.store.get_all()
        self.assertEqual(len(all_todos), 1)
        self.assertEqual(all_todos[0].id, todo.id)

    def test_update(self):
        """Test updating a todo."""
        todo = self.store.add(Todo(description="Original"))
        
        # Update the todo
        todo.description = "Updated"
        updated = self.store.update(todo)
        
        # Verify the update
        self.assertEqual(updated.description, "Updated")
        retrieved = self.store.get(todo.id)
        self.assertEqual(retrieved.description, "Updated")

    def test_remove(self):
        """Test removing a todo."""
        todo = self.store.add(Todo(description="To be removed"))
        
        # Verify it exists
        self.assertIsNotNone(self.store.get(todo.id))
        
        # Remove it
        result = self.store.remove(todo.id)
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(self.store.get(todo.id))
        
        # Try removing non-existent todo
        result = self.store.remove("non-existent-id")
        self.assertFalse(result)

    def test_mark_complete(self):
        """Test marking a todo as completed."""
        todo = self.store.add(Todo(description="To be completed"))
        
        # Complete the todo
        completed = self.store.mark_complete(todo.id)
        self.assertEqual(completed.status, Status.COMPLETED)
        self.assertIsNotNone(completed.completed_at)
        
        # Verify it's saved
        retrieved = self.store.get(todo.id)
        self.assertEqual(retrieved.status, Status.COMPLETED)
        
        # Try completing non-existent todo
        result = self.store.mark_complete("non-existent-id")
        self.assertIsNone(result)
        
    def test_mark_pending(self):
        """Test marking a todo as pending."""
        # First add and complete a todo
        todo = self.store.add(Todo(description="To be marked pending"))
        self.store.mark_complete(todo.id)
        
        # Verify it's completed
        retrieved = self.store.get(todo.id)
        self.assertEqual(retrieved.status, Status.COMPLETED)
        self.assertIsNotNone(retrieved.completed_at)
        
        # Mark as pending
        pending = self.store.mark_pending(todo.id)
        self.assertEqual(pending.status, Status.PENDING)
        self.assertIsNone(pending.completed_at)
        
        # Verify it's saved
        retrieved = self.store.get(todo.id)
        self.assertEqual(retrieved.status, Status.PENDING)
        self.assertIsNone(retrieved.completed_at)
        
        # Try marking non-existent todo as pending
        result = self.store.mark_pending("non-existent-id")
        self.assertIsNone(result)

    def test_filter(self):
        """Test filtering todos."""
        # Add some todos with different statuses and file paths
        self.store.add(Todo(
            description="Pending task",
            status=Status.PENDING,
            file_path="file1.py"
        ))
        completed = Todo(
            description="Completed task",
            status=Status.PENDING,
            file_path="file2.py"
        )
        completed.mark_complete()
        self.store.add(completed)
        self.store.add(Todo(
            description="Another pending",
            status=Status.PENDING,
            file_path="file1.py"
        ))
        
        # Filter by status
        pending = self.store.filter(status=Status.PENDING)
        self.assertEqual(len(pending), 2)
        
        completed = self.store.filter(status=Status.COMPLETED)
        self.assertEqual(len(completed), 1)
        
        # Filter by file path
        file1_todos = self.store.filter(file_path="file1.py")
        self.assertEqual(len(file1_todos), 2)
        
        # Filter by both
        pending_file1 = self.store.filter(
            status=Status.PENDING,
            file_path="file1.py"
        )
        self.assertEqual(len(pending_file1), 2)

    def test_persistence(self):
        """Test that todos are saved to and loaded from disk."""
        # Add a todo
        todo = self.store.add(Todo(description="Persistent"))
        
        # Create a new store instance with the same file
        new_store = TodoStore(self.temp_file.name)
        
        # Verify the todo was loaded
        loaded = new_store.get(todo.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.description, "Persistent")


if __name__ == "__main__":
    unittest.main()
