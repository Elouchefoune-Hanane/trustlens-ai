import os
import uuid
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Query
from pydantic import BaseModel
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

import PyPDF2
import json


# =========================
# ✅ LOAD ENV
# =========================
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")

print("USING INDEX:", AZURE_INDEX_NAME)

# =========================
# ✅ GLOBAL SESSION
# =========================
CURRENT_DOC_ID = None

# =========================
# ✅ CLIENTS
# =========================
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# =========================
# ✅ FASTAPI
# =========================
app = FastAPI()

class QueryRequest(BaseModel):
    question: str

# =========================
# 📄 PDF EXTRACT
# =========================
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# =========================
# ✂️ CHUNKING (OPTIMIZED)
# =========================
def chunk_text(text, chunk_size=1000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# =========================
# 🧠 BATCH EMBEDDINGS (FAST)
# =========================
def get_embeddings_batch(texts):
    response = openai_client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=texts
    )
    return [d.embedding for d in response.data]

# =========================
# 🤖 GENERIC AGENT
# =========================
def call_agent(system_prompt, user_prompt):
    response = openai_client.chat.completions.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

# =========================
# 🤖 AGENTS
# =========================
def risk_agent(user_chunks, trusted_chunks):
    prompt = f"""
Analyze contract risk.

USER CONTRACT:
{user_chunks}

TRUSTED CONTRACTS:
{trusted_chunks}

Return JSON:
{{
  "risk_level": "LOW | MEDIUM | HIGH",
  "explanation": ["..."]
}}
"""
    return call_agent("Risk analysis expert.", prompt)


def clause_agent(user_chunks):
    prompt = f"""
Find missing clauses:

{user_chunks}

Return JSON:
{{
  "missing_clauses": ["..."]
}}
"""
    return call_agent("Legal clause expert.", prompt)


def suspicious_agent(user_chunks):
    prompt = f"""
Find suspicious terms:

{user_chunks}

Return JSON:
{{
  "suspicious_terms": ["..."]
}}
"""
    return call_agent("Legal risk detector.", prompt)


def supervisor_agent(risk, clauses, suspicious):
    prompt = f"""
Combine all analysis into ONE final answer.

RISK:
{risk}

CLAUSES:
{clauses}

SUSPICIOUS:
{suspicious}

Return STRICT JSON:

{{
  "verdict": "SAFE or RISKY",
  "risk_level": "LOW | MEDIUM | HIGH",
  "explanation": ["..."],
  "missing_clauses": ["..."],
  "suspicious_terms": ["..."],
  "confidence": 0.0-1.0
}}
"""
    return call_agent("Senior legal supervisor.", prompt)

# =========================
# 📤 UPLOAD (FAST)
# =========================
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    doc_type: str = Query("user")
):
    try:
        global CURRENT_DOC_ID

        content = await file.read()
        pdf_file = BytesIO(content)

        text = extract_text_from_pdf(pdf_file)

        if not text.strip():
            return {"error": "No text extracted"}

        # 🔥 LIMIT + BIGGER CHUNKS
        chunks = chunk_text(text)[:40]

        # ⚡ BATCH EMBEDDINGS
        embeddings = get_embeddings_batch(chunks)

        documents = []

        for i, chunk in enumerate(chunks):
            documents.append({
                "id": str(uuid.uuid4()),
                "chunk": chunk,
                "doc_id": file.filename,
                "doc_type": doc_type,
                "text_vector": embeddings[i]
            })

        search_client.upload_documents(documents)

        CURRENT_DOC_ID = file.filename

        return {
            "message": "Uploaded successfully",
            "chunks": len(chunks)
        }

    except Exception as e:
        return {"error": str(e)}

# =========================
# ❓ ASK (MULTI-AGENT)
# =========================
@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        global CURRENT_DOC_ID

        if CURRENT_DOC_ID is None:
            return {"error": "Upload document first"}

        question = request.question

        # 🔎 RETRIEVE
        user_results = search_client.search(
            search_text=question,
            filter=f"doc_id eq '{CURRENT_DOC_ID}'",
            top=5
        )
        user_chunks = [r["chunk"] for r in user_results]

        trusted_results = search_client.search(
            search_text=question,
            filter="doc_type eq 'trusted'",
            top=5
        )
        trusted_chunks = [r["chunk"] for r in trusted_results]

        # =========================
        # 🤖 AGENTS
        # =========================
        risk_output = risk_agent(user_chunks, trusted_chunks)
        clause_output = clause_agent(user_chunks)
        suspicious_output = suspicious_agent(user_chunks)

        final_output = supervisor_agent(
            risk_output,
            clause_output,
            suspicious_output
        )

        raw = final_output

        # =========================
        # 🧼 CLEAN JSON
        # =========================
        try:
            cleaned = raw.strip()

            if cleaned.startswith("```"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()

            answer = json.loads(cleaned)

        except Exception:
            answer = {
                "error": "Parse failed",
                "raw_output": raw
            }

        return {
            "answer": answer,
            "doc_id": CURRENT_DOC_ID
        }

    except Exception as e:
        return {"error": str(e)}