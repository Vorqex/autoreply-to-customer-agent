# AutoReply AI

**AI-powered platform for automatically generating intelligent, context-aware replies to customer reviews across multiple platforms.**

AutoReply AI helps businesses maintain a consistent, timely, and on-brand response to every customer review. Using a multi-agent AI pipeline, the system analyzes sentiment, retrieves relevant knowledge, ensures safety compliance, and generates personalized replies — all with minimal human intervention.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            NGINX (80/443)                          │
│                      SSL / Rate Limiting / Proxy                    │
└────────┬────────────────────────────────────┬───────────────────────┘
         │ /api/*                              │ /*
         ▼                                     ▼
┌─────────────────┐                  ┌──────────────────────┐
│   FastAPI App   │                  │   Next.js Frontend   │
│   :8000         │                  │   :3000              │
│                 │                  │   React / TypeScript │
│  ┌───────────┐  │                  │   TanStack Query    │
│  │Agents     │  │                  │   Tailwind CSS      │
│  │Orchestrator│ │                  └──────────────────────┘
│  │Sentiment  │  │
│  │Reply Gen  │  │                  ┌──────────────────────┐
│  │Safety     │  │                  │   Celery Worker      │
│  │Quality    │  │                  │   Async Task Proc.   │
│  └───────────┘  │                  └──────────────────────┘
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────┐
│Postgres│ │Redis │
│ :5432  │ │:6379 │
└────────┘ └──────┘
```

---

## Features

- **Multi-Platform Review Ingestion** — Connect Google Business, Yelp, Trustpilot, Facebook, and more
- **Sentiment Analysis** — Automatic sentiment and emotion detection for every review
- **AI Reply Generation** — Context-aware replies using GPT-4o / configurable LLM
- **Brand Voice Customization** — Configure tone, style, and vocabulary to match your brand
- **Knowledge Base Integration** — Pull product info, FAQs, and policies into replies
- **Safety Guardrails** — Content moderation, PII detection, and risk classification
- **Quality Evaluation** — Automated review of generated replies before publishing
- **Multi-Tenant SaaS** — Isolated workspaces per business account
- **Async Processing** — Celery workers for review fetching, reply generation, and bulk operations
- **Audit Logging** — Full traceability of all generated and published replies

---

## Tech Stack

| Category        | Technology                                          |
| --------------- | --------------------------------------------------- |
| **Backend**     | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic       |
| **Frontend**    | Next.js 14, React 18, TypeScript, Tailwind CSS      |
| **Database**    | PostgreSQL 16, Redis 7                              |
| **Task Queue**  | Celery 5.4, Redis (broker/backend)                  |
| **AI/ML**       | OpenAI API, LangChain, Custom Agent Framework       |
| **Vector DB**   | Pinecone / Qdrant                                   |
| **Auth**        | JWT (access + refresh tokens), bcrypt               |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions         |
| **Reverse Proxy** | NGINX, SSL termination, rate limiting            |
| **Monitoring**  | Sentry, Prometheus                                  |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (for containerized setup)
- PostgreSQL 16 (if running outside Docker)
- Redis 7 (if running outside Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/autoreply-ai.git
cd autoreply-ai
```

### 2. Configure Environment Variables

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit `backend/.env` with your configuration:

```env
DATABASE_URL=postgresql+asyncpg://autoreply:password@localhost:5432/autoreply
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 3. Run with Docker (Recommended)

```bash
# Build and start all services
docker compose up -d

# Check service health
curl http://localhost:8000/api/v1/health

# View logs
docker compose logs -f
```

### 4. Run Locally (Development)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in a new terminal)
cd frontend
npm ci
npm run dev
```

The app will be available at:
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000/api/v1
- **API Docs:** http://localhost:8000/docs

---

## Docker Deployment

### Production Deploy

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Scale workers
docker compose up -d --scale celery-worker=3
```

### Environment Variables Reference

| Variable                     | Description                    | Default                     |
| ---------------------------- | ------------------------------ | --------------------------- |
| `DATABASE_URL`               | PostgreSQL connection string   | (required)                  |
| `REDIS_URL`                  | Redis connection string        | `redis://localhost:6379/0`  |
| `SECRET_KEY`                 | JWT signing secret             | (required)                  |
| `JWT_ALGORITHM`              | JWT signing algorithm          | `HS256`                     |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Access token TTL               | `30`                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | Refresh token TTL              | `7`                         |
| `OPENAI_API_KEY`             | OpenAI API key                 | (required)                  |
| `OPENAI_MODEL`               | LLM model name                 | `gpt-4o`                    |
| `EMBEDDING_MODEL`            | Embedding model                | `text-embedding-3-small`    |
| `VECTOR_DB_TYPE`             | Vector DB provider             | `pinecone`                  |
| `PINECONE_API_KEY`           | Pinecone API key               | (optional)                  |
| `QDRANT_URL`                 | Qdrant server URL              | (optional)                  |
| `CELERY_BROKER_URL`          | Celery broker URL              | (required)                  |
| `CELERY_RESULT_BACKEND`      | Celery result backend URL      | (required)                  |
| `CORS_ORIGINS`               | Allowed CORS origins           | `http://localhost:3000`     |
| `SENTRY_DSN`                 | Sentry DSN                     | (optional)                  |
| `RATE_LIMIT`                 | API rate limit                 | `100/minute`                |
| `AI_QUALITY_THRESHOLD`       | Minimum quality score (0-1)    | `0.85`                      |
| `SAFETY_SCORE_THRESHOLD`     | Minimum safety score (0-1)     | `0.90`                      |

---

## API Documentation

Once the backend is running, interactive API documentation is available:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

| Method | Path                    | Description              |
| ------ | ----------------------- | ------------------------ |
| POST   | `/api/v1/auth/login`    | User login               |
| POST   | `/api/v1/auth/signup`   | User registration        |
| GET    | `/api/v1/reviews`       | List reviews             |
| POST   | `/api/v1/replies/generate` | Generate a reply      |
| GET    | `/api/v1/businesses`    | List businesses          |
| GET    | `/api/v1/health`        | Health check             |

---

## Project Structure

```
autoreply-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── utils/           # Helper functions
│   │   └── workers/         # Celery task definitions
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── lib/             # API client, auth, utils
│   │   ├── providers/       # React context providers
│   │   ├── stores/          # State management
│   │   └── types/           # TypeScript type definitions
│   ├── Dockerfile
│   ├── next.config.js
│   └── package.json
├── data/
│   └── agent/               # Agent configuration & templates
├── docker/
│   ├── nginx.conf
│   └── entrypoint.sh
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   └── deploy.yml
│   └── CODEOWNERS
├── docker-compose.yml
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
└── SECURITY.md
```

---

---

## Deployment

### Architecture

```
                         ┌──────────────────────────┐
                         │        Vercel             │
                         │   Next.js Frontend        │
                         │   https://autoreply-ai...  │
                         └──────────┬───────────────┘
                                    │ HTTPS /api/v1/*
                                    ▼
                    ┌───────────────────────────────┐
                    │      Render / Railway          │
                    │                                │
                    │  ┌─────────────────────────┐   │
                    │  │  Web: FastAPI Backend   │   │
                    │  │  :8000                  │   │
                    │  └────────┬────────────────┘   │
                    │           │                     │
                    │      ┌────┴────┐               │
                    │      ▼         ▼                │
                    │  ┌────────┐ ┌──────┐           │
                    │  │Postgres│ │Redis │           │
                    │  └────────┘ └──────┘           │
                    │                                │
                    │  ┌─────────────────────────┐   │
                    │  │  Worker: Celery         │   │
                    │  │  Async tasks            │   │
                    │  └─────────────────────────┘   │
                    └────────────────────────────────┘
```

### Option 1: Vercel (Frontend) + Render (Backend) — Recommended

#### Prerequisites

- [Vercel](https://vercel.com) account (GitHub login)
- [Render](https://render.com) account (GitHub login)
- OpenAI API key
- (Optional) Pinecone API key for vector search

#### Deploy Backend on Render

1. Push your repository to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com) → **New +** → **Blueprint**
3. Connect your GitHub repo
4. Render automatically detects `render.yaml` and creates:
   - **PostgreSQL** database (`autoreply-db`)
   - **Redis** instance (`autoreply-redis`)
   - **Web Service** (`autoreply-backend`) — FastAPI
   - **Worker** (`autoreply-celery-worker`) — Celery tasks
5. After creation, go to each service and set the **secret environment variables** marked as `sync: false`:
   - `OPENAI_API_KEY` — Your OpenAI API key
   - `PINECONE_API_KEY` — (optional) For vector search
   - `SENTRY_DSN` — (optional) Error monitoring
   - `SECRET_KEY` — Auto-generated, but you can override
6. Wait for the build to finish, then note your backend URL:
   ```
   https://autoreply-backend.onrender.com
   ```
7. Verify health: `curl https://autoreply-backend.onrender.com/health`

#### Deploy Frontend on Vercel

1. In **Vercel Dashboard** → **Add New** → **Project**
2. Import your GitHub repository
3. Vercel auto-detects `vercel.json` with `rootDirectory: "frontend"`
4. **Environment Variables** (required):
   ```
   NEXT_PUBLIC_API_URL=https://autoreply-backend.onrender.com/api/v1
   NEXT_PUBLIC_APP_URL=https://autoreply-ai.vercel.app
   ```
5. Click **Deploy**
6. Vercel builds and deploys your Next.js frontend

#### Post-Deployment

1. Update `CORS_ORIGINS` on Render:
   ```env
   CORS_ORIGINS=https://autoreply-ai.vercel.app
   ```
2. Test the full flow:
   - Visit your Vercel URL
   - Create an account
   - Verify API communication works

### Option 2: Vercel (Frontend) + Railway (Backend)

#### Deploy Backend on Railway

1. Push to GitHub
2. Go to [Railway Dashboard](https://railway.app/dashboard) → **New Project**
3. Choose **Deploy from GitHub repo**
4. Railway auto-detects the `backend/` directory
5. Add Railway services:
   - **PostgreSQL** plugin
   - **Redis** plugin
   - **Web Service** — `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Worker** — `cd backend && celery -A app.workers.celery_app worker -l info`
6. Configure environment variables (same as Render above)
7. Deploy

#### Deploy Frontend on Vercel

Same steps as Option 1.

### Option 3: Docker Compose (Self-Hosted)

```bash
# Build and start all services
docker compose up -d

# Run migrations
docker compose exec backend alembic upgrade head

# Check health
curl http://localhost:8000/health
```

### Environment Variables Reference

| Variable | Required | Description | Example |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ (Vercel) | Backend API URL | `https://api.autoreply.ai/api/v1` |
| `NEXT_PUBLIC_APP_URL` | ✅ (Vercel) | Frontend URL | `https://autoreply.ai` |
| `DATABASE_URL` | ✅ (Backend) | PostgreSQL connection | `postgresql+asyncpg://...` |
| `SECRET_KEY` | ✅ (Backend) | JWT signing secret (min 32 chars) | — |
| `OPENAI_API_KEY` | ✅ (Backend) | OpenAI API key | `sk-...` |
| `REDIS_URL` | ✅ (Backend) | Redis connection | `redis://...` |
| `CELERY_BROKER_URL` | ✅ (Backend) | Celery broker (same as REDIS_URL) | `redis://.../1` |
| `CELERY_RESULT_BACKEND` | ✅ (Backend) | Celery result backend | `redis://.../1` |
| `CORS_ORIGINS` | ✅ (Backend) | Allowed CORS origins | `https://autoreply.ai` |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit changes: `git commit -m "feat: add my feature"`
4. Push: `git push origin feat/my-feature`
5. Open a Pull Request

### Development Guidelines

- Follow existing code style (Black for Python, Prettier for frontend)
- Write tests for new functionality
- Update API documentation for endpoint changes
- Run lint and tests before pushing

```bash
make lint
make test
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  Built with ❤️ for businesses that value their customers.
</div>
