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

# System Setup

## Prerequisites
- Docker and Docker Compose installed
- Python 3.11+ (for local development)

## Database Setup

### Using Docker Compose (Recommended)

1. Start MongoDB and all services:
```bash
docker-compose up -d
```

This will start:
- MongoDB on port `27017`
- API service on port `8000`
- AI service on port `8001`

### Environment Variables

1. Copy the example environment file:
```bash
cp api/.env.example api/.env
```

2. The default `MONGO_URI` in docker-compose is:
```
mongodb://mongo:27017/budgetbaddie
```

For local development without Docker, use:
```
mongodb://localhost:27017/budgetbaddie
```

### Database Initialization

The database indexes are automatically created when the API service starts. To manually initialize:

```bash
# Inside the API container
docker exec -it budget-api python -m api.scripts.init_db
```

### Seed Data (Optional)

To populate the database with sample data for testing:

```bash
# Inside the API container
docker exec -it budget-api python -m api.scripts.seed_data
```

This creates:
- A test user: `test@budgetbaddie.com`
- Sample budget plan for current month
- Sample expenses and income

## Database Schema

### Collections

- **users**: User accounts and authentication
- **budget_plans**: Monthly budget planning data
- **expenses**: Expense tracking with categories
- **incomes**: Income tracking
- **spending_habits**: AI analysis data for spending patterns
- **price_history**: Historical price data for AI suggestions

### Indexes

All collections have optimized indexes for:
- User-based queries (`user_id`)
- Time-based queries (`date`, `month`, `year`)
- Category filtering (`category`)
- Unique constraints (user email, budget plans per month)

# How to Use

# Application Structure

```
api/
├── app/
│   ├── main.py           # FastAPI application
│   ├── database.py       # MongoDB connection
│   ├── models/           # Database models
│   └── schemas/          # Pydantic schemas
├── scripts/              # Database initialization scripts
└── tests/                # Unit tests

ai-service/
└── app/
    └── main.py          # AI service application
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