# Budget Baddie 💰

[![Web CI/CD](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml)
[![API CI/CD](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml)

**Spend Smart, Slay Hard!💅**

An AI-powered budgeting app that helps you make smart financial decisions. Track income, manage expenses, visualize spending patterns, and get personalized AI advice before making purchases.

---

## 🌟 Features

- 📊 **Budget Planning**: Set monthly budgets by category
- 💰 **Income & Expense Tracking**: Track all financial transactions
- 📈 **Data Visualizations**: 
  - Budget vs actual spending comparison
  - Category-wise expense breakdown pie charts
  - Income capacity tracker
  - Per-category budget analysis with progress bars
- 🤖 **AI Budget Advisor**: Ask Google Gemini AI for spending advice
- 💾 **Savings Tracker**: Monitor monthly and total savings
- 🔒 **Budget Locking**: Lock budgets to prevent changes
- 🗑️ **Expense Management**: Delete unwanted transactions

---

## 👥 Team Members

- **[Athena Luo – funfig_16](https://github.com/funfig16)** – Frontend UX Design & Database 
- **[Avi Herman – AviH7531](https://github.com/avih7531)** – System Building & Database 
- **[Ezra Shapiro – ems9856-lgtm](https://github.com/ems9856-lgtm)** – System Building & Data Visualization 
- **[Mya Pyke – myapyke123](https://github.com/myapyke123)** – AI and API Incorporation 
- **[Tawhid Zaman – TawhidZGit](https://github.com/TawhidZGit)** – Front End Design & AI Incorporation

---

## 🏗️ Architecture

Budget Baddie consists of two containerized subsystems:

### 1. **Web Application** (Flask)
- **Technology**: Python Flask, Jinja2 templates, vanilla JavaScript
- **Port**: 5000
- **Docker Image**: [avih7531/budgetbaddie-web](https://hub.docker.com/r/avih7531/budgetbaddie-web)
- **Purpose**: User interface, authentication, budget management, AI integration

### 2. **API Service** (FastAPI)
- **Technology**: Python FastAPI, Motor (async MongoDB driver)
- **Port**: 8000
- **Docker Image**: [avih7531/budgetbaddie-api](https://hub.docker.com/r/avih7531/budgetbaddie-api)
- **Purpose**: REST API endpoints, potential future mobile app backend

### 3. **Database** (MongoDB)
- **Version**: MongoDB 7
- **Collections**: users, budget_plans, expenses, incomes, spending_habits, price_history

---

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11+
- MongoDB 7.x
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/swe-students-fall2025/5-final-budgetbaddie.git
cd 5-final-budgetbaddie
```

### Step 2: Install MongoDB

**macOS** (using Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Ubuntu/Debian**:
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows**:
Download and install from [MongoDB Download Center](https://www.mongodb.com/try/download/community)

### Step 3: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values:

```env
# MongoDB - leave as default for local development
MONGO_URI=mongodb://localhost:27017

# Flask Secret Key - generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-generated-secret-key

# Google Gemini AI API Key - get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration (optional - only needed for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Step 5: Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Step 6: (Optional) Run the API Service

```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

---

## 🔑 Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGO_URI` | Yes | MongoDB connection string | `mongodb://localhost:27017` |
| `SECRET_KEY` | Yes | Flask session encryption key | Generate with `secrets.token_hex(32)` |
| `GEMINI_API_KEY` | Yes | Google Gemini AI API key | Get from Google AI Studio |
| `MAIL_SERVER` | No | SMTP server for emails | `smtp.gmail.com` |
| `MAIL_PORT` | No | SMTP port | `587` |
| `MAIL_USE_TLS` | No | Use TLS for email | `True` |
| `MAIL_USERNAME` | No | Email account username | `your-email@gmail.com` |
| `MAIL_PASSWORD` | No | Email account password | Gmail app password |
| `MAIL_DEFAULT_SENDER` | No | Default sender email | `your-email@gmail.com` |

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

---

## 🏭 Production Pipeline

Budget Baddie uses GitHub Actions for continuous integration and deployment.

### CI/CD Workflow

```
Code Push to main → GitHub Actions → Build & Test → Docker Hub → Digital Ocean
```

### Workflow Details

#### **Web Application Workflow** (`web.yml`)

1. **Trigger**: Push or Pull Request to `main` branch
2. **Build & Test**:
   - Spins up MongoDB test container
   - Installs Python dependencies
   - Runs pytest with coverage requirements (80%+)
3. **Docker Build**:
   - Builds Docker image from `Dockerfile`
   - Uses build cache for faster builds
4. **Publish** (main branch only):
   - Logs in to Docker Hub
   - Pushes image with tags: `latest` and `<git-sha>`
5. **Deploy** (main branch only):
   - SSH into Digital Ocean droplet
   - Pulls latest image
   - Stops old container
   - Starts new container with environment variables
   - Health check verification

#### **API Service Workflow** (`api.yml`)

Same process as web, but:
- Works in `api/` directory
- Uses FastAPI-specific tests
- Deploys on port 8000
- Includes comprehensive test coverage (295+ lines of database tests)

---

## 🔐 GitHub Secrets

The following secrets must be configured in GitHub repository settings:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `DOCKER_USERNAME` | Docker Hub username | Your Docker Hub account |
| `DOCKER_PASSWORD` | Docker Hub password/token | Docker Hub → Account Settings → Security |
| `DO_HOST` | Digital Ocean droplet IP | From DO dashboard |
| `DO_USERNAME` | SSH username (usually `root`) | Digital Ocean setup |
| `DO_SSH_KEY` | Private SSH key for droplet | Generate with `ssh-keygen` |
| `MONGO_URI` | Production MongoDB URI | `mongodb://host.docker.internal:27017/budgetbaddie` |
| `SECRET_KEY` | Flask secret key | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GOOGLE_AI_API_KEY` | Gemini API key | Google AI Studio |

### Setting Secrets via CLI

```bash
# Example: Set Docker credentials
gh secret set DOCKER_USERNAME -b "your-username"
gh secret set DOCKER_PASSWORD -b "your-password"

# Set Digital Ocean credentials
gh secret set DO_HOST -b "138.68.251.91"
gh secret set DO_USERNAME -b "root"
gh secret set DO_SSH_KEY < ~/.ssh/id_rsa

# Set application secrets
gh secret set MONGO_URI -b "mongodb://host.docker.internal:27017/budgetbaddie"
gh secret set SECRET_KEY -b "$(python -c 'import secrets; print(secrets.token_hex(32))')"
gh secret set GOOGLE_AI_API_KEY -b "your-gemini-api-key"
```

---

## 🐳 Docker Images

- **Web Application**: [avih7531/budgetbaddie-web](https://hub.docker.com/r/avih7531/budgetbaddie-web)
- **API Service**: [avih7531/budgetbaddie-api](https://hub.docker.com/r/avih7531/budgetbaddie-api)

### Running with Docker Locally

```bash
# Run web application
docker run -d \
  --name budget-web \
  -p 5000:5000 \
  -e MONGO_URI="mongodb://host.docker.internal:27017/budgetbaddie" \
  -e SECRET_KEY="your-secret-key" \
  -e GEMINI_API_KEY="your-api-key" \
  avih7531/budgetbaddie-web:latest

# Run API service
docker run -d \
  --name budget-api \
  -p 8000:8000 \
  -e MONGO_URI="mongodb://host.docker.internal:27017/budgetbaddie" \
  -e GOOGLE_AI_API_KEY="your-api-key" \
  avih7531/budgetbaddie-api:latest
```

---

## 🧪 Running Tests

### Web Application Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest --cov=. --cov-report=term-missing --cov-report=html

# View coverage report
open htmlcov/index.html
```

### API Service Tests

```bash
cd api

# Run comprehensive test suite
pytest tests/ \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=html \
  -v

# The API has 295+ lines of database tests and 283+ lines of schema tests
```

---

## 📊 Database Collections

Budget Baddie uses MongoDB with the following collections:

| Collection | Purpose |
|------------|---------|
| `users` | User accounts with authentication |
| `budget_plans` | Monthly budget plans with category allocations |
| `expenses` | Expense transactions |
| `incomes` | Income transactions |
| `spending_habits` | User spending pattern analysis (future) |
| `price_history` | Historical price data (future) |

### Sample Data Structure

**Budget Plan**:
```json
{
  "user_id": ObjectId,
  "year": 2025,
  "month": 12,
  "total_budget": 1000.00,
  "category_budgets": {
    "Groceries": 400.00,
    "Rent": 500.00,
    "Extra": 100.00
  },
  "is_locked": false,
  "is_filled": true
}
```

**Expense**:
```json
{
  "user_id": ObjectId,
  "category": "Groceries",
  "amount": 50.00,
  "date": ISODate("2025-12-08"),
  "month": 12,
  "year": 2025,
  "note": "Weekly shopping"
}
```

---

## 🌐 Production Deployment

**Live Application**: http://138.68.251.91:5000

### Deployment Architecture

```
Digital Ocean Droplet (138.68.251.91)
├── MongoDB (systemd service, port 27017)
├── Flask Web App (Docker container, port 5000)
└── FastAPI Service (Docker container, port 8000)
```

### How Deployment Works

1. **Push to `main` branch** triggers GitHub Actions
2. **Automated workflow**:
   - Runs tests with MongoDB test database
   - Verifies 80% code coverage
   - Builds Docker image
   - Pushes to Docker Hub
   - SSHs into Digital Ocean droplet
   - Pulls latest image
   - Restarts container with new code
   - Performs health check

### Manual Deployment

If you need to deploy manually:

```bash
# SSH into the droplet
ssh root@138.68.251.91

# Pull latest images
docker pull avih7531/budgetbaddie-web:latest
docker pull avih7531/budgetbaddie-api:latest

# Restart web container
docker stop budget-web && docker rm budget-web
docker run -d \
  --name budget-web \
  -p 5000:5000 \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  -e MONGO_URI="mongodb://host.docker.internal:27017/budgetbaddie" \
  -e SECRET_KEY="<secret-key>" \
  -e GEMINI_API_KEY="<api-key>" \
  avih7531/budgetbaddie-web:latest

# Restart API container
docker stop budget-api && docker rm budget-api
docker run -d \
  --name budget-api \
  -p 8000:8000 \
  --add-host=host.docker.internal:host-gateway \
  --restart unless-stopped \
  -e MONGO_URI="mongodb://host.docker.internal:27017/budgetbaddie" \
  -e GOOGLE_AI_API_KEY="<api-key>" \
  avih7531/budgetbaddie-api:latest
```

---

## 💻 Tech Stack

### Frontend
- HTML5, CSS3 (Modern design with CSS variables)
- Vanilla JavaScript (no frameworks)
- Chart.js for data visualization
- Jinja2 templating

### Backend
- **Web**: Flask (Python web framework)
- **API**: FastAPI (async REST API framework)
- **Database**: MongoDB 7.x with PyMongo/Motor drivers
- **AI**: Google Gemini AI (gemini-2.0-flash-exp model)

### DevOps
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub
- **Hosting**: Digital Ocean
- **Deployment**: SSH-based automated deployment

### Testing
- pytest with coverage reporting
- Async test fixtures for API
- MongoDB test database integration

---

## 🛠️ Development Tips

### Generating a Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Accessing MongoDB Shell

```bash
# Local development
mongosh budgetbaddie

# Production (via SSH)
ssh root@138.68.251.91
mongosh budgetbaddie
```

### Viewing Container Logs

```bash
# On production server
ssh root@138.68.251.91
docker logs -f budget-web    # Follow web logs
docker logs -f budget-api    # Follow API logs
```

### Rebuilding After Code Changes

```bash
# Local testing
docker build -t budgetbaddie-web:local .
docker run -p 5000:5000 -e MONGO_URI="mongodb://host.docker.internal:27017" budgetbaddie-web:local

# For API
cd api
docker build -t budgetbaddie-api:local .
docker run -p 8000:8000 -e MONGO_URI="mongodb://host.docker.internal:27017" budgetbaddie-api:local
```

---

## 🐛 Troubleshooting

### MongoDB Connection Issues

**Problem**: `ServerSelectionTimeoutError`

**Solution**: 
- Verify MongoDB is running: `systemctl status mongod`
- Check `.env` has correct `MONGO_URI`
- For Docker: Use `host.docker.internal:27017` instead of `localhost:27017`

### Port Already in Use

**Problem**: `Address already in use: 5000`

**Solution**:
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python app.py --port 5001
```

### Docker Container Won't Start

**Problem**: Container exits immediately

**Solution**:
```bash
# Check logs for errors
docker logs budget-web

# Verify all environment variables are set
docker inspect budget-web | grep -A 20 "Env"
```

### AI Not Responding

**Problem**: Gemini API errors

**Solution**:
- Verify API key is correct and active
- Check model name is `gemini-2.0-flash-exp`
- Ensure API key has sufficient quota
- Check logs for specific error messages

---

## 📝 Project Structure

```
5-final-budgetbaddie/
├── app.py                      # Main Flask application
├── Dockerfile                  # Docker config for web app
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── templates/                 # HTML templates
│   ├── base.html
│   ├── dashboard.html         # Main dashboard with visualizations
│   ├── login.html
│   ├── signup.html
│   └── ...
├── static/                    # Static assets
│   ├── style.css              # Main stylesheet (1400+ lines)
│   ├── js/
│   └── *.png                  # Icons
├── api/                       # FastAPI service
│   ├── app/
│   │   ├── main.py
│   │   ├── ai_routes.py
│   │   ├── database.py
│   │   ├── models/            # Database models
│   │   └── schemas/           # Pydantic schemas
│   ├── tests/                 # Comprehensive test suite
│   ├── Dockerfile
│   └── requirements.txt
└── .github/
    └── workflows/
        ├── web.yml            # Web app CI/CD
        ├── api.yml            # API service CI/CD
        └── event-logger.yml   # Commit tracking
```

---

## 🎯 Key Features Explained

### Budget Planning
Users set monthly budgets divided into categories (Groceries, Rent, etc.). The system tracks spending against these budgets with visual indicators.

### AI Budget Advisor
Click the 🤖 emoji in the dashboard to ask questions like:
- "Can I afford a $50 dinner?"
- "Should I buy a $200 jacket?"

The AI analyzes your current budget, expenses, and income to provide personalized advice.

### Data Visualizations
- **Pie Chart**: Shows expense breakdown as percentage of total budget
- **Category Cards**: Per-category budget vs actual spending with progress bars
- **Income Tracker**: Horizontal bar showing expenses, remaining budget, and savings
- **Color Coding**: Green (under budget), Yellow (close), Red (over budget)

### Savings Calculator
Automatically calculates monthly savings as: `Income - Expenses` for each month, showing both monthly breakdown and cumulative total.

---

## 📦 Dependencies

### Main Application
- Flask 3.1.2 - Web framework
- pymongo 4.15.5 - MongoDB driver
- google-generativeai 0.8.5 - Gemini AI integration
- Flask-Mail - Email functionality
- python-dotenv - Environment variable management
- werkzeug - Security utilities
- bcrypt - Password hashing

### API Service
- FastAPI - Async web framework
- motor - Async MongoDB driver
- pydantic - Data validation
- uvicorn - ASGI server
- httpx - Async HTTP client
- pytest & pytest-asyncio - Testing

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

Built as the final project for Software Engineering course at NYU, Fall 2025.

Special thanks to Professor Bloomberg for the project requirements and guidance.
