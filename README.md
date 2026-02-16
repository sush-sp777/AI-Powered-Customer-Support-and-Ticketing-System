# 🚀 SupportIQ – AI-Powered Customer Support Automation Platform

- SupportIQ is an AI-powered customer support automation system that intelligently triages support tickets, decides whether they can be safely auto-resolved, and assists human agents when needed.
- The system combines structured LLM classification, risk-based decision logic, and retrieval-augmented generation (RAG) to create a safe and practical AI support workflow.
---

## 📌 Project Overview

Customer support teams spend significant time:

- Manually categorizing tickets
- Prioritizing requests
- Answering repetitive questions
- Escalating sensitive issues

SupportIQ automates this process using AI — but with guardrails.

Instead of blindly auto-replying, the system:

- Classifies the ticket using an LLM
- Evaluates risk and confidence
- Decides whether to auto-resolve or escalate
- Assists agents with AI-generated drafts when needed

This ensures automation without losing human control.

---

## 🎯 Key Features
### ✅ AI Ticket Triage (Structured Output)

- Classifies tickets into categories
- Assigns priority level
- Detects sentiment
- Evaluates risk (LOW / MEDIUM / HIGH)
- Calculates confidence score
- Generates a short AI summary

The LLM returns structured JSON, making the system reliable and predictable.

### ✅ Risk-Based Decision Engine

After AI classification, a rule-based decision engine determines:
- Low risk + high confidence → Auto resolve
- Otherwise → Route to human agent

This prevents unsafe automation.

### ✅ Retrieval-Augmented Generation (RAG)

For auto-resolved tickets:

- Retrieves relevant information from internal knowledge base
- Uses embeddings + vector search (FAISS)
- Generates grounded responses
- Reduces hallucination risk

### ✅ Human-in-the-Loop Agent Assistance

For escalated tickets:

- Agents can generate AI reply drafts
- AI uses:
  - Ticket context
  - Conversation history
  - Sentiment
  - Risk level
- Agent reviews and sends final response

AI assists — humans stay in control.

### ✅ Role-Based Authentication

- JWT-based authentication
- USER and AGENT roles
- Secure password hashing
- Protected endpoints

---

## 🏗 System Architecture
```scss
User Dashboard
      ↓
FastAPI Backend (Auth + Ticket API)
      ↓
Ticket Stored in PostgreSQL
      ↓
AI Triage (LLM → Structured JSON)
      ↓
Extract:
• Category
• Priority
• Sentiment
• Risk
• Confidence
      ↓
Decision Engine
      ├── If (Risk = LOW) AND (Confidence ≥ 0.70)
      │         ↓
      │     RAG Engine (Vector Search + Context)
      │         ↓
      │     LLM Grounded Response
      │         ↓
      │     Auto-Resolve Ticket
      │         ↓
      │     Save Response to Database
      │
      └── Else
                ↓
           Route to Agent Queue
                ↓
           Agent Dashboard
                ↓
           AI Draft Generator
                ↓
           Human Review & Edit
                ↓
           Final Response Sent
                ↓
           Save Response to Database

```
---

## 📡 API Endpoints

### 🔐 Authentication
- POST /auth/register  
- POST /auth/login  
- GET /auth/me  
- GET /auth/agent-only  

### 🎫 Tickets
- POST /tickets/  
- GET /tickets/my  
- GET /tickets/agent/pending  
- POST /tickets/{ticket_id}/generate-draft  
- POST /tickets/{ticket_id}/reply  
- GET /tickets/{ticket_id}/messages  
- POST /tickets/{ticket_id}/close  

---

## 🔄 Ticket Workflow

### 1️⃣ User Creates Ticket

- Ticket stored in PostgreSQL
- AI triage automatically runs

### 2️⃣ AI Classification

The system extracts:
- Category
- Priority
- Sentiment
- Risk
- Confidence
- Summary

### 3️⃣ Decision Engine

If:
- Confidence ≥ 0.70
- Risk = LOW
→ Ticket is auto-resolved

Else:

→ Ticket is assigned to agent queue

### 4️⃣ Agent Handling (If Escalated)

- Agent reviews ticket
- Option to generate AI draft
- Agent edits and sends final response

---

## 💻 Tech Stack

### Backend:

- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT Authentication
- OAuth2

### AI Layer:

- Groq API (LLaMA 3.1)
- LangChain
- SentenceTransformers
- FAISS (Vector Search)
- Structured prompt engineering

### Frontend:

- Streamlit 

---

## 🎥 Demo 

https://github.com/user-attachments/assets/330ea0fd-4944-4c94-95a6-19b27ee8a71c

---

## 📸 Screenshots

<img width="1366" height="631" alt="user-create-ticket" src="https://github.com/user-attachments/assets/b157f53a-9969-4dc1-8e58-181dafe23c6e" />
<img width="1366" height="631" alt="agent-queue" src="https://github.com/user-attachments/assets/15cd4785-81f3-41da-b09c-b5cc6d9bab03" />
<img width="1366" height="627" alt="ai-draft" src="https://github.com/user-attachments/assets/2ba40456-a75d-4350-9831-c2290461b278" />

---

## 📂 Project Structure

```bash
supportiq-ai-support-automation/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── ai/
│       ├── auth/
│       ├── users/
│       ├── tickets/
│       ├── core/
│       └── knowledge_base/
│
├── frontend/
│   └── app.py
│
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── LICENSE

```
---

## ⚙️ Local Setup

1️⃣ Clone Repository
```
git clone https://github.com/sush-sp777/supportiq-ai-support-automation.git
cd supportiq-ai-support-automation
```
2️⃣ Create Environment File

Create a .env file:
```ini
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
```
3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
4️⃣ Run Backend
```bash
uvicorn backend.app.main:app --reload
```
Backend runs at:
```
http://localhost:8000
```
5️⃣ Run Frontend
```bash
streamlit run frontend/app.py
```
---

## 📊 Example Scenarios

### 🟢 Scenario 1: Low-Risk FAQ Question

User:

"How do I reset my password?"

AI:
- Category: Account Support
- Risk: LOW
- Confidence: 0.92

System:
→ Auto resolves using RAG knowledge base.

### 🔴 Scenario 2: High-Risk Complaint

User:

"I was charged twice and this is unacceptable."

AI:

- Risk: HIGH
- Sentiment: Negative
- Confidence: 0.75

System:
→ Routes to human agent.

Agent:
→ Generates AI draft
→ Reviews and sends final reply

---

## 🔐 Security & Reliability

- JWT token expiration
- Password hashing with bcrypt
- Structured LLM output parsing
- Fallback handling for invalid AI responses
- Risk-aware automation limits

---

## 🚀 Why This Project Is Valuable

This project demonstrates:

- Real-world AI system design
- Safe AI automation (not blind chatbot responses)
- LLM structured output handling
- Decision-engine thinking
- Human-in-the-loop workflows
- RAG-based grounding

It reflects production-oriented backend AI engineering.

---
## 🔮 Future Improvements

- Analytics dashboard (auto-resolution rate, sentiment trends, ticket volume insights)
- Email integration for automatic ticket ingestion
- SLA-based dynamic prioritization
- Admin panel for monitoring AI performance

---

## 👨‍💻 Author

**Sushant Patil**

AI Engineer

🔗 https://github.com/sush-sp777

🔗 https://www.linkedin.com/in/sushant-patil-9a05ab2a4/

---
