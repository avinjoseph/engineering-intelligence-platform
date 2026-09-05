import os
import sys

import psycopg2
import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

DB_DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:6543/sre_agent?sslmode=disable",
)

TOP_K = 5  # Number of top results to return
VECTOR_WEIGHT = 0.6
KEYWORD_WEIGHT = 0.4
MIN_VECTOR_SCORE = 0.55  # Minimum vector similarity score to consider

def embed(text: str) -> list[float]:
    """Get embeddings for the given text using Ollama API."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": EMBED_MODEL, "prompt": text},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Warning: Failed to fetch embeddings from Ollama ({e}). Returning empty search vector.")
        return []

def search(query:str, top_k:int = TOP_K) -> list[dict]:
    """Search for the most relevant chunks based on the query."""
    query_vector = embed(query)
    if not query_vector:
        return []
    
    try:
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT c.chunk_text, 
                   d.source, 
                   (1 - (c.embedding <=> %s:: vector)) AS vector_score,
                   ts_rank(c.tsv, plainto_tsquery('english', %s)) AS keyword_score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY
                (%s * (1 - (c.embedding <=> %s:: vector)) 
                + %s * ts_rank(c.tsv, plainto_tsquery('english', %s))) DESC LIMIT %s
            """,
            (
                query_vector, query,
                VECTOR_WEIGHT, query_vector,
                KEYWORD_WEIGHT, query,
                top_k,
            ),
        )
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        results = [
            {
                "text": row[0],
                "source": row[1],
                "vector_score": round(row[2], 4),
                "keyword_score": round(row[3], 4),
            }
            for row in rows
        ]   
        
        return [r for r in results if r["vector_score"] >= MIN_VECTOR_SCORE]
    except Exception as e:
        print(f"Warning: PostgreSQL database search failed ({e}). Returning empty doc list.")
        return []
    
    
if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "checkout latency"
    results = search(query)
    print(f"\nQuery: {query!r}\n")
    if not results:
        print(f"No results above relevance threshold of {MIN_VECTOR_SCORE}.\n")
    for i, r in enumerate(results, 1):
        print(f"[{i}] source={r['source']}  vector={r['vector_score']}  keyword={r['keyword_score']}")
        print(f"    {r['text'][:150]}...\n")