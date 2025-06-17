from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
import json
import os
import heapq  # For min heap operations


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Todo:
    description: str
    priority: Priority = Priority.MEDIUM
    file_path: Optional[str] = None
    id: str = field(default="0")  # Default ID, will be assigned by TodoStore
    status: Status = Status.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def mark_complete(self) -> None:
        """Mark the todo as completed with current timestamp."""
        self.status = Status.COMPLETED
        self.completed_at = datetime.now().isoformat()
        
    def mark_pending(self) -> None:
        """Mark the todo as pending, removing completion timestamp."""
        self.status = Status.PENDING
        self.completed_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Todo to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        """Create a Todo instance from a dictionary."""
        # Convert string values to enum types
        if "priority" in data:
            data["priority"] = Priority(data["priority"])
        if "status" in data:
            data["status"] = Status(data["status"])
        return cls(**data)


class TodoStore:
    def __init__(self, storage_path: str = None):
        """Initialize the TodoStore with a path to the storage file."""
        if storage_path is None:
            # Check for development mode environment variable
            if os.environ.get("TODO_DEV_MODE") == "1":
                home_dir = os.path.expanduser("/Users/jiamatt/todo-proj/todo-cli")
            else:
                home_dir = os.path.expanduser("~")
            
            storage_dir = os.path.join(home_dir, ".todo")
            os.makedirs(storage_dir, exist_ok=True)
            storage_path = os.path.join(storage_dir, "todos.json")
        
        self.storage_path = storage_path
        self.todos: Dict[str, Todo] = {}
        self.available_ids = list(range(100))  # IDs from 0-99
        heapq.heapify(self.available_ids)  # Convert to min heap
        self._load()

    def _load(self) -> None:
        """Load todos from the storage file."""
        if os.path.exists(self.storage_path) and os.path.getsize(self.storage_path) > 0:
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.todos = {
                        todo_id: Todo.from_dict(todo_data)
                        for todo_id, todo_data in data.items()
                    }
                
                # Rebuild the available IDs heap
                used_ids = set(int(todo_id) for todo_id in self.todos.keys())
                self.available_ids = [i for i in range(100) if i not in used_ids]
                heapq.heapify(self.available_ids)
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading todos: {e}")
                # Initialize with empty dict if file is corrupted
                self.todos = {}
        else:
            self.todos = {}

    def _save(self) -> None:
        """Save todos to the storage file."""
        try:
            with open(self.storage_path, "w") as f:
                serialized = {
                    todo_id: todo.to_dict()
                    for todo_id, todo in self.todos.items()
                }
                json.dump(serialized, f, indent=2)
        except IOError as e:
            print(f"Error saving todos: {e}")

    def add(self, todo: Todo) -> Todo:
        """Add a new todo to the store."""
        if not self.available_ids:
            raise ValueError("Maximum number of todos (100) reached. Please remove some todos first.")
        
        # Get the lowest available ID
        next_id = str(heapq.heappop(self.available_ids))
        todo.id = next_id
        self.todos[next_id] = todo
        self._save()
        return todo

    def get(self, todo_id: str) -> Optional[Todo]:
        """Get a todo by ID."""
        return self.todos.get(todo_id)

    def get_all(self) -> List[Todo]:
        """Get all todos."""
        return list(self.todos.values())

    def update(self, todo: Todo) -> Todo:
        """Update an existing todo."""
        if todo.id not in self.todos:
            raise ValueError(f"Todo with ID {todo.id} not found")
        self.todos[todo.id] = todo
        self._save()
        return todo

    def remove(self, todo_id: str) -> bool:
        """Remove a todo by ID."""
        if todo_id in self.todos:
            del self.todos[todo_id]
            # Return the ID to the available pool
            heapq.heappush(self.available_ids, int(todo_id))
            self._save()
            return True
        return False

    def mark_complete(self, todo_id: str) -> Optional[Todo]:
        """Mark a todo as completed."""
        todo = self.get(todo_id)
        if todo:
            todo.mark_complete()
            self._save()
            return todo
        return None
        
    def mark_pending(self, todo_id: str) -> Optional[Todo]:
        """Mark a todo as pending (uncomplete it)."""
        todo = self.get(todo_id)
        if todo:
            todo.mark_pending()
            self._save()
            return todo
        return None

    def filter(self, status: Optional[Status] = None, 
               file_path: Optional[str] = None) -> List[Todo]:
        """Filter todos by status and/or file path.
        
        Args:
            status: Filter by todo status (completed or pending)
            file_path: Filter by file path (supports partial matching)
        """
        filtered = self.get_all()
        
        if status is not None:
            filtered = [todo for todo in filtered if todo.status == status]
        
        if file_path is not None:
            # Support partial matching for file paths
            filtered = [todo for todo in filtered if todo.file_path and file_path in todo.file_path]
            
        return filtered
