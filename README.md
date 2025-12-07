
[![api ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml)
[![ai-service ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/ai-service.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/ai-service.yml)
[![web ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml)

# Final Project


---


# Budget Baddie 💰
**Spend Smart, Slay Hard!💅**

Ever want to buy something unnecessary at 2 am?
Budget Baddie is here to help you make the right money decision!

---

# Overview 🔍
An AI powered budgeting app that helps you say YES to:
- ☑️ Money Tracking   
- ☑️ Healthy Spending Habits  
- ☑️ REAL Budgeting   

...and NO to impulse buys and end-of-month panic!

**Think Twice, Swipe Right!**

---

# Features 📁
- Monthly budget planning
- Data visualization dashboard
- Income and expense analysis
- AI-powered purchase assistance
- Reward system for smart spending

# Getting Started 🚀

## Prerequisites

- **Docker** and **Docker Compose** installed
- No Python installation required - everything runs in Docker!

## Local Development

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd 5-final-budgetbaddie
```

2. **Start all services with a single command:**
```bash
docker compose up -d
```

This single command starts all services:
- **MongoDB** on port `27017`
- **Web service (Flask)** on port `5000`
- **API service (FastAPI)** on port `8000`
- **AI service (FastAPI)** on port `8001`

3. **Access the application:**
- Open your browser and navigate to `http://localhost:5000`
- The web interface is now running and connected to all backend services

4. **Verify services are running:**
```bash
# Check web service (Flask)
curl http://localhost:5000/

# Check API health
curl http://localhost:8000/health

# Check AI service health
curl http://localhost:8001/health
```

5. **View logs:**
```bash
# View all service logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f web
docker compose logs -f api
docker compose logs -f ai-service
```

6. **Stop services:**
```bash
docker compose down
```

### Local Development Workflow

- **No virtual environment needed** - all dependencies are in Docker containers
- **No manual service startup** - `docker compose up` handles everything
- **Hot reload**: For development, you can mount volumes to enable live code reloading (see docker-compose.yml)
- **Database access**: MongoDB is accessible at `mongodb://localhost:27017/budgetbaddie` from your host machine

## Production Deployment

### CI/CD Pipeline

The application uses GitHub Actions for automated CI/CD. When code is pushed to the `main` or `master` branch:

1. **Automated Testing**: All services run their test suites
2. **Docker Image Build**: Each service builds its Docker image
3. **Push to DockerHub**: Images are tagged and pushed to DockerHub
4. **Deploy to Digital Ocean**: Services are automatically deployed to the Digital Ocean droplet

### Production Services

All three services are deployed as separate containers on Digital Ocean:
- **Web service**: `budget-web` container on port `5000`
- **API service**: `budget-api` container on port `8000`
- **AI service**: `budget-ai-service` container on port `8001`

### GitHub Secrets Required

The following secrets must be configured in GitHub for production deployment:
- `DOCKER_USERNAME` - DockerHub username
- `DOCKER_PASSWORD` - DockerHub password
- `MONGO_URI` - MongoDB connection string for production
- `SECRET_KEY` - Flask secret key for sessions
- `MAIL_USERNAME` - Email username for password reset
- `MAIL_PASSWORD` - Email password for password reset
- `MAIL_DEFAULT_SENDER` - Default email sender address
- `DO_HOST` - Digital Ocean droplet IP address
- `DO_USERNAME` - SSH username for deployment
- `DO_SSH_KEY` - SSH private key for deployment

### Manual Production Deployment

If you need to manually deploy:

```bash
# SSH into Digital Ocean droplet
ssh $DO_USERNAME@$DO_HOST

# Pull latest images
docker pull $DOCKER_USERNAME/budgetbaddie-web:latest
docker pull $DOCKER_USERNAME/budgetbaddie-api:latest
docker pull $DOCKER_USERNAME/budgetbaddie-ai-service:latest

# Stop and remove old containers
docker stop budget-web budget-api budget-ai-service || true
docker rm budget-web budget-api budget-ai-service || true

# Start new containers with environment variables
docker run -d --name budget-web -p 5000:5000 \
  --env MONGO_URI=$MONGO_URI \
  --env SECRET_KEY=$SECRET_KEY \
  --env MAIL_USERNAME=$MAIL_USERNAME \
  --env MAIL_PASSWORD=$MAIL_PASSWORD \
  --env MAIL_DEFAULT_SENDER=$MAIL_DEFAULT_SENDER \
  $DOCKER_USERNAME/budgetbaddie-web:latest

docker run -d --name budget-api -p 8000:8000 \
  --env MONGO_URI=$MONGO_URI \
  $DOCKER_USERNAME/budgetbaddie-api:latest

docker run -d --name budget-ai-service -p 8001:8001 \
  $DOCKER_USERNAME/budgetbaddie-ai-service:latest
```

## Database Setup

### Production Database (Digital Ocean)

The production MongoDB database is **hosted on Digital Ocean**. The database runs on a Digital Ocean droplet and is accessible remotely. Connection details are configured through GitHub Secrets for CI/CD deployments.

**Database Details:**
- **Host**: Digital Ocean droplet
- **Database Name**: `budgetbaddie`
- **Collections**: `users`, `budget_plans`, `expenses`, `incomes`, `spending_habits`, `price_history`

### Local Development Database

For local development with Docker Compose, MongoDB runs in a container and is automatically started with `docker compose up -d`. All services (web, api, ai-service) automatically connect to the MongoDB container using the service name `mongo` in the Docker network.

### Automatic Index Creation

Database indexes are **automatically created** when the API service starts. No manual setup required! The indexes include:
- User-based queries (`user_id`)
- Time-based queries (`date`, `month`, `year`)
- Category filtering (`category`)
- Unique constraints (user email, budget plans per month)

### Manual Database Operations (Optional)

If you need to manually initialize the database or seed data:

```bash
# Initialize indexes manually
docker exec -it budget-api python -m api.scripts.init_db

# Seed sample data
docker exec -it budget-api python -m api.scripts.seed_data
```

### Environment Variables

**Note**: This project uses **Digital Ocean for production** and **Docker Compose for local development**. Environment variables are primarily configured through:

1. **GitHub Secrets** (for CI/CD and production deployment)
   - `MONGO_URI` - MongoDB connection string for production
   - `DO_HOST` - Digital Ocean droplet IP address
   - `DO_USERNAME` - SSH username for deployment
   - `DO_SSH_KEY` - SSH private key for deployment

2. **Docker Compose** (for local development)
   - All environment variables are configured in `docker-compose.yml`
   - MongoDB connection: `mongodb://mongo:27017/budgetbaddie` (uses Docker service name)
   - Flask secret key defaults to `dev-secret` (override with `SECRET_KEY` env var)
   - Email settings are optional for local development

No `.env` files are required for local development when using Docker Compose. The services are configured to work out of the box with sensible defaults.

### Database Schema

**Collections:**
- `users` - User accounts and authentication
  - Fields: `_id`, `email` (unique), `password_hash`, `name`, `created_at`, `updated_at`
- `budget_plans` - Monthly budget planning data
  - Fields: `_id`, `user_id`, `month`, `year`, `total_budget`, `categories` (object), `created_at`, `updated_at`
- `expenses` - Expense tracking with categories
  - Fields: `_id`, `user_id`, `budget_plan_id`, `category`, `amount`, `is_essential`, `date`, `month`, `year`, `description`, `created_at`, `updated_at`
- `incomes` - Income tracking
  - Fields: `_id`, `user_id`, `budget_plan_id`, `amount`, `is_recurring`, `date`, `month`, `year`, `source`, `created_at`, `updated_at`
- `spending_habits` - AI analysis data for spending patterns
  - Fields: `_id`, `user_id` (unique), `habits` (object with analysis data), `created_at`, `updated_at`
- `price_history` - Historical price data for AI suggestions
  - Fields: `_id`, `item_name`, `price`, `date`, `store`, `created_at`

**Relationships:**
- Users have many budget plans, expenses, and incomes
- Users have one spending habits record
- Budget plans can have many expenses and incomes
- Expenses and incomes reference both users and budget plans

# Application Structure 📁

```
5-final-budgetbaddie/
├── api/                          # Main API service (FastAPI)
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # MongoDB connection & index setup
│   │   ├── models/              # Database models (User, BudgetPlan, etc.)
│   │   │   ├── user.py
│   │   │   ├── budget_plan.py
│   │   │   ├── expense.py
│   │   │   ├── income.py
│   │   │   ├── spending_habit.py
│   │   │   └── price_history.py
│   │   └── schemas/             # Pydantic validation schemas
│   │       ├── user.py
│   │       ├── budget_plan.py
│   │       ├── expense.py
│   │       ├── income.py
│   │       ├── spending_habit.py
│   │       └── price_history.py
│   ├── scripts/                 # Database utilities
│   │   ├── init_db.py           # Initialize database indexes
│   │   └── seed_data.py         # Seed sample data
│   ├── tests/                   # Unit tests
│   │   ├── conftest.py          # Test fixtures
│   │   └── test_database.py     # Database model tests
│   ├── Dockerfile               # API container definition
│   └── requirements.txt         # Python dependencies
│
├── ai-service/                   # AI service (FastAPI)
│   ├── app/
│   │   └── main.py              # AI service FastAPI app
│   ├── Dockerfile               # AI service container definition
│   └── requirements.txt         # Python dependencies
│
├── app.py                        # Web service (Flask) - main entry point
├── templates/                    # Flask HTML templates
├── static/                       # Flask static files (CSS, JS, images)
├── Dockerfile                    # Web service container definition
├── requirements.txt              # Web service Python dependencies
├── docker-compose.yml            # Service orchestration (all services)
└── README.md                     # This file
```

# Tech Stack

- **Frontend**: Flask (Python) - Web interface
- **Backend API**: FastAPI (Python) - REST API service
- **AI Service**: FastAPI (Python) - AI-powered features
- **Database**: MongoDB 7 (hosted on Digital Ocean for production, Docker for local)
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support
- **Deployment**: Digital Ocean (droplet hosting all services)
- **CI/CD**: GitHub Actions (automated build, test, and deployment to DockerHub and Digital Ocean)

# Future Planning

# Team Members
## 👥 Team Members
- **[Athena Luo – funfig_16](https://github.com/funfig16)** – Frontend UX Design & Database 
- **[Avi Herman – AviH7531](https://github.com/avih7531)** – System Building & Database 
- **[Ezra Shapiro – ems9856-lgtm](https://github.com/ems9856-lgtm)** – System Building & Data Visualization 
- **[Mya Pyke – myapyke123](https://github.com/myapyke123)** – AI and API Incorporation 
- **[Tawhid Zaman – TawhidZGit](https://github.com/TawhidZGit)** – Front End Design & AI Incorporation  


# License