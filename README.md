# Smart Service Desk  
## AI-Powered Enterprise Support Management System

Smart Service Desk is a full-stack AI-powered enterprise service desk platform designed to manage employee support requests across **IT**, **HR**, and **Facilities** departments. The system combines traditional ticket management with **Generative AI**, **Agentic AI**, **AI Agent Assist**, **RAG (Retrieval-Augmented Generation)**, **NLP-based ticket classification**, **employee roster security**, **department-based agent access control**, **ticket ownership locking**, and **feedback analytics**.

This project demonstrates how modern AI can improve enterprise support operations by reducing manual workload, improving response speed, increasing support accuracy, and providing better visibility for administrators.

---

## Project Overview

Smart Service Desk is an enterprise-level support management system where employees can raise issues, search FAQs, ask AI-powered knowledge base questions, create tickets, upload attachments, and track issue resolution.

The platform provides separate portals for:

- **Users** – employees who raise issues.
- **Agents** – support staff who resolve tickets.
- **Admins** – management users who control employees, agents, FAQs, knowledge base, analytics, and reports.

The system is designed as a modern full-stack web application using:

- **Django + Django REST Framework** for backend APIs.
- **React + Vite** for frontend UI.
- **JWT Authentication** for secure login.
- **RAG + LLMs** for AI-powered knowledge answers.
- **Generative AI** for summaries, replies, and suggestions.
- **Agentic AI** for AI-assisted ticket handling workflows.
- **ChromaDB + Sentence Transformers** for semantic search.

---

## Problem Statement

In many organizations, internal support requests are handled through emails, calls, chat messages, or basic ticketing tools. These traditional systems create several problems:

- Employees wait longer for simple issue resolutions.
- Agents manually read and classify every ticket.
- Tickets may be assigned to the wrong department.
- Multiple agents may work on the same ticket accidentally.
- Repeated issues require repeated manual replies.
- Knowledge base documents are not used effectively.
- Admins do not get clear analytics about agent performance.
- Former employees may still access support systems if access is not controlled properly.

Smart Service Desk solves these problems by introducing AI automation, secure access control, intelligent ticket routing, RAG-based self-service support, and feedback analytics.

---

## Why This Project

This project was created to demonstrate how AI can improve real enterprise service desk operations.

The main reasons for building this project are:

1. **Reduce manual support workload**  
   AI handles classification, summarization, answer generation, and reply suggestions.

2. **Improve support response time**  
   Users can get instant answers from FAQ and RAG before creating a ticket.

3. **Improve ticket routing accuracy**  
   NLP and LLM-based classification identify whether a ticket belongs to IT, HR, or Facilities.

4. **Avoid duplicate agent handling**  
   Ticket ownership locking ensures only one agent handles a ticket at a time.

5. **Improve enterprise security**  
   Employee ID-based registration ensures only active employees can access the system.

6. **Improve management visibility**  
   Admin dashboards and reports show ticket analytics, AI logs, KB gaps, and agent feedback performance.

---

## Objectives

The main objectives of Smart Service Desk are:

- Build a complete AI-powered enterprise service desk.
- Provide role-based access for users, agents, and admins.
- Implement secure employee roster-based registration.
- Provide FAQ and RAG-based self-service support.
- Automatically classify tickets using AI.
- Generate ticket summaries and suggested solutions.
- Provide AI Assist for support agents.
- Allow attachments such as images, videos, and documents.
- Analyze uploaded images/videos where supported.
- Implement department-based ticket access for agents.
- Lock tickets to the first valid agent who opens them.
- Collect feedback after ticket closure.
- Provide agent-wise feedback analytics for admins.

---

## Core Features

### User Features

- User registration with Employee ID.
- Secure login using JWT authentication.
- FAQ search for common issues.
- RAG-based AI knowledge assistant.
- Continuous chat memory for better follow-up questions.
- Auto ticket draft generation from unresolved AI chat.
- Ticket creation.
- Ticket list and ticket detail view.
- Ticket conversation thread.
- File attachment upload.
- Feedback submission after ticket closure.

### Agent Features

- Agent login.
- Agent dashboard.
- Department-based queue.
- Ticket auto-claim when opened.
- Ticket ownership lock.
- User-agent ticket chat.
- View image/video/document attachments.
- AI Assist Panel.
- AI-generated ticket summary.
- Priority reason explanation.
- Sentiment explanation.
- Suggested reply generation.
- Suggested troubleshooting steps.
- Ticket escalation.
- Ticket closure.
- Agent feedback summary.

### Admin Features

- Admin dashboard.
- User management.
- Agent management.
- Employee roster upload.
- Active/inactive employee control.
- FAQ management.
- Knowledge base document upload.
- AI classification log view.
- KB gap detection.
- Ticket analytics.
- Agent-wise feedback analytics.
- Report summary export.

---

## AI Concepts Used

This project uses multiple modern AI concepts:

- **Artificial Intelligence**
- **Generative AI**
- **AI Agent**
- **Agentic AI**
- **RAG**
- **NLP**
- **LLMs**
- **Prompt Engineering**
- **Embeddings**
- **Semantic Search**
- **Vector Database**
- **Sentiment Analysis**
- **Text Classification**
- **Summarization**
- **AI-assisted decision support**

---

## Generative AI Implementation

Generative AI is used to create useful human-like text outputs.

In this project, Generative AI is used for:

- RAG-based answer generation.
- Ticket summary generation.
- Suggested solution generation.
- Agent reply generation.
- Priority explanation.
- Sentiment explanation.
- Escalation suggestion.

### How Generative AI Works Here

The system sends structured prompts to an LLM. The prompt contains:

- User query or ticket description.
- Retrieved knowledge base context.
- Required output format.
- Role instructions.
- Safety and formatting rules.

The LLM then generates a professional response.

### Example Use Cases

| Use Case | Generated Output |
|---|---|
| User asks a support question | AI generates step-by-step answer |
| Ticket is created | AI generates summary and solution |
| Agent opens ticket | AI generates suggested reply |
| Ticket is urgent | AI suggests escalation |
| Admin reviews reports | AI helps identify support patterns |

---

## AI Agent Concept

An AI Agent is an intelligent assistant that can understand context, use available information, and support decision-making.

In this project, the AI Agent concept is mainly used in the **Agent Assist Panel**.

The AI Agent helps the support agent by:

- Reading ticket subject and description.
- Understanding user sentiment.
- Explaining priority.
- Summarizing the issue.
- Searching related knowledge.
- Suggesting a professional reply.
- Suggesting troubleshooting steps.
- Recommending escalation if needed.

The AI Agent does not replace the human support agent. Instead, it acts as a productivity assistant that helps the agent respond faster and more accurately.

---

## Agentic AI Concept

Agentic AI means AI that supports a workflow through multiple steps instead of only answering one question.

This project applies Agentic AI in the ticket handling process.

### Agentic AI Workflow

```text
Ticket Created
↓
AI Classifies Department, Priority, and Sentiment
↓
Agent Opens Ticket
↓
AI Summarizes Issue
↓
AI Finds Related Knowledge
↓
AI Suggests Reply
↓
Agent Reviews and Sends Response
↓
Ticket is Closed or Escalated
```

### Why This Is Agentic AI

The AI performs multiple support tasks:

- Understands the problem.
- Retrieves useful information.
- Generates summaries.
- Recommends next action.
- Supports human decision-making.

This makes the system more than a chatbot. It becomes an AI-assisted workflow system.

---

## RAG Implementation

RAG stands for **Retrieval-Augmented Generation**.

RAG is used to answer user questions based on uploaded knowledge base documents.

A normal LLM may generate generic answers, but RAG improves accuracy by retrieving relevant company knowledge before generating the answer.

### RAG Pipeline

```text
Admin Uploads Knowledge Document
↓
Backend Extracts Text
↓
Text Cleaning
↓
Smart Chunking
↓
Embedding Generation
↓
Vector Storage in ChromaDB
↓
User Asks Question
↓
Question Embedding Generated
↓
Semantic Search Finds Relevant Chunks
↓
LLM Generates Final Answer
```

### RAG Components

| Component | Purpose |
|---|---|
| Text Extraction | Extract text from PDF, DOCX, or TXT |
| Text Cleaning | Remove unwanted symbols, markdown, duplicate text |
| Chunking | Split large text into smaller meaningful sections |
| Embeddings | Convert text into numerical vectors |
| Vector Database | Store and search embeddings |
| Semantic Search | Retrieve chunks based on meaning |
| LLM | Generate final answer using retrieved context |

### Why RAG Is Used

RAG is used because enterprise support answers must be based on company knowledge, policies, and uploaded documents.

Benefits of RAG:

- Reduces hallucination.
- Improves answer accuracy.
- Supports company-specific knowledge.
- Allows knowledge base updates without retraining the LLM.
- Provides better self-service support.

---

## NLP Implementation

NLP stands for **Natural Language Processing**.

NLP is used to understand user-written text such as ticket descriptions, support questions, and feedback comments.

### NLP Tasks Used

| NLP Task | Usage |
|---|---|
| Text Classification | Classify ticket as IT, HR, or Facilities |
| Sentiment Analysis | Detect user emotion |
| Summarization | Generate short issue summary |
| Semantic Search | Match user question with KB chunks |
| Question Answering | Generate support answers |
| Prompt Processing | Format input for LLM |

### Example

User writes:

```text
My laptop screen is flickering and showing green lines before my client meeting.
```

The AI can classify:

```text
Request Type: IT
Priority: HIGH
Sentiment: URGENT
Summary: User is facing laptop display flickering issue before a client meeting.
```

---

## Ticket Workflow

```text
User asks FAQ/RAG question
↓
AI gives answer from knowledge base
↓
If unresolved, user creates ticket
↓
AI classifies ticket
↓
Ticket goes to correct department queue
↓
First valid agent opens ticket
↓
Ticket is locked to that agent
↓
Agent uses AI Assist
↓
Agent replies, escalates, or closes ticket
↓
User submits feedback
↓
Admin reviews analytics
```

---

## Role-Based Modules

### User Module

Users can ask questions, create tickets, upload attachments, chat with agents, and submit feedback.

### Agent Module

Agents can handle tickets only from their own department. The first agent who opens an unassigned ticket becomes the assigned owner of that ticket.

### Admin Module

Admins can manage the entire platform, including users, agents, employee rosters, FAQs, KB documents, reports, and analytics.

---

## Security Features

### JWT Authentication

The system uses JWT authentication to protect APIs.

### Role-Based Access Control

Three roles are supported:

- USER
- AGENT
- ADMIN

Each role has different permissions.

### Employee Roster Security

Only employees uploaded by the admin can register and login.

Rules:

- Employee ID is required for registration.
- Employee ID must exist in the active roster.
- One employee ID can register only once.
- If employee ID is removed or inactive, login is blocked.

### Department-Based Agent Access

Agents can access only tickets matching their department.

Example:

| Agent Department | Allowed Tickets |
|---|---|
| IT | IT tickets only |
| HR | HR tickets only |
| Facilities | Facilities tickets only |

### Ticket Ownership Lock

When an agent opens an unassigned ticket:

- The ticket is automatically assigned to that agent.
- Other agents cannot work on the same ticket.
- Only the assigned agent can reply, close, or escalate it.
- Admin can still view all tickets.

---

## Technology Stack

### Backend

- Python
- Django
- Django REST Framework
- Simple JWT
- SQLite for development
- PostgreSQL recommended for production
- ChromaDB
- Sentence Transformers
- Groq / OpenRouter LLM APIs
- PyTesseract OCR
- OpenCV video processing

### Frontend

- React
- Vite
- Axios
- React Router
- Normal CSS
- Component-based architecture

### AI / ML

- RAG
- Generative AI
- Agentic AI
- NLP
- LLMs
- Embeddings
- Semantic search
- Vector database
- Prompt engineering

---

## System Architecture

```text
React Frontend
│
│ Axios API Calls
↓
Django REST Framework Backend
│
├── Authentication & RBAC
├── Ticket Management
├── Employee Roster Security
├── FAQ Management
├── Knowledge Base Management
├── AI Classification
├── RAG Service
├── Agent Assist Service
└── Admin Analytics
│
├── SQLite / PostgreSQL Database
├── ChromaDB Vector Store
└── LLM Provider APIs
```

---

## Database Design

Main database entities:

- User
- EmployeeRecord
- EmployeeUploadBatch
- Ticket
- TicketMessage
- TicketAttachment
- TicketFeedback
- TicketActivityLog
- TicketAIClassification
- TicketAgentSuggestion
- FAQ
- KBDocument
- KBChunk

### Important Relationships

- One user can create many tickets.
- One ticket can have many messages.
- One ticket can have many attachments.
- One ticket can have one feedback.
- One ticket can be assigned to one agent.
- One agent can receive many feedback records.
- One KB document can have many chunks.
- One employee record can be linked to one registered user.

---

## API Modules

### Authentication APIs

- Register
- Login
- Token refresh
- Profile
- Logout

### Ticket APIs

- Create ticket
- My tickets
- Ticket detail
- Add message
- Upload attachment
- Submit feedback

### Agent APIs

- Agent dashboard
- Agent queue
- Ticket detail
- Reply ticket
- Close ticket
- Escalate ticket
- AI suggestion
- Feedback summary

### Admin APIs

- User management
- Agent management
- Employee roster upload
- Ticket analytics
- AI logs
- KB gap detection
- Agent feedback analytics
- Report summary

### Knowledge Base APIs

- Upload document
- Process document
- Store chunks
- RAG question answering

---

## Output Screenshots

Add your project screenshots inside:

```text
frontend/public/screenshots/
```

Recommended screenshot names:

```text
01-home-page.png
02-rag-chat.png
03-user-ticket-page.png
04-agent-dashboard.png
05-agent-queue.png
06-agent-ticket-chat.png
07-ai-assist-panel.png
08-admin-dashboard.png
09-employee-roster-upload.png
10-kb-management.png
11-admin-reports.png
12-feedback-analytics.png
```

### Home Page

![Home Page](frontend/public/screenshots/01-home-page.png)

### RAG Chat

![RAG Chat](frontend/public/screenshots/02-rag-chat.png)

### User Ticket Page

![User Ticket Page](frontend/public/screenshots/03-user-ticket-page.png)

### Agent Dashboard

![Agent Dashboard](frontend/public/screenshots/04-agent-dashboard.png)

### Agent Queue

![Agent Queue](frontend/public/screenshots/05-agent-queue.png)

### Agent Ticket Chat

![Agent Ticket Chat](frontend/public/screenshots/06-agent-ticket-chat.png)

### AI Assist Panel

![AI Assist Panel](frontend/public/screenshots/07-ai-assist-panel.png)

### Admin Dashboard

![Admin Dashboard](frontend/public/screenshots/08-admin-dashboard.png)

### Employee Roster Upload

![Employee Roster Upload](frontend/public/screenshots/09-employee-roster-upload.png)

### Knowledge Base Management

![Knowledge Base Management](frontend/public/screenshots/10-kb-management.png)

### Admin Reports

![Admin Reports](frontend/public/screenshots/11-admin-reports.png)

### Feedback Analytics

![Feedback Analytics](frontend/public/screenshots/12-feedback-analytics.png)

---

## Project Structure

```text
smart-service-desk/
│
├── backend/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── tickets/
│   │   ├── faqs/
│   │   ├── knowledge_base/
│   │   ├── ai_engine/
│   │   ├── dashboard/
│   │   └── notifications/
│   ├── config/
│   ├── data/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   └── screenshots/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
```

Backend URL:

```text
http://127.0.0.1:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Environment Variables

Create a `.env` file inside the backend folder.

```env
SECRET_KEY=django-insecure-change-this-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

LLM_PROVIDER=auto

GROQ_API_KEY=
GROQ_PRIMARY_MODEL=llama-3.3-70b-versatile
GROQ_FALLBACK_MODEL=llama-3.1-8b-instant

OPENROUTER_API_KEY=
OPENROUTER_MODEL=

AI_TIMEOUT_SECONDS=30

EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHROMA_DB_PATH=./data/vector_store/chroma_db
CHROMA_COLLECTION_NAME=smartdesk_kb_chunks
RAG_TOP_K=5
RAG_MIN_SCORE=0.25

KB_CLEAN_TEXT_ENABLED=True
KB_CHUNK_MAX_WORDS=220
KB_CHUNK_OVERLAP_WORDS=35
KB_SPLIT_BY_ISSUE=True

IMAGE_ANALYSIS_ENABLED=True
VIDEO_ANALYSIS_ENABLED=True
VIDEO_MAX_FRAMES=5
```

Do not commit `.env` to GitHub.

---

## Employee Roster CSV Format

```csv
employee_id,full_name,email,department,role_type
EMP001,Praveen Kumar,praveen.user@smartdesk.com,IT,USER
EMP002,Divya Lakshmi,divya.user@smartdesk.com,HR,USER
EMP003,Naveen Raj,naveen.user@smartdesk.com,FACILITIES,USER
EMP004,Arun Kumar,arun.agent@smartdesk.com,IT,AGENT
EMP005,Meera Nair,meera.agent@smartdesk.com,HR,AGENT
```

---

## Testing Flow

### User Flow

```text
Register with employee ID
↓
Login
↓
Ask FAQ/RAG question
↓
Create ticket if issue is not solved
↓
Track ticket
↓
Chat with agent
↓
Submit feedback after closure
```

### Agent Flow

```text
Login as agent
↓
Open department queue
↓
Open ticket
↓
Ticket gets assigned automatically
↓
Use AI Assist
↓
Reply / Escalate / Close ticket
↓
View feedback summary
```

### Admin Flow

```text
Login as admin
↓
Upload employee roster
↓
Manage users and agents
↓
Upload FAQ and KB documents
↓
Monitor ticket analytics
↓
Review AI logs and KB gaps
↓
View agent feedback analytics
↓
Export report summary
```

---

## Future Enhancements

- PostgreSQL production deployment.
- Docker support.
- Celery and Redis background jobs.
- Email notification system.
- WhatsApp notification system.
- SLA tracking and auto-escalation.
- SSO or LDAP login.
- Multi-company tenant support.
- Advanced BI dashboard.
- Mobile application.
- Voice-based ticket creation.
- AI-powered root cause analysis.

---

## Author

**Thangamanikandan I**

Python Full Stack Developer  
Django REST Framework | React | AI/ML | RAG | Generative AI | Agentic AI

- GitHub: `github.com/manikandan-mk007`
- LinkedIn: `linkedin.com/in/thangamanikandan-i-560b20396/`

---

## License

This project is created for academic, learning, portfolio, and demonstration purposes.
