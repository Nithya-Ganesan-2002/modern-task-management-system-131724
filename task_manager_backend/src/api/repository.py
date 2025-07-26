from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from dotenv import load_dotenv

# For demonstration purposes, this logic should later be replaced with Supabase/Postgres integration.
# Here, a simple in-memory store is used. Replace with actual Supabase client logic per supabase.md.

load_dotenv()

# --- Mocked in-memory stores ---
USERS = {}
TASKS = {}

def init_workspace():
    """Initialize workspace (mock). In reality, check/create required tables in Supabase."""
    USERS.clear()
    TASKS.clear()
    return True

# PUBLIC_INTERFACE
def register_user(email: str, password: str) -> Dict[str, Any]:
    """Registers a new user."""
    if email in USERS:
        raise ValueError("User already exists")
    user_id = str(uuid.uuid4())
    USERS[email] = {"user_id": user_id, "email": email, "password": password}
    return USERS[email]

# PUBLIC_INTERFACE
def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates a user."""
    user = USERS.get(email)
    if not user or user["password"] != password:
        return None
    return user

# PUBLIC_INTERFACE
def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user by ID."""
    for user in USERS.values():
        if user["user_id"] == user_id:
            return user
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
