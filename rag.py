import numpy as np
import json
import subprocess
import wikipedia
from embeddings import get_embedding
from db import fetch_all
from cache import cache

OLLAMA_PATH = r"C:\Users\heman\AppData\Local\Programs\Ollama\ollama.exe"
MODEL_NAME = "mistral"


# -------------------------------
# Similarity
# -------------------------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)


# -------------------------------
# Retrieval
# -------------------------------
def retrieve(query, top_k=3):
    # cache embedding
    query_emb = cache.get(query)

    if not query_emb:
        query_emb = get_embedding(query)
        cache.set(query, query_emb)

    docs = fetch_all()

    scored = []
    for text, emb in docs:
        emb = np.array(json.loads(emb))
        score = cosine_similarity(query_emb, emb)
        scored.append((score, text))

    scored.sort(reverse=True)

    return [text for _, text in scored[:top_k]]


# -------------------------------
# Wikipedia Multi Search
# -------------------------------
def fetch_multiple_wiki(query):
    results = []

    try:
        search_results = wikipedia.search(query, results=3)

        for title in search_results:
            try:
                summary = wikipedia.summary(title, sentences=2)
                url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                results.append((summary, url))
            except:
                continue

    except:
        pass

    return results


# -------------------------------
# LLM
# -------------------------------
def call_llm(prompt):
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", MODEL_NAME],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=60
        )
        return result.stdout.strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"


# -------------------------------
# Generate Answer
# -------------------------------
def generate_answer(query, context):
    prompt = f"""
You are a strict AI assistant.

Your job is to answer ONLY using the provided context.

RULES:
1. Use ONLY the information from the context below
2. If the answer is NOT clearly present, respond EXACTLY with:
   "I don't know based on the provided context"
3. Do NOT guess
4. Do NOT use prior knowledge
5. Keep answer concise (2–3 sentences max)

Context:
{context}

Question:
{query}

Answer:
"""
    return call_llm(prompt)


# -------------------------------
# FINAL PIPELINE (TOP 3 ANSWERS)
# -------------------------------
def rag_pipeline(query):
    responses = []

    # 1. Local RAG answer
    local_chunks = retrieve(query)
    local_context = "\n\n".join(local_chunks)

    local_answer = generate_answer(query, local_context)
    responses.append(("Local Knowledge", local_answer, local_chunks))


    # 2. Wikipedia answers (Top 3)
    wiki_results = fetch_multiple_wiki(query)

    for summary, url in wiki_results:
        answer = generate_answer(query, summary)
        if "i don't know" not in answer.lower():
            responses.append((url, answer, [url]))

     # create snippet view
    snippets = []
    for chunk in local_chunks:
        clean = chunk.strip().replace("\n", " ")
        if len(clean) > 30:
            snippets.append(clean[:120] + "...")

    snippets = list(dict.fromkeys(snippets))[:3]

    print("DEBUG chunks:", local_chunks)

    clean_responses = []

    for source, answer, meta in responses:
        if "i don't know" not in answer.lower():
            clean_responses.append((source, answer, meta))

    # fallback if all removed
    if not clean_responses:
        clean_responses = responses[:1]

    return {
        "answers": clean_responses[:3],
        "snippets": snippets
    }
