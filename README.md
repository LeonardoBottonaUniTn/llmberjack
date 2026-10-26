# Conversation Creator

A Vue.js application for creating and visualizing hierarchical discussion trees with integrated chat functionality. This tool helps facilitate structured debates and discussions by organizing arguments in a tree-like structure with pro/con relationships.

## ✨ Features

- **Discussion Graph Visualization**: Interactive tree and single-branch views of argument structures
- **Real-time Chat Interface**: Telegram-style chat with multiple user personas
- **Argument Tree Management**: Support for thesis, pro, and con argument types
- **Dynamic User Personas**: AI-generated speakers with distinct stances and communication styles
- **Responsive Design**: Optimized for both desktop and mobile viewing
- **Multiple View Modes**: Switch between tree view and focused single-branch view
- **Conversation Annotation / Labeling**: Annotate conversations with customizable schemas, including message-level and conversation-level fields, progress tracking, and a built-in schema editor
- **Supabase-backed Persistence**: User authentication, file storage, and metadata stored in a managed Postgres database

## 🏗️ Architecture

### Frontend (Vue.js)

- **Framework**: Vue 3 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Custom components for chat and graph visualization
- **State Management**: Vue Composition API with composables

### Backend (FastAPI + Supabase)

- **API**: FastAPI (Python) serving file, folder, user, and LLM routes
- **Database**: **Supabase Postgres** — the `files` table stores file metadata and the `user_settings` table stores per-user API keys, model/provider preferences, and the saved `annotation_schema`
- **Auth**: Supabase authentication; records are scoped per user (`created_by` / `user_id`)
- **Storage**: Supabase Storage for uploaded file contents; empty folders use hidden `.folder` marker objects

File metadata and settings use the backend-only service client after authentication, with access scoped to the verified user's ID. Conversation files and personas are served through authenticated API routes; the backend directory and local file directory are not exposed as public static assets.

### Annotation / Labeling

The annotation page lets you label a selected conversation:

- **Customizable schema**: Define message-level and conversation-level fields via the schema editor; schemas are saved per user in `user_settings.annotation_schema`
- **Progress tracking**: Per-conversation annotation progress and completion status
- **Persistence**: Annotations are stored alongside the conversation data

## 📁 Project Structure

```
conv_creator/
├── frontend/
│   ├── package.json          # Frontend dependencies and npm scripts
│   └── src/
│       ├── components/
│       │   ├── annotation/   # Annotation fields and schema editor
│       │   ├── chat/         # Telegram-style chat interface
│       │   ├── graph/        # Graph visualization, controls, nodes, and views
│       │   └── shared/       # Reusable components
│       ├── composables/      # Auth, files, graph, and annotation state
│       ├── router/           # Routes and authentication guards
│       ├── types/            # TypeScript type definitions
│       └── views/            # Home, Login, Files, Discussion, Annotation, Settings
├── backend/
│   ├── main.py               # FastAPI app and active API endpoints
│   ├── routes/               # Route modules and LLM prompts
│   ├── database.py           # Supabase file metadata access
│   ├── supabase_client.py    # Supabase clients and auth helpers
│   ├── file_storage.py       # Supabase Storage helpers
│   ├── requirements.txt      # Python dependencies
│   └── scripts/setup_db.py   # Idempotent table setup
├── supabase/
│   └── migrations/           # Database schema, grants, and storage policies
├── start-dev.sh              # Starts backend and frontend together
└── package.json              # Root dependencies; no application npm scripts
```

## 🛠️ Technology Stack

- **Vue 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Vue Router** - Client-side routing
- **D3** - Graph visualization
- **PrimeVue / PrimeIcons** - UI components and icons
- **FastAPI / Uvicorn** - Python API and development server
- **Supabase** - Authentication, Postgres, and file storage
- **Playwright** - End-to-end testing
- **ESLint + Prettier** - Code formatting and linting

## 🚀 Getting Started

### Prerequisites

- Node.js matching `^20.19.0 || >=22.12.0`, as declared in `frontend/package.json`. The version-manager files in `frontend/` pin Node.js 20.19.0.
- Python 3.10 or newer with `venv` and `pip` (the backend uses Python 3.10 union type syntax).
- A Supabase project with Auth, Postgres, and Storage available.
- A Groq or OpenAI API key to use AI generation and rewriting.

### Installation

1. **Clone the repository**

```sh
git clone --branch emnlp-final https://github.com/LeonardoBottonaUniTn/llmberjack.git
cd llmberjack/conv_creator
```

All commands below start from `llmberjack/conv_creator` unless stated otherwise.

2. **Install frontend dependencies**

```sh
cd frontend
# If using nvm:
nvm install
nvm use
npm ci
cd ..
```

The npm application scripts live in `frontend/`. Installing dependencies at the root does not install the frontend application.

3. **Install backend dependencies**

```sh
python3 -m venv backend/backend_env
source backend/backend_env/bin/activate
python -m pip install -r backend/requirements.txt
```

These activation commands and `start-dev.sh` target macOS/Linux shells. On Windows, activate the virtual environment with `backend\backend_env\Scripts\Activate.ps1` in PowerShell and start the servers separately as shown below.

4. **Create a Supabase project and collect its credentials**

Open the [Supabase dashboard](https://supabase.com/dashboard), sign in, and select **New project**. Choose an organization, enter a project name (for example, `llmberjack-emnlp`), save the database password, and choose a nearby region. Wait until the project finishes provisioning.

In the new project's dashboard:

- Open **Connect** to find the project URL (`https://<project-ref>.supabase.co`).
- Open **Settings → API Keys**. For this branch's existing authentication integration, use the legacy **anon** and **service_role** keys for `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_ROLE_KEY`. The service role key belongs only in the backend environment.
- Open **Connect → Session pooler** and copy its Postgres connection URI. Replace the password placeholder with the database password you saved when creating the project. Use this URI for `DATABASE_IPv4_URL`; the session pooler supports IPv4 connections. URL-encode special characters in the password when placing it in a URI.

The Postgres URI and project URL are different values: `SUPABASE_URL` starts with `https://`, while `DATABASE_IPv4_URL` starts with `postgresql://`. Both must refer to the same project. See Supabase's [API key guide](https://supabase.com/docs/guides/getting-started/api-keys) and [database connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres).

5. **Configure the environment**

Create `.env` in `conv_creator/` with values from the same Supabase project:

```dotenv
SUPABASE_URL='https://<project-ref>.supabase.co'
SUPABASE_ANON_KEY='<anon-key>'
SUPABASE_SERVICE_ROLE_KEY='<service-role-key>'
DATABASE_IPv4_URL='postgresql://<user>:<password>@<host>:<port>/<database>'
SUPABASE_STORAGE_BUCKET='user-files'
```

| Variable | Purpose |
| --- | --- |
| `SUPABASE_URL` | Supabase HTTP API and Auth URL. |
| `SUPABASE_ANON_KEY` | Public API key used by the backend for Auth and table access. `SUPABASE_PUBLISHABLE_KEY` is also supported. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend-only key required for Storage, file metadata, and user settings operations. Keep it out of frontend environment variables. |
| `DATABASE_IPv4_URL` | Postgres connection URI used by the schema setup script; use a connection endpoint reachable from your machine. |
| `SUPABASE_STORAGE_BUCKET` | Optional bucket name; defaults to `user-files`. The bundled storage migration uses this default. |

`SUPABASE_STORAGE_BUCKET` is the name of a storage bucket, not an API key or generated credential. Use `user-files` for this project. You can find it under **Storage** in the dashboard after running the storage migration in the next step. If Storage is empty, complete that step first.

The development launcher sources this file as shell syntax, so use assignments without spaces around `=` and quote values as above. Keep `.env` local and do not commit credentials; `.env` files are excluded by `.gitignore`.

6. **Set up Supabase tables and storage**

With the backend virtual environment active, run:

```sh
python backend/scripts/setup_db.py
```

This creates or updates `files` and `user_settings`, including the provider and annotation schema columns. It does not create storage buckets, storage policies, or explicit table grants.

For a new project using this table setup script, open these additional SQL files locally in order:

- [20260706152200_add_user_settings.sql](supabase/migrations/20260706152200_add_user_settings.sql) — includes the grants for `user_settings`.
- [20260706170000_user_files_bucket.sql](supabase/migrations/20260706170000_user_files_bucket.sql) — creates the private `user-files` bucket and policies for each user's storage prefix.

For each file, copy its **entire SQL contents**, open **SQL Editor → New query** in Supabase, paste the contents, and click **Run**. Run the first file before the second. The SQL Editor executes SQL statements; pasting only a file path such as `supabase/migrations/...sql` produces a syntax error near `supabase`.

Afterward, check **Table Editor** for `files` and `user_settings`, and **Storage** for the private `user-files` bucket.

The other incremental migrations cover per-user file paths, provider settings, and annotation schemas; those table changes are also included in `setup_db.py`. The full migration history, including the original schema snapshot, is in `supabase/migrations/`. For an existing project managed through migrations, apply its pending migrations through that workflow instead of replaying the original snapshot manually.

7. **Create a confirmed demo account**

Enable email/password sign-in under **Authentication → Sign In / Providers**. For a demo, create a confirmed account directly from the dashboard without sending a confirmation email:

1. Open **Authentication → Users**.
2. Select **Add user → Create new user** (not the invitation option).
3. Enter a valid email address you control and a password of at least eight characters.
4. Enable **Auto Confirm User** and create the account.
5. When the app is running, use **Sign in** with these credentials; do not register the same account again.

Use an email address with a full domain. `localdemo@emnlp` is rejected by Supabase's email validator; use a real personal or university mailbox instead. You can still use `localdemo` as the display name.

If signup reports **email rate limit exceeded**, the built-in email provider currently allows only **two emails per hour per project**, shared across email-sending Auth endpoints. Creating the auto-confirmed demo account above avoids sending another confirmation email. For normal signup emails, wait for the rate-limit window to expire or configure [custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp). Repeated signup attempts do not bypass the limit. See [Supabase Auth rate limits](https://supabase.com/docs/guides/auth/rate-limits).

When registering through the app with email confirmation enabled, the login page displays a confirmation notice and waits for you to confirm your email and sign in. It only stores a login session when Supabase returns an access token.

The backend verifies access tokens through the project's JWKS endpoint. Use an asymmetric signing key such as ES256 whose public key is exposed there; legacy shared-secret signing does not provide a public key for this verification path. See [Supabase JWT signing keys](https://supabase.com/docs/guides/auth/signing-keys).

8. **Start both development servers**

From `conv_creator/`:

```sh
./start-dev.sh
```

The script loads `.env`, activates `backend/backend_env` when available, starts Uvicorn at `http://127.0.0.1:8000`, and starts Vite with `VITE_API_BASE=http://127.0.0.1:8000`. Press Ctrl+C to stop the development session.

Open `http://localhost:5173` and sign in. In **Settings → API**, select Groq or OpenAI, enter that provider's API key, and choose a model before using AI features. The provider, key, and model are saved per user.

If saving an API key fails with `new row violates row-level security policy for table "user_settings"`, ensure the backend is running the current code and `SUPABASE_SERVICE_ROLE_KEY` is set to the service role key from the same project. Settings use this backend-only client after login verification, with reads and writes scoped to the authenticated user's ID. Keep row-level security enabled; granting table privileges alone does not override its policies.

### Start the servers separately

In one terminal, from `conv_creator/`:

```sh
source backend/backend_env/bin/activate
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd frontend
VITE_API_BASE=http://127.0.0.1:8000 npm run dev
```

For PowerShell, set `$env:VITE_API_BASE = 'http://127.0.0.1:8000'` before running `npm run dev` in `frontend/`.

The backend loads `conv_creator/.env`, falling back to `backend/.env`. If you start Vite directly, set `VITE_API_BASE` in its environment or in `frontend/.env.local`; the Vite config does not proxy API requests. FastAPI's interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## 📜 Available Scripts

### Development

Run these commands from `frontend/`:

```sh
npm run dev          # Start development server with hot reload
npm run build        # Type-check and build for production
npm run build-only   # Build without type-checking
npm run preview      # Preview production build locally
npm run type-check   # Check Vue and TypeScript types
npm run lint         # Lint and apply fixes
npm run format       # Format src/ with Prettier
npm run test:e2e     # Run Playwright tests
```

The frontend production output is written to `frontend/dist/`. Set `VITE_API_BASE` before building when the deployed API uses a different origin. Frontend build and preview commands do not start the backend.

### Regression checks

From `conv_creator/`, with the backend virtual environment installed:

```sh
backend/backend_env/bin/python -m unittest discover -s backend/tests
```

From `frontend/`, install Playwright's Chromium browser once, then run the browser checks:

```sh
npx playwright install chromium
npm run test:e2e
```

The browser tests start a separate Vite server on port 5174 and mock signup responses. Backend unit tests mock Supabase access. These checks do not require a live Supabase project or send confirmation emails.

### Graph Components

- **DiscussionGraph**: Main graph container with view switching
- **TreeView**: Hierarchical tree visualization
- **ArgumentNode/ThesisNode**: Individual argument displays

### Chat Components

- **TelegramChat**: Main chat interface
- **ChatMessages**: Message history display
- **ChatInput**: Message composition
- **ChatHeader**: Chat title and controls

## 🔧 Development Tools

### Version Management

The frontend supports multiple Node.js version managers. Run them from `frontend/`, where their configuration files live:

- `.nvmrc` for nvm users
- `.node-version` for nodenv users
- `.tool-versions` for asdf users
