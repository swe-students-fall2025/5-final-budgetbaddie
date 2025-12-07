
[![api ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml)
[![ai-service ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/ai-service.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/ai-service.yml)
[![web ci/cd](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml)

# Budget Baddie 💰
**Spend Smart, Slay Hard!💅**

An AI-powered budgeting app that helps you track expenses, plan budgets, and make smart spending decisions.

---

## Quick Start

### Prerequisites
- **Docker** and **Docker Compose** installed

### Local Development

1. **Clone the repository:**
```bash
git clone <repository-url>
cd 5-final-budgetbaddie
```

2. **Start all services:**
```bash
docker compose up -d
```

This single command starts:
- **MongoDB** on port `27017`
- **Web service (Flask)** on port `5000` - Main UI
- **API service (FastAPI)** on port `8000` - REST API
- **AI service (FastAPI)** on port `8001` - AI features

3. **Access the application:**
- Open `http://localhost:5000` in your browser

4. **View logs:**
```bash
docker compose logs -f
```

5. **Stop services:**
```bash
docker compose down
```

**That's it!** No Python installation, no virtual environments, no manual service startup. Everything runs in Docker.

---

## Production Deployment

### CI/CD Pipeline

When code is pushed to `main`:
1. All services run tests
2. Docker images are built and pushed to DockerHub
3. Services are automatically deployed to Digital Ocean

### Services on Digital Ocean
- **Web**: `budget-web` container on port `5000`
- **API**: `budget-api` container on port `8000`
- **AI Service**: `budget-ai-service` container on port `8001`
- **MongoDB**: Systemd service (`mongod`) running directly on the droplet on port `27017`

### Required GitHub Secrets
- `DOCKER_USERNAME` / `DOCKER_PASSWORD` - DockerHub credentials
- `MONGO_URI` - MongoDB connection string
- `SECRET_KEY` - Flask session secret
- `MAIL_USERNAME` / `MAIL_PASSWORD` / `MAIL_DEFAULT_SENDER` - Email configuration
- `GOOGLE_AI_API_KEY` - Google AI API key
- `DO_HOST` / `DO_USERNAME` / `DO_SSH_KEY` - Digital Ocean deployment credentials

---

## Project Structure

```
5-final-budgetbaddie/
├── app.py                    # Flask web service (port 5000)
├── Dockerfile                 # Web service container
├── docker-compose.yml        # All services orchestration
├── requirements.txt          # Web service dependencies
│
├── api/                       # FastAPI service (port 8000)
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/           # Database models
│   │   └── schemas/          # Pydantic schemas
│   └── Dockerfile
│
└── ai-service/                # AI service (port 8001)
    ├── app/
    │   ├── main.py
    │   └── service.py        # Google AI integration
    └── Dockerfile
```

---

## Tech Stack

- **Frontend**: Flask (Python)
- **Backend API**: FastAPI (Python)
- **AI Service**: FastAPI with Google Gemini
- **Database**: MongoDB 7
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions → DockerHub → Digital Ocean

---

## Team Members

- **[Athena Luo – funfig_16](https://github.com/funfig16)** – Frontend UX Design & Database 
- **[Avi Herman – AviH7531](https://github.com/avih7531)** – System Building & Database 
- **[Ezra Shapiro – ems9856-lgtm](https://github.com/ems9856-lgtm)** – System Building & Data Visualization 
- **[Mya Pyke – myapyke123](https://github.com/myapyke123)** – AI and API Incorporation 
- **[Tawhid Zaman – TawhidZGit](https://github.com/TawhidZGit)** – Front End Design & AI Incorporation  

---

# License
