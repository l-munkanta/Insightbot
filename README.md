# InsightBot — Enterprise Data Intelligence Chatbot

An AI-powered chatbot that connects to a live business database and answers
natural language questions about customers, revenue, and operations — no SQL knowledge required.

## Demo

> Ask it anything about your business data:

**"Who are the top 10 customers at risk of churning?"**
> InsightBot runs a churn probability model across all customers and returns
> a ranked list with risk scores — powered by a trained RandomForest classifier.

**"Which customers have the highest monthly spend?"**
> Converts your question into SQL, queries the live database, and explains the results.

**"What is our refund policy for Pro customers?"**
> Searches internal policy documents using semantic vector search and returns the answer.

---

## What it does

- Converts natural language into SQL and queries a live SQLite business database
- Predicts customer churn risk using a trained scikit-learn RandomForest model
- Answers policy and product questions using RAG (ChromaDB + sentence-transformers)
- Manages a full agentic tool-use loop — the AI decides which tool to call,
  runs it, and loops until it has a complete answer
- Served through a FastAPI REST backend with a Streamlit chat interface

---

## Architecture

<img width="595" height="394" alt="Bildschirmfoto 2026-06-16 um 19 44 01" src="https://github.com/user-attachments/assets/a3655777-d1cc-485a-a635-675fbc5bb1a4" />

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | GPT-OSS 120B via Groq API (tool use / function calling) |
| Backend | FastAPI + Python |
| Database | SQLite (swappable to PostgreSQL) |
| ML model | scikit-learn RandomForestClassifier |
| Vector store | ChromaDB + sentence-transformers |
| Frontend | Streamlit |

---

## Project structure

<img width="595" height="402" alt="Bildschirmfoto 2026-06-16 um 19 46 07" src="https://github.com/user-attachments/assets/c7eee3d4-147b-45f0-b66a-a653b40f7a20" />

---

## Setup instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOURNAME/insightbot.git
cd insightbot
```

### 2. Create a virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your API key
Copy `.env.example` to `.env` and add your free Groq API key
(get one at console.groq.com — no credit card required):

GROQ_API_KEY=your_key_here

### 4. Generate the database and train the ML model
```bash
python3 data/seed_db.py
python3 models/train_model.py
```

### 5. Start the backend
```bash
uvicorn backend.main:app --reload
```

### 6. Start the frontend (open a second terminal)
```bash
streamlit run frontend/app.py
```

Open your browser at `http://localhost:8501`

---

## Sample questions to try

| Question | Tool used |
|---|---|
| Which customers have the highest monthly spend? | Text-to-SQL |
| Who are the top 10 customers at risk of churning? | ML prediction |
| How many completed orders were placed this year? | Text-to-SQL |
| What is our refund policy for Pro customers? | RAG document search |
| Show me all Enterprise customers from Germany | Text-to-SQL |
| What plan features does the Pro tier include? | RAG document search |

---

## Key technical decisions

**Why tool use instead of a single prompt?**
Giving the AI tools to call (SQL executor, ML model, document search) is more
reliable than asking it to answer from memory. Each tool returns real data,
so the AI always responds based on facts from the actual database.

**Why inject today's date into the system prompt?**
LLMs have a training cutoff and don't know the current date. Without this,
time-based queries like "this year" or "last 30 days" return wrong results.

**Why RandomForest for churn prediction?**
It handles class imbalance well with the `class_weight="balanced"` parameter,
requires no feature scaling, and produces calibrated probability scores — ideal
for ranking customers by risk level.

