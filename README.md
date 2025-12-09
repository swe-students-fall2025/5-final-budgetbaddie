# Budget Baddie 💰

[![Web CI/CD](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/web.yml)
[![API CI/CD](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml/badge.svg)](https://github.com/swe-students-fall2025/5-final-budgetbaddie/actions/workflows/api.yml)

**Spend Smart, Slay Hard!💅**

An AI-powered budgeting app that helps you track income, manage expenses, visualize spending patterns, and get personalized financial advice from Google Gemini AI.

**Live App**: http://138.68.251.91:5000/

---

## 👥 Team Members

- **[Athena Luo – funfig_16](https://github.com/funfig16)** – Backend Dev & Frontend UX Design & Database 
- **[Avi Herman – AviH7531](https://github.com/avih7531)** – Backend Dev & Frontend UI Design & System Building & Database 
- **[Ezra Shapiro – ems9856-lgtm](https://github.com/ems9856-lgtm)** – System Building & Data Visualization 
- **[Mya Pyke – myapyke123](https://github.com/myapyke123)** – AI and API Incorporation 
- **[Tawhid Zaman – TawhidZGit](https://github.com/TawhidZGit)** – Front End Design & AI Incorporation

---

## 🚀 Local Development

### Prerequisites

- Python 3.11+
- MongoDB 7.x
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/swe-students-fall2025/5-final-budgetbaddie.git
cd 5-final-budgetbaddie
```

2. **Install MongoDB**

**macOS**:
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**Ubuntu/Debian**:
```bash
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows**: Download from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)

3. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy the example file and edit it:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
MONGO_URI=mongodb://localhost:27017
SECRET_KEY=your-generated-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

**Generate a secret key**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Get a Gemini API key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

### (Optional) Run the API Service

```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | Yes | MongoDB connection string |
| `SECRET_KEY` | Yes | Flask session encryption key |
| `GEMINI_API_KEY` | Yes | Google Gemini AI API key |
| `MAIL_SERVER` | No | SMTP server (for password reset) |
| `MAIL_USERNAME` | No | Email account |
| `MAIL_PASSWORD` | No | Email password |

See `.env.example` for a complete template.

---

## 🐳 Docker Images

- Web App: [avih7531/budgetbaddie-web](https://hub.docker.com/r/avih7531/budgetbaddie-web)
- API Service: [avih7531/budgetbaddie-api](https://hub.docker.com/r/avih7531/budgetbaddie-api)

---

## 🌐 Production

The app is deployed to Digital Ocean and accessible at **http://138.68.251.91:5000/**

Pushing to the `main` branch automatically triggers CI/CD workflows that:
1. Run tests with 80% coverage requirement
2. Build Docker images
3. Push to Docker Hub
4. Deploy to Digital Ocean

### GitHub Secrets (for CI/CD)

The following secrets are configured in the repository:

- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password
- `DO_HOST` - Digital Ocean droplet IP (138.68.251.91)
- `DO_USERNAME` - SSH username for deployment
- `DO_SSH_KEY` - SSH private key
- `MONGO_URI` - Production MongoDB connection string
- `SECRET_KEY` - Production Flask secret key
- `GOOGLE_AI_API_KEY` - Gemini AI API key

---

## 🧪 Running Tests

```bash
pip install pytest pytest-cov
pytest --cov=. --cov-report=term-missing
```

For the API service:
```bash
cd api
pytest tests/ --cov=app --cov-report=term-missing -v
```

---

## 💻 Tech Stack

- **Frontend**: HTML/CSS/JavaScript, Chart.js
- **Backend**: Flask (web), FastAPI (API)
- **Database**: MongoDB 7
- **AI**: Google Gemini AI
- **Deployment**: Docker, GitHub Actions, Digital Ocean

---

## 🎨 Features

- Monthly budget planning with category breakdown
- Income and expense tracking
- Interactive data visualizations (pie charts, progress bars, capacity tracker)
- AI-powered spending advice via chat interface
- Savings calculator
- Budget locking to prevent overspending
- Mobile-responsive design

---

## 📝 License

MIT License
