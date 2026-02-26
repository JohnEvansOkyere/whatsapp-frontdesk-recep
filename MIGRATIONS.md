# Database migrations guide

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations. The database is **PostgreSQL only** (Neon). You must set `NEON_DATABASE_URL` in `backend/.env` before running migrations or the app.

---

## Prerequisites

- Python environment with backend dependencies installed: from the **backend** directory run `uv sync` or `pip install -r requirements.txt`.
- A [Neon](https://neon.tech) account and a PostgreSQL database.

---

## 1. Create a database in Neon

1. Go to [neon.tech](https://neon.tech) and sign in.
2. Create a new **project** (or use an existing one).
3. Create a **branch** and **database** if needed (Neon often creates a default database).
4. Open the project **Dashboard** and copy the **connection string**.
   - Use the **pooled** connection string if available (e.g. for serverless).
   - It looks like:  
     `postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require`

---

## 2. Configure the database URL

Create a `.env` in the **backend** directory (copy from `backend/.env.example`) and set:

```env
NEON_DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Replace the placeholder with your actual Neon connection string.  
**Do not commit `.env`** — it is listed in `.gitignore`.  
Migrations and the app both require `NEON_DATABASE_URL` to be set; there is no SQLite fallback.

---

## 3. Apply migrations (create/update schema)

From the **backend** directory:

```bash
cd backend
alembic upgrade head
```

This applies all pending migrations and brings the database schema up to date. For a new Neon database, this creates all tables (businesses, customers, services, staff, bookings, faqs, conversation_history, support_sessions).

**Check current revision:** (from backend directory)

```bash
cd backend && alembic current
```

**See migration history:**

```bash
cd backend && alembic history
```

---

## 4. Create a new migration (after model changes)

After changing SQLAlchemy models under `backend/app/models/db/`:

1. Ensure the app can load (so Alembic can see `Base.metadata`). Run from the **backend** directory.
2. Generate a new revision:

   ```bash
   cd backend
   alembic revision --autogenerate -m "Short description of the change"
   ```

3. Open the new file under `backend/migrations/versions/` and fix any PostgreSQL-specific types if you generated against SQLite (e.g. use `sa.Text()` / `sa.String()` in JSON/ARRAY, and `sa.text('now()')` for timestamp defaults).
4. Apply it:

   ```bash
   cd backend && alembic upgrade head
   ```

---

## 5. Downgrade (roll back)

Roll back one revision (from backend directory):

```bash
cd backend && alembic downgrade -1
```

Roll back to a specific revision:

```bash
cd backend && alembic downgrade <revision_id>
```

Roll back all migrations:

```bash
cd backend && alembic downgrade base
```

---

## 6. Common commands reference

| Command | Description |
|--------|-------------|
| `cd backend && alembic upgrade head` | Apply all migrations (bring DB to latest). |
| `cd backend && alembic downgrade -1` | Undo the last migration. |
| `cd backend && alembic current` | Show current revision. |
| `cd backend && alembic history` | List all revisions. |
| `cd backend && alembic revision --autogenerate -m "msg"` | Create a new migration from model changes. |

---

## Troubleshooting

- **"relation already exists" / "table already exists"**  
  The migration was likely applied already. Check with `alembic current` and `alembic history`. If you need a clean slate on Neon, create a new branch/database and run `alembic upgrade head` again.

- **SSL or connection errors to Neon**  
  Ensure the URL includes `?sslmode=require` and that Neon allows connections from your IP (or use "Allow from anywhere" in Neon dashboard for development).

- **Autogenerate**  
  With `NEON_DATABASE_URL` set, new migrations are generated for PostgreSQL. Use `postgresql.JSON(astext_type=sa.Text())`, `postgresql.ARRAY(sa.String())`, and `server_default=sa.text('now()')` where appropriate.
