from embedder import retrieve
import requests
import os

# Configuration for Ollama (local)
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3"

# Configuration for Groq (cloud - free tier available)
# Get free API key at: https://console.groq.com/keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"  # Free model on Groq

# System prompt for the RAG assistant
SYSTEM_PROMPT = """You are a compliance and security questionnaire assistant. Your task is to answer 
questions using ONLY the provided context from reference documents. 

Guidelines:
1. Be concise and factual
2. If the context does not contain enough information to answer the question, respond with exactly: Not found in references.
3. Do not make up information or infer beyond what's in the context
4. Focus on accuracy and cite relevant details when available
5. Format your answer as a complete, professional response suitable for a security questionnaire"""

# Fallback response when no context is found
NO_CONTEXT_RESPONSE = "Not found in references."


def check_ollama_available() -> bool:
    """Check if Ollama is running."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def generate_with_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Generate text using local Ollama model."""
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 1024,
            }
        },
        timeout=120
    )
    
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    else:
        raise Exception(f"Ollama error: {response.text}")


def check_groq_available() -> bool:
    """Check if Groq API key is configured."""
    return bool(GROQ_API_KEY)


def generate_with_groq(prompt: str, model: str = GROQ_MODEL) -> str:
    """Generate text using Groq cloud API (free tier)."""
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not set in environment")
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 1024
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"Groq error: {response.text}")


def generate_answer(question: str, index, chunks) -> dict:
    """
    Generate an answer for a question using RAG.
    Prefers Groq (cloud) if API key is available, falls back to Ollama (local).
    """
    # Determine which LLM to use: Groq (cloud) > Ollama (local)
    use_groq = check_groq_available()
    use_ollama = check_ollama_available()
    
    if not use_groq and not use_ollama:
        return {
            "answer": "No LLM available. Please configure GROQ_API_KEY or start Ollama.",
            "citation": "N/A",
            "confidence": 0.0,
            "snippet": ""
        }
    
    # Retrieve relevant context
    retrieved = retrieve(question, index, chunks)

    # Handle no results case
    if not retrieved:
        return {
            "answer": NO_CONTEXT_RESPONSE,
            "citation": "N/A",
            "confidence": 0.0,
            "snippet": ""
        }

    # Build context from retrieved chunks
    context = "\n\n".join([f"[{r['source']}]\n{r['text']}" for r in retrieved])
    
    # Calculate average similarity score
    avg_score = sum(r["score"] for r in retrieved) / len(retrieved)

    # Generate answer using available LLM
    prompt = f"""{SYSTEM_PROMPT}

Context:
{context}

Question: {question}

Answer:"""
    
    try:
        if use_groq:
            answer = generate_with_groq(prompt)
        else:
            answer = generate_with_ollama(prompt)
    except Exception as e:
        return {
            "answer": f"Error generating answer: {str(e)}",
            "citation": "N/A",
            "confidence": 0.0,
            "snippet": ""
        }
    
    # Prepare citation and snippet
    all_sources = list(dict.fromkeys(r["source"] for r in retrieved))
    citation = ", ".join(all_sources)
    snippet = retrieved[0]["text"][:300] + "..." if retrieved[0]["text"] else ""

    # Calculate confidence score
    confidence = round(avg_score, 2)

    return {
        "answer": answer,
        "citation": citation,
        "confidence": confidence,
        "snippet": snippet
    }


def generate_batch_answers(questions: list[dict], index, chunks, progress_callback=None) -> list[dict]:
    """
    Generate answers for multiple questions.
    """
    answers = []
    total = len(questions)
    
    for i, q in enumerate(questions):
        result = generate_answer(q["question"], index, chunks)
        
        answers.append({
            "number": q["number"],
            "question": q["question"],
            "answer": result["answer"],
            "citation": result["citation"],
            "confidence": result["confidence"],
            "snippet": result["snippet"]
        })
        
        if progress_callback:
            progress_callback((i + 1) / total)
    
    return answers


def get_coverage_summary(answers: list[dict]) -> dict:
    """
    Get a summary of answer coverage.
    """
    total = len(answers)
    found = sum(1 for a in answers if a["answer"] != NO_CONTEXT_RESPONSE)
    not_found = total - found
    
    answered_confidences = [a["confidence"] for a in answers if a["answer"] != NO_CONTEXT_RESPONSE]
    avg_confidence = sum(answered_confidences) / len(answered_confidences) if answered_confidences else 0
    
    return {
        "total_questions": total,
        "answered": found,
        "not_found": not_found,
        "avg_confidence": round(avg_confidence, 2)
    }
