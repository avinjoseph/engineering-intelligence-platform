# Docker commands
-- docker compose -f docker.compose.yml up -d    # To up the pgvector container
-- python src/database/__init_db.py         # To initialize the db and create tables
-- docker exec -it engineering-intelligence-platform-postgres-1 psql -U postgres -d sre_agent -c "\dt"     
-- python src/scripts/ingest.py     # Get the test files embeddings into the database
-- python src/scripts/search.py "how do I request time off"     # Search functions