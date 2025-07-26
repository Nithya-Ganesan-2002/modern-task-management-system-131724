# Supabase Integration for Task Manager Backend

This backend is designed to use Supabase as the persistent database for user accounts and tasks.

## Integration Points

- All user and task operations (register, login, task CRUD) will interact with Supabase via the official supabase-py client.
- For local development, to enable Supabase, install `supabase` and set the required environment variables in your `.env` file (see below).
- Replace the code in `src/api/repository.py` with actual calls to the Supabase client.

## Required Environment Variables

Add these entries to your `.env` file in the `task_manager_backend` container root:

```
SUPABASE_URL=https://<your-supabase-project>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

**Note**: Do NOT check your real keys into version control.

## How to Use in Code

1. In `src/api/repository.py`, import and configure the client:

```python
from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Prefer service role for backend ops
supabase = create_client(url, key)
```

2. Replace USER and TASK CRUD logic to use Supabase tables:
- Table `users`: columns (`id`, `email`, `password_hash`, ...)
- Table `tasks`: columns (`id`, `user_id`, `title`, `description`, `status`, `created_at`, `updated_at`)

3. Secure password storage! Use hashing (e.g., `bcrypt`).

## Email Confirmations

For user registration using Supabase auth, handle email registration with:

```python
resp = supabase.auth.sign_up(
    {"email": email, "password": password},
    email_redirect_to=f"{os.getenv('SITE_URL', 'http://localhost:3000')}/auth/callback"
)
```

**Site URL:** Set the frontend base URL in `.env` as `SITE_URL`.

## Replacing the In-Memory Store

Currently, we use an in-memory Python dict for prototyping. Replace all the CRUD operations in `repository.py` with the equivalents from Supabase.

## Testing

Before deploying, thoroughly test all auth and task routes with Supabase as backend.

---
Task completed: Initial FastAPI backend structure with models, modular CRUD/auth logic, routes, and Supabase integration guidance written.
