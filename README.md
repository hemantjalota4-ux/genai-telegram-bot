
# GenAI Telegram Bot (RAG + Vision)

A lightweight **Generative AI Telegram Bot** that supports:

- Retrieval-Augmented Generation (RAG)
- Image Captioning (Vision AI)
- Conversational Memory
- Query Caching
- External Knowledge (Wikipedia augmentation)

---

## Features

### 1. RAG-based Question Answering
- Retrieves relevant document chunks from a local knowledge base
- Uses embeddings (`all-MiniLM-L6-v2`)
- Generates answers using **LLM (Ollama - Mistral)**

 Uses **strict prompt grounding** (no hallucination)  
 Answers ONLY from retrieved context  
 Filters out irrelevant or low-quality responses  
 Returns clean, structured answers with sources  

---

### 2. Image Captioning
- Accepts user-uploaded images
- Uses **BLIP model (Salesforce/blip-image-captioning-base)**
- Returns:
  - Caption
  - Top 3 tags

---

### 3. Memory (Last 3 Interactions)
- Maintains user-specific history
- Enables `/summarize` command

---

### 4. Caching
- Avoids recomputing embeddings for repeated queries

---

### 5. Wikipedia Augmentation
- Fetches top 3 relevant Wikipedia summaries
- Enhances answer quality beyond local docs

---

## Prompt Design

The system uses a **strict grounding prompt** to ensure reliable answers:

- Uses ONLY retrieved context  
- Prevents hallucination  
- Returns "I don't know" if answer is not found  
- Keeps answers concise (2–3 sentences)  

---

## Project Structure

```
.
├── app.py
├── rag.py
├── vision.py
├── embeddings.py
├── db.py
├── cache.py
├── memory.py
├── load_docs.py
├── docs/
├── rag.db
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Install dependencies
pip install -r requirements.txt

### 2. Install Ollama
Download from: https://ollama.com

Then run:
ollama pull mistral

### 3. Load documents
python load_docs.py

### 4. Add Telegram Bot Token
Replace TOKEN in app.py

### 5. Run
python app.py

---

## Commands

- /ask <query>
- /image
- /help

---

## System Flow

1. User sends query/image via Telegram  
2. Bot routes request:
   - Text → RAG pipeline  
   - Image → Vision model  
3. RAG retrieves relevant chunks from DB  
4. LLM generates grounded answer (strict prompt)  
5. Responses are filtered to remove low-quality outputs  
6. Final answers + sources + snippets returned  

---

## Models Used

- Embeddings: all-MiniLM-L6-v2  
- LLM: Mistral (Ollama)  
- Vision: BLIP (Salesforce)  

---

## Key Design Choices

- SQLite used for lightweight vector storage  
- Local LLM via Ollama for cost efficiency  
- Modular architecture for scalability  
- Hybrid RAG (Local + Wikipedia)  
- Strict prompt design to prevent hallucination  
- Output filtering for better answer quality  
- Clean response formatting for improved UX  

---

## Demo

![RAG Demo](image.png)
![Image Demo](image-2.png)
![Help Demo](image-1.png)

### Example Output

 Top Answers  

1. Local Knowledge  
RAG stands for Retrieval-Augmented Generation...  

 Sources  
1. Local Knowledge Base  

 Context Used  
- RAG stands for Retrieval-Augmented Generation...  

---

## Author

Hemant Jalota
