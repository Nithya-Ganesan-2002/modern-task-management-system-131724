from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Only task CRUD logic remains here. All authentication/user profile logic uses Supabase Auth ONLY!
# If using Supabase DB for tasks, replace in-memory TASKS with DB queries.

load_dotenv()

TASKS = {}

def init_workspace():
    """Initialize workspace (mock). In reality, check/create required tables in Supabase."""
    TASKS.clear()
    return True

# --- User registration/authentication logic REMOVED from here; handled by supabase in main.py ---

# PUBLIC_INTERFACE
def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Disabled: User lookup logic is now handled via Supabase Auth JWT.
    This function is not used, present for backward compatibility."""
    return None

# PUBLIC_INTERFACE
def create_task(user_id: str, title: str, description: Optional[str], status: str) -> Dict[str, Any]:
    """Create a new task for a user."""
    task_id = str(uuid.uuid4())
    now = datetime.utcnow()
    task = {
        "id": task_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }
    TASKS[task_id] = task
    return task

# PUBLIC_INTERFACE
def list_tasks(user_id: str) -> List[Dict[str, Any]]:
    """List all tasks belonging to a user."""
    return [t for t in TASKS.values() if t["user_id"] == user_id]

# PUBLIC_INTERFACE
def get_task(task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a task by ID for the given user."""
    task = TASKS.get(task_id)
    if task and task["user_id"] == user_id:
        return task
    return None

# PUBLIC_INTERFACE
def update_task(task_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing task."""
    task = TASKS.get(task_id)
    if not task or task["user_id"] != user_id:
        return None
    for key in ("title", "description", "status"):
        if key in updates and updates[key] is not None:
            task[key] = updates[key]
    task["updated_at"] = datetime.utcnow()
    TASKS[task_id] = task
    return task

# PUBLIC_INTERFACE
def delete_task(task_id: str, user_id: str) -> bool:
    """Delete a user's task."""
    task = TASKS.get(task_id)
    if not task or task["user_id"] != user_id:
        return False
    del TASKS[task_id]
    return True
