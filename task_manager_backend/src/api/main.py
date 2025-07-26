from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import (
    UserRegisterRequest, UserLoginRequest, UserResponse, AuthTokenResponse,
    TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse
)
from .repository import (
    register_user, authenticate_user, get_user_by_id,
    create_task, list_tasks, get_task, update_task, delete_task,
    init_workspace
)

load_dotenv()

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

def fake_generate_token(user_id: str) -> str:
    """(Temporary) Generate a fake session token. Replace with JWT/Supabase session."""
    return f"fake-token-{user_id}"

def get_current_user(authorization: str = Header(None)) -> UserResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Authorization header")
    token = authorization.split(" ")[1]
    # For now, extract user_id from the fake token
    if not token.startswith("fake-token-"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = token.replace("fake-token-", "")
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return UserResponse(user_id=user_id, email=user["email"])


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
    Register a new user. Stores user in backend and returns access token.
    """
    try:
        user = register_user(body.email, body.password)
        token = fake_generate_token(user["user_id"])
        return AuthTokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(user_id=user["user_id"], email=user["email"]),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@app.post("/auth/login", response_model=AuthTokenResponse, summary="Login", tags=["auth"])
def login(body: UserLoginRequest):
    """
    Log user in. Returns access token.
    """
    user = authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = fake_generate_token(user["user_id"])
    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(user_id=user["user_id"], email=user["email"]),
    )


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
