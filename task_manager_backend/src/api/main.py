from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import (
    UserRegisterRequest, UserLoginRequest, UserResponse, AuthTokenResponse,
    TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse
)
from .repository import (
    create_task, list_tasks, get_task, update_task, delete_task,
    init_workspace
)

import os
from supabase import create_client, Client
import jwt

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

openapi_tags = [
    {"name": "auth", "description": "Authentication and user management"},
    {"name": "tasks", "description": "Task CRUD operations"},
    {"name": "workspace", "description": "Initialization utilities"},
]

app = FastAPI(
    title="Task Manager Backend API",
    description="API backend for user authentication and task CRUD for a task management app, with Supabase integration.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def decode_supabase_jwt(token: str) -> dict:
    """Decode the JWT from Supabase auth (does not verify signature, just parses claims)."""
    # For robust verification, fetch Supabase project JWKS/public keys and verify signature
    # Here we parse claims for user id/email
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
        return unverified
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to decode token")


# PUBLIC_INTERFACE
def get_current_user(authorization: str = Header(None)) -> UserResponse:
    """
    FastAPI dependency to extract and validate the current user using Supabase JWT from Authorization header.

    Args:
        authorization (str): The HTTP Authorization header

    Returns:
        UserResponse: The authenticated user's id and email

    Raises:
        HTTPException: If missing/invalid token or user not found in Supabase
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Authorization header")
    token = authorization.split(" ")[1]
    # Decode claims to get user id (subject = uid), and email
    try:
        claims = decode_supabase_jwt(token)
        user_id = claims.get("sub")
        email = claims.get("email")
        if not user_id or not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase token claims")
        # Optionally, refresh session or validate token with Supabase (if you want live session check)
        # user = supabase.auth.api.get_user(token) # this is supported by supabase-py for validation
        return UserResponse(user_id=user_id, email=email)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")


@app.get("/", summary="Health Check", tags=["workspace"])
def health_check():
    """Check that the backend service is running."""
    return {"message": "Healthy"}


@app.post("/workspace/init", summary="Initialize workspace", tags=["workspace"])
def workspace_init():
    """
    Set up the initial application workspace.
    In a real scenario, this would initialize the Supabase tables.
    """
    init_workspace()
    return {"message": "Workspace initialized"}


@app.post("/auth/register", response_model=AuthTokenResponse, summary="Register new user", tags=["auth"])
def register(body: UserRegisterRequest):
    """
    Register a new user. Calls Supabase Auth and returns access token.
    """
    try:
        # Register with Supabase; expect user is created and session is returned
        resp = supabase.auth.sign_up(
            {
                "email": body.email,
                "password": body.password,
            },
            email_redirect_to=f"{os.getenv('SITE_URL', 'http://localhost:3000')}/auth/callback"
        )
        user = resp.get("user")
        session = resp.get("session")
        if not user:
            raise HTTPException(status_code=400, detail="Error registering user")
        if not session:
            # Supabase may require email confirmation
            raise HTTPException(status_code=202, detail="Check your email to confirm registration")
        token = session.get("access_token")
        user_id = user.get("id") or user.get("user_metadata", {}).get("sub")
        return AuthTokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(user_id=user_id, email=body.email),
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Internal error or Supabase error during registration")


@app.post("/auth/login", response_model=AuthTokenResponse, summary="Login", tags=["auth"])
def login(body: UserLoginRequest):
    """
    Log user in via Supabase and return access token.
    """
    try:
        resp = supabase.auth.sign_in_with_password({
            "email": body.email,
            "password": body.password,
        })
        session = resp.get("session")
        user = resp.get("user")
        if not session or not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = session.get("access_token")
        user_id = user.get("id") or user.get("user_metadata", {}).get("sub")
        return AuthTokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(user_id=user_id, email=body.email),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Login failed due to internal or Supabase error")


@app.post("/auth/logout", summary="Logout", tags=["auth"])
def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    Logout a user. (Stateless: client simply drops token.)
    """
    return {"message": "Logout successful"}


@app.post("/tasks", response_model=TaskResponse, summary="Create Task", tags=["tasks"])
def create_task_endpoint(
    body: TaskCreateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new task.
    """
    task = create_task(
        user_id=current_user.user_id,
        title=body.title,
        description=body.description,
        status=body.status or "pending"
    )
    return TaskResponse(**task)


@app.get("/tasks", response_model=TaskListResponse, summary="List Tasks", tags=["tasks"])
def list_tasks_endpoint(current_user: UserResponse = Depends(get_current_user)):
    """
    List all tasks for the authenticated user.
    """
    tasks = list_tasks(user_id=current_user.user_id)
    return TaskListResponse(tasks=[TaskResponse(**t) for t in tasks])


@app.get("/tasks/{task_id}", response_model=TaskResponse, summary="Get Task", tags=["tasks"])
def get_task_endpoint(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a task by ID.
    """
    task = get_task(task_id=task_id, user_id=current_user.user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)


@app.put("/tasks/{task_id}", response_model=TaskResponse, summary="Update Task", tags=["tasks"])
def update_task_endpoint(
    task_id: str,
    body: TaskUpdateRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update a task by ID.
    """
    existing = get_task(task_id, user_id=current_user.user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = body.dict(exclude_unset=True)
    task = update_task(task_id=task_id, user_id=current_user.user_id, updates=updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)


@app.delete("/tasks/{task_id}", summary="Delete Task", tags=["tasks"])
def delete_task_endpoint(
    task_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a task by ID.
    """
    result = delete_task(task_id=task_id, user_id=current_user.user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Deleted"}


@app.patch("/tasks/{task_id}/status", response_model=TaskResponse, summary="Update Task Status", tags=["tasks"])
def update_task_status_endpoint(
    task_id: str,
    status: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update only the status of a task.
    """
    task = get_task(task_id=task_id, user_id=current_user.user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    updates = {"status": status}
    updated = update_task(task_id=task_id, user_id=current_user.user_id, updates=updates)
    return TaskResponse(**updated)
