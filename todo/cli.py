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


def normalize_priority(priority: str) -> str:
    """Convert shorthand priority (h, m, l) to full form (high, medium, low)."""
    priority = priority.lower()
    if priority == 'h':
        return 'high'
    elif priority == 'm':
        return 'medium'
    elif priority == 'l':
        return 'low'
    return priority


# Initialize the todo store and console
store = TodoStore()
console = Console()


@click.group()
@click.version_option(version="1.1.0")
def cli():
    """Todo CLI - A simple command-line todo application."""
    pass


@cli.command("a", help="Add a new todo")
@click.argument("description")
@click.option("-f", "--file", "file_path", help="Associate with a file path")
@click.option("-p", "--priority", type=click.Choice(["high", "medium", "low", "h", "m", "l"], case_sensitive=False), default="medium", help="Set priority (h/m/l or high/medium/low, default: medium)")
def add(description: str, file_path: Optional[str], priority: str):
    """Add a new todo with the given description."""
    try:
        # Normalize priority
        priority = normalize_priority(priority)
        
        todo = Todo(
            description=description,
            file_path=file_path,
            priority=Priority(priority)
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
        console.print(f"({priority})", style=f"bold {priority_color}")
    except Exception as e:
        console.print(f"❌ Error adding todo: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command("l", help="List todos")
@click.option("-c", "--completed", is_flag=True, help="Show only completed todos")
@click.option("-p", "--pending", is_flag=True, help="Show only pending todos")
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


@cli.command("c", help="Complete todos")
@click.argument("todo_ids", nargs=-1, required=False)
@click.option("-a", "--all", is_flag=True, help="Mark all pending todos as completed")
def complete(todo_ids: List[str], all: bool):
    """Mark todos as completed. Specify todo IDs or use --all flag."""
    try:
        # Case 1: Mark all pending todos as completed
        if all:
            pending_todos = store.filter(status=Status.PENDING)
            
            if not pending_todos:
                console.print("No pending todos to complete.", style="yellow")
                return
            
            # Mark all pending todos as completed
            count = 0
            for todo in pending_todos:
                store.mark_complete(todo.id)
                count += 1
            
            console.print(f"✅ Marked {count} todos as completed.", style="bold green")
            return
        
        # Case 2: Mark specific todos as completed
        if not todo_ids:
            console.print("Please specify either todo ID(s) or use the --all flag.", style="yellow")
            return
            
        todos_completed = []
        not_found_ids = []
        
        # Process each todo ID
        for todo_id in todo_ids:
            todo = store.mark_complete(todo_id)
            if todo:
                todos_completed.append(todo)
            else:
                not_found_ids.append(todo_id)
        
        # Report any IDs that weren't found
        if not_found_ids:
            console.print(f"❌ Todo(s) not found: {', '.join(not_found_ids)}", style="bold red")
            if not todos_completed:
                sys.exit(1)
        
        # Report successful completions
        if len(todos_completed) == 1:
            console.print(f"✅ Marked as Completed: ", end="")
            console.print(f"{todos_completed[0].description}", style="bold green")
        else:
            console.print(f"✅ Marked {len(todos_completed)} todos as completed:", style="bold green")
            for todo in todos_completed:
                console.print(f"  • {todo.description}")
        
    except Exception as e:
        console.print(f"❌ Error completing todos: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command("p", help="Mark todos as pending")
@click.argument("todo_ids", nargs=-1, required=False)
@click.option("-a", "--all", is_flag=True, help="Mark all completed todos as pending")
def pending(todo_ids: List[str], all: bool):
    """Mark todos as pending. Specify todo IDs or use --all flag."""
    try:
        # Case 1: Mark all completed todos as pending
        if all:
            completed_todos = store.filter(status=Status.COMPLETED)
            
            if not completed_todos:
                console.print("No completed todos to mark as pending.", style="yellow")
                return
            
            # Mark all completed todos as pending
            count = 0
            for todo in completed_todos:
                store.mark_pending(todo.id)
                count += 1
            
            console.print(f"🔄 Marked {count} todos as pending.", style="bold yellow")
            return
        
        # Case 2: Mark specific todos as pending
        if not todo_ids:
            console.print("Please specify either todo ID(s) or use the --all flag.", style="yellow")
            return
            
        todos_pending = []
        not_found_ids = []
        
        # Process each todo ID
        for todo_id in todo_ids:
            todo = store.mark_pending(todo_id)
            if todo:
                todos_pending.append(todo)
            else:
                not_found_ids.append(todo_id)
        
        # Report any IDs that weren't found
        if not_found_ids:
            console.print(f"❌ Todo(s) not found: {', '.join(not_found_ids)}", style="bold red")
            if not todos_pending:
                sys.exit(1)
        
        # Report successful changes to pending
        if len(todos_pending) == 1:
            console.print(f"🔄 Marked as Pending: ", end="")
            console.print(f"{todos_pending[0].description}", style="bold yellow")
        else:
            console.print(f"🔄 Marked {len(todos_pending)} todos as pending:", style="bold yellow")
            for todo in todos_pending:
                console.print(f"  • {todo.description}")
        
    except Exception as e:
        console.print(f"❌ Error marking todos as pending: {str(e)}", style="bold red")
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
@click.argument("todo_ids", nargs=-1, required=False)
@click.option("-a", "--all", is_flag=True, help="Erase all todos (both completed and pending)")
@click.option("-c", "--completed", is_flag=True, help="Erase all completed todos")
@click.option("-p", "--pending", is_flag=True, help="Erase all pending todos")
@click.option("-f", "--force", is_flag=True, help="Skip confirmation")
def erase(todo_ids: List[str], all: bool, completed: bool, pending: bool, force: bool):
    """
    Erase todos. With todo_ids, it marks as completed and removes those specific todos.
    With --all, --completed, or --pending flags, it erases multiple todos.
    """
    try:
        # Case 1: Erase specific todos by ID(s)
        if todo_ids:
            todos_to_erase = []
            not_found_ids = []
            
            # Collect todos to erase
            for todo_id in todo_ids:
                todo = store.get(todo_id)
                if todo:
                    todos_to_erase.append(todo)
                else:
                    not_found_ids.append(todo_id)
            
            # Report any IDs that weren't found
            if not_found_ids:
                console.print(f"❌ Todo(s) not found: {', '.join(not_found_ids)}", style="bold red")
                if not todos_to_erase:
                    sys.exit(1)
            
            # Confirm before erasing
            if not force and todos_to_erase:
                descriptions = [f"#{todo.id}: {todo.description}" for todo in todos_to_erase]
                console.print(Panel("\n".join(descriptions), title=f"Erase {len(todos_to_erase)} todo(s)?"))
                confirm = click.confirm("Proceed?")
                if not confirm:
                    console.print("Operation cancelled.", style="yellow")
                    return
            
            # Mark as completed and remove
            count = 0
            for todo in todos_to_erase:
                # First mark as completed
                if todo.status != Status.COMPLETED:
                    todo.mark_complete()
                    store.update(todo)
                
                # Then remove
                store.remove(todo.id)
                count += 1
            
            if count == 1:
                console.print(f"✨ Erased: ", end="")
                console.print(f"{todos_to_erase[0].description}", style="bold green")
            else:
                console.print(f"✨ Erased {count} todos.", style="bold green")
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
            console.print("Please specify either todo ID(s) or use --all, --completed, or --pending flags.", style="yellow")
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

@cli.command("m", help="Modify todos priority")
@click.argument("todo_ids", nargs=-1, required=False)
@click.option("-p", "--priority", type=click.Choice(["high", "medium", "low", "h", "m", "l"], case_sensitive=False), default="medium", help="Set priority (h/m/l or high/medium/low, default: medium)")
@click.option("-a", "--all", is_flag=True, help="Modify all todos (both completed and pending)")
def modify(todo_ids: List[str], priority: str, all: bool):
    """
    Modify todos priority. Specify todo IDs to change their priority,
    or use --all flag to modify all todos.
    """
    try:
        # Normalize priority
        priority = normalize_priority(priority)
        
        # Case 1: Modify all todos
        if all:
            todos_to_modify = store.get_all()
            
            if not todos_to_modify:
                console.print("No todos to modify.", style="yellow")
                return
            
            # Update priority for all todos
            count = 0
            for todo in todos_to_modify:
                todo.priority = Priority(priority)
                store.update(todo)
                count += 1
            
            console.print(f"✨ Updated priority to {priority} for {count} todos.", style="bold blue")
            return
        
        # Case 2: Modify specific todos by ID(s)
        if not todo_ids:
            console.print("Please specify either todo ID(s) or use the --all flag.", style="yellow")
            return
            
        todos_to_modify = []
        not_found_ids = []
        
        # Collect todos to modify
        for todo_id in todo_ids:
            todo = store.get(todo_id)
            if todo:
                todos_to_modify.append(todo)
            else:
                not_found_ids.append(todo_id)
        
        # Report any IDs that weren't found
        if not_found_ids:
            console.print(f"❌ Todo(s) not found: {', '.join(not_found_ids)}", style="bold red")
            if not todos_to_modify:
                sys.exit(1)
        
        # Update priority
        count = 0
        for todo in todos_to_modify:
            # Update priority
            todo.priority = Priority(priority)
            store.update(todo)
            count += 1
        
        if count == 1:
            console.print(f"✨ Updated priority to {priority}: ", end="")
            console.print(f"{todos_to_modify[0].description}", style="bold blue")
        else:
            console.print(f"✨ Updated priority to {priority} for {count} todos.", style="bold blue")
        
    except Exception as e:
        console.print(f"❌ Error modifying todos: {str(e)}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    cli()
