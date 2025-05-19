"""Command-line interface for the todo application."""
import click
import shutil
import sys
from typing import Optional, List
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from .models import Todo, TodoStore, Priority, Status


# Initialize the todo store and console
store = TodoStore()
console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Todo CLI - A simple command-line todo application."""
    pass


@cli.command("a", help="Add a new todo")
@click.argument("description")
@click.option("-f", "--file", "file_path", help="Associate with a file path")
@click.option(
    "-p", 
    "--priority", 
    type=click.Choice(["high", "medium", "low"], case_sensitive=False),
    default="medium",
    help="Set priority (default: medium)"
)
def add(description: str, file_path: Optional[str], priority: str):
    """Add a new todo with the given description."""
    try:
        todo = Todo(
            description=description,
            file_path=file_path,
            priority=Priority(priority.lower())
        )
        store.add(todo)
        
        # Show confirmation with color based on priority
        priority_color = {
            Priority.HIGH: "red",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "green"
        }[todo.priority]
        
        console.print(f"✅ Added todo ", end="")
        console.print(f"#{todo.id}", style="bold blue", end=": ")
        console.print(description, end=" ")
        console.print(f"({priority.lower()})", style=f"bold {priority_color}")
    except Exception as e:
        console.print(f"❌ Error adding todo: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command("l", help="List todos")
@click.option("--completed", is_flag=True, help="Show only completed todos")
@click.option("--pending", is_flag=True, help="Show only pending todos")
@click.option("-f", "--file", "file_path", help="Filter by file path")
def list_todos(completed: bool, pending: bool, file_path: Optional[str]):
    """List todos with optional filters."""
    try:
        status = None
        if completed:
            status = Status.COMPLETED
        elif pending:
            status = Status.PENDING
        
        todos = store.filter(status=status, file_path=file_path)
        
        if not todos:
            console.print("[yellow]No todos found.[/yellow]")
            return
        
        # Sort todos by priority (high to low) and then by ID
        priority_order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2
        }
        
        todos.sort(key=lambda t: (priority_order[t.priority], int(t.id)))
        
        # Create a table for displaying todos
        table = Table(show_header=True, header_style="bold")
        table.add_column("Status", style="bold", width=3)
        table.add_column("ID", style="dim", width=8)
        
        # Get terminal width to determine description column width
        term_width = shutil.get_terminal_size().columns
        desc_width = max(20, term_width - 50)  # Adjust based on other columns
        
        table.add_column("Description", width=desc_width)
        table.add_column("Priority", width=10)
        table.add_column("File", width=15)
        
        # Add rows to the table
        for todo in todos:
            # Format status
            status_str = "✓" if todo.status == Status.COMPLETED else " "
            
            # Format priority with color and emoji
            priority_format = {
                Priority.HIGH: ("red", "🔴"),
                Priority.MEDIUM: ("yellow", "🟡"),
                Priority.LOW: ("green", "🟢")
            }[todo.priority]
            priority_str = Text(f"{priority_format[1]} {todo.priority.value}", style=priority_format[0])
            
            # Truncate description if needed
            description = todo.description
            if len(description) > desc_width:
                description = description[:desc_width-3] + "..."
            
            # Format file path
            file_str = todo.file_path if todo.file_path else ""
            
            # Add the row
            table.add_row(
                status_str,
                todo.id,
                description,
                priority_str,
                file_str
            )
        
        console.print(f"Found {len(todos)} todo(s):")
        console.print(table)
        console.print("Use [bold]todo s <id>[/bold] to show full details of a specific todo.")
    except Exception as e:
        console.print(f"❌ Error listing todos: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command("c", help="Complete a todo")
@click.argument("todo_id")
def complete(todo_id: str):
    """Mark a todo as completed."""
    try:
        todo = store.mark_complete(todo_id)
        if todo:
            console.print(f"Marked as Completed: ", end="")
            console.print(f"{todo.description}", style="bold green")
        else:
            console.print(f"❌ Todo #{todo_id} not found.", style="bold red")
            sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error completing todo: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command("p", help="Mark a todo as pending")
@click.argument("todo_id")
def pending(todo_id: str):
    """Mark a completed todo as pending."""
    try:
        todo = store.mark_pending(todo_id)
        if todo:
            console.print(f"Marked as Pending: ", end="")
            console.print(f"{todo.description}", style="bold yellow")
        else:
            console.print(f"❌ Todo #{todo_id} not found.", style="bold red")
            sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error marking todo as pending: {str(e)}", style="bold red")
        sys.exit(1)




@cli.command("s", help="Show todo details")
@click.argument("todo_id")
def show(todo_id: str):
    """Show details of a specific todo."""
    try:
        todo = store.get(todo_id)
        if not todo:
            console.print(f"❌ Todo #{todo_id} not found.", style="bold red")
            sys.exit(1)
        
        # Create a panel with todo details
        status_color = "green" if todo.status == Status.COMPLETED else "yellow"
        priority_color = {
            Priority.HIGH: "red",
            Priority.MEDIUM: "yellow",
            Priority.LOW: "green"
        }[todo.priority]
        
        # Format dates for better readability
        created_date = datetime.fromisoformat(todo.created_at).strftime("%Y-%m-%d %H:%M")
        completed_date = None
        if todo.completed_at:
            completed_date = datetime.fromisoformat(todo.completed_at).strftime("%Y-%m-%d %H:%M")
        
        # Build the content
        content = [
            Text(f"ID: {todo.id}", style="dim"),
            Text(f"Description: {todo.description}", style="bold"),
            Text(f"Status: {todo.status.value}", style=status_color),
            Text(f"Priority: {todo.priority.value}", style=priority_color),
        ]
        
        if todo.file_path:
            content.append(Text(f"File: {todo.file_path}", style="blue underline"))
        
        content.append(Text(f"Created: {created_date}"))
        
        if completed_date:
            content.append(Text(f"Completed: {completed_date}", style="green"))
        
        # Display the panel
        panel = Panel(
            "\n".join(str(line) for line in content),
            title=f"Todo Details",
            border_style="blue"
        )
        console.print(panel)
    except Exception as e:
        console.print(f"❌ Error showing todo: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command("e", help="Erase todos")
@click.argument("todo_id", required=False)
@click.option("--all", is_flag=True, help="Erase all todos (both completed and pending)")
@click.option("--completed", is_flag=True, help="Erase all completed todos")
@click.option("--pending", is_flag=True, help="Erase all pending todos")
@click.option("--force", is_flag=True, help="Skip confirmation")
def erase(todo_id: Optional[str], all: bool, completed: bool, pending: bool, force: bool):
    """
    Erase todos. With a todo_id, it marks as completed and removes that specific todo.
    With --all, --completed, or --pending flags, it erases multiple todos.
    """
    try:
        # Case 1: Erase a specific todo by ID
        if todo_id:
            todo = store.get(todo_id)
            if not todo:
                console.print(f"❌ Todo #{todo_id} not found.", style="bold red")
                sys.exit(1)
            
            if not force:
                console.print(Panel(f"Are you sure you want to erase: {todo.description}?"))
                confirm = click.confirm("Proceed?")
                if not confirm:
                    console.print("Operation cancelled.", style="yellow")
                    return
            
            # First mark as completed
            if todo.status != Status.COMPLETED:
                todo.mark_complete()
                store.update(todo)
            
            # Then remove
            store.remove(todo.id)
            console.print(f"✨ Erased: ", end="")
            console.print(f"{todo.description}", style="bold green")
            return
        
        # Case 2: Erase multiple todos based on flags
        todos_to_erase = []
        
        if all:
            todos_to_erase = store.get_all()
            action_description = "all todos"
        elif completed:
            todos_to_erase = store.filter(status=Status.COMPLETED)
            action_description = "all completed todos"
        elif pending:
            todos_to_erase = store.filter(status=Status.PENDING)
            action_description = "all pending todos"
        else:
            console.print("Please specify either a todo ID or use --all, --completed, or --pending flags.", style="yellow")
            return
        
        if not todos_to_erase:
            console.print(f"No {action_description.split(' ', 1)[1]} to erase.", style="yellow")
            return
        
        if not force:
            console.print(Panel(f"Are you sure you want to erase {len(todos_to_erase)} {action_description.split(' ', 1)[1]}?"))
            confirm = click.confirm("Proceed?")
            if not confirm:
                console.print("Operation cancelled.", style="yellow")
                return
        
        # Mark pending todos as completed before removing
        for todo in todos_to_erase:
            if todo.status != Status.COMPLETED:
                todo.mark_complete()
                store.update(todo)
        
        # Remove all the todos
        count = 0
        for todo in todos_to_erase:
            store.remove(todo.id)
            count += 1
        
        console.print(f"✨ Erased {count} {action_description.split(' ', 1)[1]}.", style="bold green")
        
    except Exception as e:
        console.print(f"❌ Error erasing todos: {str(e)}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    cli()
