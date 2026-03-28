# 🚀 TrustLens AI

**AI-powered contract analysis platform that detects risks, missing clauses, and suspicious terms using Retrieval-Augmented Generation (RAG) and trusted document comparison.**

---

## 🧠 What it does

TrustLens AI helps users understand contracts instantly by:

* 📄 Uploading contracts (PDF)
* ❓ Asking natural language questions
* ⚠️ Detecting **risk levels** (LOW / MEDIUM / HIGH)
* 📉 Identifying **missing clauses**
* 🔍 Highlighting **suspicious or vague terms**
* 📊 Providing a **confidence score**

---

## 🔥 What makes it unique

Unlike traditional document analysis tools, **TrustLens AI compares user contracts against trusted contract templates**.

* 🧠 Uses **semantic similarity (vector search)**
* 📊 Detects **deviation from safe legal patterns**
* ⚠️ Flags contracts that differ significantly as higher risk

👉 This enables deeper risk detection beyond keyword matching.

---

## ⚙️ Tech Stack

### Backend

* **FastAPI** — API framework
* **Azure OpenAI** — GPT-4o-mini for reasoning
* **Azure AI Search** — vector database (RAG)
* **PyPDF** — PDF parsing
* **tiktoken** — chunking support

### Frontend (basic)

* HTML / CSS / JavaScript

---

## 🏗️ Architecture

User → Upload PDF → Backend
↓
Text Extraction
↓
Chunking + Embeddings
↓
Azure AI Search (Vector DB)
↓
Retrieve:

* User contract chunks
* Trusted contract chunks
  ↓
  Multi-Agent AI Analysis:
* Risk Agent
* Clause Agent
* Suspicious Terms Agent
  ↓
  Supervisor AI (final output)
  ↓
  Structured JSON Response

---

## 🤖 Multi-Agent AI System

TrustLens AI uses a modular AI architecture:

* ⚠️ **Risk Agent** → evaluates contract safety
* 📉 **Clause Agent** → detects missing clauses
* 🔍 **Suspicious Agent** → finds vague or risky terms
* 🧠 **Supervisor Agent** → combines outputs into final decision

---

## 📡 API Endpoints

### 📤 Upload Contract

`POST /upload?doc_type=user`

* Upload a PDF contract
* Splits into chunks
* Stores embeddings in Azure AI Search

---

### ❓ Ask Question

`POST /ask`

```json
{
  "question": "Is this contract risky?"
}
```

### 📥 Response

```json
{
  "answer": {
    "verdict": "RISKY",
    "risk_level": "HIGH",
    "explanation": ["..."],
    "missing_clauses": ["..."],
    "suspicious_terms": ["..."],
    "confidence": 0.85
  }
}
```

---

## 🧪 Demo Flow

1. Upload a contract
2. Ask: *“Is this contract risky?”*
3. Receive structured AI analysis

---

## ☁️ Azure Integration

* **Azure OpenAI**

  * GPT-4o-mini → reasoning
  * Embeddings → semantic understanding

* **Azure AI Search**

  * Vector storage
  * Semantic retrieval
  * Trusted vs user document comparison

---

## 🛡️ Responsible AI

TrustLens AI follows key Responsible AI principles:

* 🔍 **Transparency** — provides explanations for decisions
* 📊 **Reliability** — includes confidence scores
* 👤 **Human Oversight** — supports informed decision-making

---

## 🚀 Setup (Local)

### 1. Clone repo

```bash
git clone https://github.com/YOUR_USERNAME/trustlens-ai.git
cd trustlens-ai/backend
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

```
AZURE_OPENAI_API=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=embedding-model

### Contributors
Elizabeth Akindele
Gloria Villa
Hanane Elouchefoune
Sadia Mehmood
Aishat Osshileye


AZURE_SEARCH_ENDPOINT=your_search_endpoint
AZURE_SEARCH_KEY=your_search_key
AZURE_SEARCH_INDEX=rag-final
```

### 5. Run backend

```bash
uvicorn main:app --reload --port 8001
```

👉 Open: http://127.0.0.1:8001/docs

---

## ⚠️ Notes

* Azure AI Search free tier has storage limits
* If quota exceeded → clear index or create new one

---

## 🔮 Future Improvements

* Multi-document comparison
* Legal recommendations
* Risk scoring dashboard
* Full SaaS platform

---

## 🏁 Conclusion

**TrustLens AI makes contracts transparent, understandable, and safer — using AI to empower better decisions.**
