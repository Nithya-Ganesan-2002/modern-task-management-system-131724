# Supabase Integration for Task Manager Backend

This backend uses Supabase as the persistent database for user accounts and tasks.

---

## Live Database Schema (Provisioned)

### Table: `users`
| Column         | Type                     | Notes                                 |
| -------------- | ------------------------ | ------------------------------------- |
| id             | uuid (PK)                | Primary key - UUID v4                 |
| email          | text                     | Unique, indexed                       |
| password_hash  | text                     | Store hashed password (not raw)       |
| created_at     | timestamp with time zone | Defaults to now()                     |
| updated_at     | timestamp with time zone | Defaults to now()                     |

Indexes & Constraints:
- `PRIMARY KEY (id)`
- `UNIQUE INDEX (email)`

### Table: `tasks`
| Column      | Type                     | Notes                                 |
| ----------- | ------------------------ | ------------------------------------- |
| id          | uuid (PK)                | Primary key - UUID v4                 |
| user_id     | uuid (FK → users.id)     | Owner                                 |
| title       | text                     | Task title                            |
| description | text (nullable)          | Task details                          |
| status      | text                     | Task status (pending/completed/etc.)  |
| created_at  | timestamp with time zone | Defaults to now()                     |
| updated_at  | timestamp with time zone | Defaults to now()                     |

Indexes & Constraints:
- `PRIMARY KEY (id)`
- `INDEX (user_id)`

---

## Row Level Security (RLS) and Policies

**Table `users`:**
- RLS Enabled.
- Select: Users can view only their row (`auth.uid() = id`).
- Insert/Update: Allowed for service/system roles (secure signup).
- Policies provisioned to prevent users reading other accounts.

**Table `tasks`:**
- RLS Enabled.
- Select, Insert, Update, Delete: Allowed only where `auth.uid() = user_id`.
  - Ensures only owner can access or modify their tasks.

---

## Integration Points (as before)

All user and task operations (register, login, task CRUD) will interact with Supabase via the official supabase-py client (for backend) and `@supabase/supabase-js` (frontend).

- For local dev, install `supabase` Python and `@supabase/supabase-js` NPM packages.
- Ensure your `.env` files have the following:

### Backend: add to `task_manager_backend/.env`:
```
SUPABASE_URL=https://<your-supabase-project>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```
*Never check real keys into version control!*

### Frontend: add to `task_manager_frontend/.env`:
```
REACT_APP_SUPABASE_URL=https://<your-supabase-project>.supabase.co
REACT_APP_SUPABASE_KEY=<your-anon-key>
```

> **Note:** The keys above must be provided by project admin via Supabase Dashboard.

---

## Python Example (Backend)

```python
from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# Example: Sign up a user
resp = supabase.auth.sign_up(
    {"email": email, "password": password},
    email_redirect_to=f"{os.getenv('SITE_URL', 'http://localhost:3000')}/auth/callback"
)
```

---

## Frontend Example (React/JS)

- Install package: `npm install @supabase/supabase-js`
- Use environment variables for URL and KEY.

```js
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseKey = process.env.REACT_APP_SUPABASE_KEY;
export const supabase = createClient(supabaseUrl, supabaseKey);
```

---

## Email Confirmations

- Email redirects MUST use a callback like `/auth/callback` as shown above.
- Update the Supabase Dashboard's Auth → URL Configuration to include:
  - http://localhost:3000/**
  - Your production URL

**Site URL:** Set the frontend base URL as `SITE_URL` in backend `.env` for email callbacks.

---

## Secure Password Storage

Passwords must be hashed (e.g., `bcrypt`). Never store plain text!

---

## Replacing the In-Memory Store

All CRUD logic in `repository.py` should call Supabase instead of local dicts.

---

## Testing Checklist

- Test user registration, login, and task CRUD from both frontend and backend
- Validate RLS by trying to access another user’s tasks (should fail)

---

Task completed: 
- Provisioned all tables/policies in Supabase live database
- Documented table schema and required policies
- Updated `.env` recommendations and integration code
- Ready to connect the FastAPI backend and React frontend to Supabase
