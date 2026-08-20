# FraudSense – Real-Time Digital Lending Fraud Detection

An AI-powered real-time fraud detection platform designed for digital lending transactions. The system combines machine-learning-based fraud prediction, PostgreSQL, pgvector semantic search, embeddings, and a hosted LLM to provide fraud decisions and explainable AI investigation summaries.

## Features

- Real-time fraud risk assessment
- Fraud probability prediction
- LOW, MEDIUM, and HIGH risk classification
- APPROVE, REVIEW, and BLOCK decisions
- Explainable fraud-risk reasons
- PostgreSQL structured data storage
- PostgreSQL with pgvector for semantic search
- Embedding-based fraud knowledge retrieval
- Gemini hosted LLM for AI investigation summaries
- Prompt templates and AI guardrails
- JWT authentication and authorization
- Input validation
- Secure environment-based API credentials
- No hardcoded secrets
- Monitoring and request logging
- React-based dashboard
- Automated basic test coverage
- Simulated incoming transaction support

## Project Structure
```text
fraud-detection-project-synchrony/
│
├── backend/
│   ├── auth.py
│   ├── database.py
│   ├── decision_engine.py
│   ├── embedding_service.py
│   ├── explanation_engine.py
│   ├── guardrails.py
│   ├── investigation_service.py
│   ├── llm_service.py
│   ├── main.py
│   ├── model_service.py
│   ├── models.py
│   ├── prompt_templates.py
│   ├── schemas.py
│   ├── semantic_search.py
│   └── simulator.py
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── App.css
│
├── ml/
│   └── machine-learning files
│
├── database/
│   └── database scripts
│
├── tests/
│   ├── conftest.py
│   ├── test_decision_engine.py
│   ├── test_explanation_engine.py
│   ├── test_guardrails.py
│   └── test_semantic_search.py
│
├── docs/
│
├── .gitignore
├── .gitattributes
└── README.md
```

## Block Diagram
```text
                    +----------------------+
                    |    React Frontend    |
                    |      FraudSense      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |    FastAPI Backend   |
                    |       REST API       |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
      +---------------+ +---------------+ +---------------+
      | ML Prediction | |  PostgreSQL   | | Authentication|
      | + Decision    | |  + pgvector   | |    + JWT      |
      +-------+-------+ +-------+-------+ +---------------+
              |                 |
              |                 v
              |         +---------------+
              |         | Semantic      |
              |         | Search        |
              |         +-------+-------+
              |                 |
              +--------+--------+
                       |
                       v
               +---------------+
               | Prompt        |
               | Templates     |
               +-------+-------+
                       |
                       v
               +---------------+
               | Gemini LLM    |
               +-------+-------+
                       |
                       v
               +---------------+
               | AI Guardrails |
               +-------+-------+
                       |
                       v
               +---------------+
               | Investigation |
               | Summary       |
               +---------------+
```

## Modules

### ML Prediction

Predicts the fraud probability for a digital lending transaction using the existing fraud model.

### Decision Engine

Maps the model probability to a risk band and business decision.

```text
LOW     → APPROVE
MEDIUM  → REVIEW
HIGH    → BLOCK
```

### Explanation Engine

Generates human-readable reasons for why a transaction was flagged.

### PostgreSQL Database

Stores structured fraud assessment information including transaction signals, fraud probability, risk band, decision, reasons, and timestamps.

### pgvector Semantic Search

Stores 384-dimensional embeddings for fraud knowledge and retrieves the most relevant knowledge for an investigation.

### Embedding Service

Generates embeddings for fraud-related text used by the semantic search layer.

### Gemini LLM

Generates a concise investigation summary using the fraud assessment, model reasons, and retrieved fraud knowledge.

### Prompt Templates

Builds a controlled investigation prompt containing the model assessment, transaction signals, model reasons, and relevant knowledge.

### AI Guardrails

Validates the LLM response for required sections, response length, and consistency with the existing fraud decision.

### Authentication

Uses JWT bearer authentication to protect application APIs.

## Fraud Assessment Flow

```text
Transaction Event
       |
       v
Input Validation
       |
       v
ML Fraud Prediction
       |
       v
Risk Assessment
       |
       v
Explainable Reasons
       |
       v
PostgreSQL Storage
       |
       v
Optional AI Investigation
       |
       v
pgvector Semantic Search
       |
       v
Prompt Template
       |
       v
Gemini LLM
       |
       v
AI Guardrails
       |
       v
Final Investigation Summary
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/login` | User authentication |
| POST | `/api/fraud/check` | Real-time fraud assessment |
| POST | `/api/fraud/simulate` | Simulated incoming transaction |
| POST | `/api/fraud/investigate` | AI fraud investigation |
| GET | `/api/knowledge/search` | Semantic fraud knowledge search |
| GET | `/api/assessments` | Recent assessments |
| GET | `/api/assessments/{assessment_id}` | Single assessment |
| GET | `/api/dashboard/summary` | Dashboard statistics |
| GET | `/health` | Backend health check |

## Explainability

The fraud assessment provides model-derived reasons such as:

- High recent activity detected
- Very short time since the previous event
- New device detected
- Unusual location
- Unusual IP / network
- Unusual transaction time
- Transaction amount is relatively high

The AI investigation uses these signals together with relevant fraud knowledge retrieved through semantic search.

## AI Investigation

The AI investigation layer is designed to explain the existing model decision rather than replace it.

```text
ML Model
   |
   +--> Fraud Probability
   +--> Risk Band
   +--> Decision
   +--> Reasons
            |
            v
      Semantic Search
            |
            v
      Prompt Template
            |
            v
         Gemini
            |
            v
       Guardrails
            |
            v
   Investigation Summary
```

The LLM is explicitly instructed not to change the model decision, invent transaction facts, or claim certainty about fraud.

## Security

The application uses environment variables for secrets and credentials.

The repository excludes sensitive and generated files using `.gitignore`.

The following are not committed to GitHub:

- API keys
- JWT secrets
- Database passwords
- `.env`
- Python virtual environments
- Node.js dependency folders

Authentication uses JWT bearer tokens.

## Monitoring and Logging

The backend logs:

- API request paths
- HTTP status codes
- Request duration
- Fraud assessment completion
- AI investigation completion

Sensitive values such as passwords, JWT tokens, API keys, prompts, and full AI responses are not logged.

## Verification

The project includes automated tests using pytest.

### Test Coverage

- Risk decision logic
- Explainability logic
- AI guardrails
- pgvector semantic search

### Test Result

```text
13 passed
```

Run all tests using:

```powershell
python -m pytest -v
```

## Tools Used

- React JS
- Vite
- Python
- FastAPI
- PostgreSQL
- pgvector
- Gemini
- pytest
- Git
- GitHub
- GitHub Desktop
- Visual Studio Code

## Verification Method

The system was verified through:

- Real-time fraud assessment from the React dashboard
- Simulated incoming transaction testing
- PostgreSQL data storage verification
- pgvector semantic search verification
- Embedding generation verification
- Gemini AI investigation verification
- Guardrail validation
- JWT authentication verification
- Backend request monitoring and logging
- Automated pytest execution