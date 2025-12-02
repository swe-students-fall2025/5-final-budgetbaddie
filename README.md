# Final Project
<!-- CI/CD Status Badges -->
[![api ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml)
[![ai-service ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/ai-service.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/ai-service.yml)

---
 

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
- For local development: **Python 3.11+**

## Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd 5-final-budgetbaddie
```

2. **Start all services:**
```bash
docker compose up -d
```

This starts:
- **MongoDB** on port `27017`
- **API service** on port `8000`
- **AI service** on port `8001`

3. **Verify services are running:**
```bash
# Check API health
curl http://localhost:8000/health

# Check AI service health
curl http://localhost:8001/health
```

4. **Stop services:**
```bash
docker compose down
```

## Database Setup

### Production Database (Digital Ocean)

The production MongoDB database is **hosted on Digital Ocean**. The database runs on a Digital Ocean droplet and is accessible remotely. Connection details are configured through GitHub Secrets for CI/CD deployments.

**Database Details:**
- **Host**: Digital Ocean droplet
- **Database Name**: `budgetbaddie`
- **Collections**: `users`, `budget_plans`, `expenses`, `incomes`, `spending_habits`, `price_history`

### Local Development Database

For local development with Docker Compose, MongoDB runs in a container:

```bash
docker compose up -d
```

This starts MongoDB on port `27017` locally. The API service automatically connects to it.

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
   - MongoDB connection is configured in `docker-compose.yml`
   - Default: `mongodb://mongo:27017/budgetbaddie`

No `.env` files are required for local development when using Docker Compose. The services are configured to work out of the box.

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
├── api/                          # Main API service
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
├── ai-service/                   # AI service
│   ├── app/
│   │   └── main.py              # AI service FastAPI app
│   ├── Dockerfile               # AI service container definition
│   └── requirements.txt         # Python dependencies
│
├── docker-compose.yml           # Service orchestration
└── README.md                    # This file
```

# Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB 7 (hosted on Digital Ocean)
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support
- **Deployment**: Digital Ocean (droplet hosting MongoDB and services)
- **CI/CD**: GitHub Actions (automated build, test, and deployment)

# Future Planning

# Team Members
## 👥 Team Members
- **[Athena Luo – funfig_16](https://github.com/funfig16)** – Frontend UX Design & Database 
- **[Avi Herman – AviH7531](https://github.com/avih7531)** – System Building & Database 
- **[Ezra Shapiro – ems9856-lgtm](https://github.com/ems9856-lgtm)** – System Building & Data Visualization 
- **[Mya Pyke – myapyke123](https://github.com/myapyke123)** – AI and API Incorporation 
- **[Tawhid Zaman – TawhidZGit](https://github.com/TawhidZGit)** – Front End Design & AI Incorporation  


# License