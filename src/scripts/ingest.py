import glob
import os

import psycopg2
import requests
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

DOC_DIR = "tests/docs"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

DB_DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:6543/sre_agent?sslmode=disable"
)

CHUNK_SIZE = 500  # Number of characters per chunk
CHUNK_OVERLAP = 50  # Number of overlapping characters between chunks

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

def chunk_text(text:str, size:int = CHUNK_SIZE, overlap:int = CHUNK_OVERLAP) -> list[str]:
    """Split text into chunks of specified size with overlap."""
    chunks = []
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on,
                                                   strip_headers=False)
  
    structural_chunks = markdown_splitter.split_text(text)
    
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP
    )
    
    final_chunks = recursive_splitter.split_documents(structural_chunks)
    return [c for c in final_chunks if c]  # Remove empty chunks


def embed(text:str) -> list[float]:
    """Get embeddings for the given text using Ollama API."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": EMBED_MODEL, "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]

def ingest_file(cur, file_path:str) -> None:
    """Ingest a single file into the database."""
    source = os.path.basename(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    cur.execute(
        "INSERT INTO documents (source, title) VALUES (%s, %s) RETURNING id",
        (source, source.replace(".md", "").replace("_"," ").title()),
    )
    doc_id = cur.fetchone()[0]

    chunks = chunk_text(text)
    
    print(f" {source}: {len(chunks)} chunks")
    for chunk in chunks:
        header_context = " > ".join(chunk.metadata.values())
        rich_text = f"Section: {header_context}\n\n{chunk.page_content}" if header_context else chunk.page_content
        
        # Embed the rich text so the vector understands the context
        vector = embed(rich_text)
        cur.execute(
            "INSERT INTO chunks (document_id, chunk_text, embedding) VALUES (%s, %s, %s)",
            (doc_id, chunk.page_content, vector)
        )
        
def main():
    """Main function to ingest all documents in the DOC_DIR."""
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False
    cur = conn.cursor()
    
    files = glob.glob(os.path.join(DOC_DIR, "*.md"))
    print(f"Found {len(files)} files in {DOC_DIR}/")
    for file_path in files:
        ingest_file(cur, file_path)
        
    conn.commit()
    cur.close()
    conn.close()
    print("Done.")
    
if __name__ == "__main__":
    main()