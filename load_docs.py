import os
from embeddings import get_embedding
from db import insert_doc

CHUNK_SIZE = 300

def chunk_text(text):
    paragraphs = text.split("\n\n")
    chunks = []

    for p in paragraphs:
        p = p.strip()

        # Skip very small chunks
        if len(p) < 40:
            continue

        # Limit chunk size (important for embeddings)
        if len(p) > 500:
            words = p.split()
            for i in range(0, len(words), 80):
                sub_chunk = " ".join(words[i:i+80])
                if len(sub_chunk) > 40:
                    chunks.append(sub_chunk)
        else:
            chunks.append(p)

    return chunks


def load_documents():
    for file in os.listdir("docs"):
        path = os.path.join("docs", file)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        for chunk in chunks:
            embedding = get_embedding(chunk)
            insert_doc(chunk, embedding)

    print("✅ Documents loaded into DB")


if __name__ == "__main__":
    load_documents()