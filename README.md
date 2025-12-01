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

## ✔️ Requirements
To run the project locally, you will need:

- **Python 3.11+**  
- **pip / pip3**  
- **Node / React** (for frontend)   
- **MongoDB** (local or Docker)

---

# 🚀 How to Use (Local Development)

## 🔹 Run the API Service (`api/`)

cd api  
python3 -m pip install -r requirements.txt  
python3 -m uvicorn app.main:app --reload --port 8000  

Visit:
http://localhost:8000/health

Expected:
{"status": "ok", "service": "api"}

---

## 🔹 Run the AI Service (`ai-service/`)

Open a new terminal:

cd ai-service  
python3 -m pip install -r requirements.txt  
python3 -m uvicorn app.main:app --reload --port 8001  

Visit:
http://localhost:8001/health

Expected:
{"status": "ok", "service": "ai-service"}

---

# 🐳 Run Entire System with Docker (optional)

docker-compose build  
docker-compose up  

Stop:
docker-compose down  

---

# 🔐 Environment Variables

Create `.env` file (root or inside `api/`):

MONGO_URI=mongodb://localhost:27017/budgetbaddie  

Template (`env.example`):

MONGO_URI=mongodb://localhost:27017/budgetbaddie  
# TODO: add more variables later  

---

# 🧱 Application Structure

5-final-budgetbaddie/  
├── api/  
│   ├── app/  
│   │   ├── main.py  
│   │   └── (more files coming soon)  
│   ├── requirements.txt  
│   └── Dockerfile  
│  
├── ai-service/  
│   ├── app/  
│   │   ├── main.py  
│   │   └── (AI logic coming soon)  
│   ├── requirements.txt  
│   └── Dockerfile  
│  
├── frontend/  
│   └── (To be added)  
│  
├── docker-compose.yml  
├── instructions.md  
├── pyproject.toml  
└── README.md  

---

# 🧠 Tech Stack

### Backend  
- FastAPI  
- Uvicorn  
- MongoDB  
- Motor  
- Docker  

### Frontend  
(To be added — React planned)

### AI  
FastAPI microservice  
(To be expanded)

### DevOps  
GitHub Actions CI/CD (in progress)  
Docker Hub deployments (coming soon)  

---

# 🔮 Future Planning

- Full user authentication (Signup/Login)  
- Persistent budgeting/transaction history  
- AI-powered purchase recommendations  
- Integration of price scraping & spending insights  
- Visual analytics dashboard  
- Rewards and gamification  
- Deployment to DigitalOcean  
- Add CI badges, coverage badges  

---

# 👥 Team Members

- **Athena Luo – funfig_16**  
  Frontend UX Design & Database  
  https://github.com/funfig16  

- **Avi Herman – AviH7531**  
  System Building & Database  
  https://github.com/AviH7531  

- **Ezra Shapiro – ems9856-lgtm**  
  System Building & Data Visualization  
  https://github.com/ems9856-lgtm  

- **Mya Pyke – myapyke123**  
  AI & API Integration  
  https://github.com/myapyke123  

- **Tawhid Zaman – TawhidZGit**  
  Frontend Design & AI Integration  
  https://github.com/TawhidZGit  

---

# License