import sqlite3
import json

conn = sqlite3.connect("rag.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, embedding TEXT)")
conn.commit()

def insert_doc(text, embedding):
    cursor.execute("INSERT INTO documents (text, embedding) VALUES (?, ?)", (text, json.dumps(embedding)))
    conn.commit()

def fetch_all():
    cursor.execute("SELECT text, embedding FROM documents")
    return cursor.fetchall()
