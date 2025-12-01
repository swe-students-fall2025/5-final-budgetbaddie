# Final Project

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

### Automatic Setup

Database indexes are **automatically created** when the API service starts. No manual setup required!

### Manual Initialization (Optional)

If you need to manually initialize the database:

```bash
docker exec -it budget-api python -m api.scripts.init_db
```

### Seed Data (Optional)

To populate the database with sample test data:

```bash
docker exec -it budget-api python -m api.scripts.seed_data
```

This creates:
- Test user: `test@budgetbaddie.com`
- Sample budget plan for current month
- Sample expenses and income entries

### Environment Variables

The default MongoDB connection is configured in `docker-compose.yml`:
```
MONGO_URI=mongodb://mongo:27017/budgetbaddie
```

For local development without Docker, create `api/.env`:
```bash
cp api/.env.example api/.env
```

Then set:
```
MONGO_URI=mongodb://localhost:27017/budgetbaddie
```

### Database Schema

**Collections:**
- `users` - User accounts and authentication
- `budget_plans` - Monthly budget planning data
- `expenses` - Expense tracking with categories
- `incomes` - Income tracking
- `spending_habits` - AI analysis data for spending patterns
- `price_history` - Historical price data for AI suggestions

**Indexes:**
- User-based queries (`user_id`)
- Time-based queries (`date`, `month`, `year`)
- Category filtering (`category`)
- Unique constraints (user email, budget plans per month)

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
- **Database**: MongoDB 7
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support

# Future Planning

# Team Members
## 👥 Team Members
- **[Athena Luo – funfig_16](https://github.com/funfig16)** – Frontend UX Design & Database 
- **[Avi Herman – AviH7531](https://github.com/avih7531)** – System Building & Database 
- **[Ezra Shapiro – ems9856-lgtm](https://github.com/ems9856-lgtm)** – System Building & Data Visualization 
- **[Mya Pyke – myapyke123](https://github.com/myapyke123)** – AI and API Incorporation 
- **[Tawhid Zaman – TawhidZGit](https://github.com/TawhidZGit)** – Front End Design & AI Incorporation  


# License