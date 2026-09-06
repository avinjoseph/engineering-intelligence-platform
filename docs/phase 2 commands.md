# Phase 2 Commands Guide

## 1. Infrastructure Setup (Docker Compose)
-- docker compose -f docker.compose.yml up -d                # Spin up Postgres (pgvector), Prometheus (9090), and Node Exporter (9100)
-- docker compose -f docker.compose.yml ps                   # Check status of running infrastructure containers

## 2. Database & RAG Ingestion
-- python src/database/__init_db.py                          # Initialize PostgreSQL tables (documents, chunks, tsv, pgvector)
-- python src/scripts/ingest.py                              # Ingest test documentation into vector & full-text search DB

## 3. Prometheus Verification & Metrics Direct Query
-- python -c "import requests; print(requests.get('http://localhost:9090/api/v1/query', params={'query': 'up'}).json())"   # Verify Prometheus instant query API
-- python -c "from src.core.prometheus import PrometheusClient; print(PrometheusClient().fetch_service_health('checkout'))"  # Test Prometheus health fetcher directly

## 4. Run Unit & Integration Tests
-- python tests/test_prometheus_tool.py                      # Run automated unit tests for Prometheus tool integration & fallback logic

## 5. Execute Incident Response Agent (LangGraph Workflow)
-- python src/agents/incidentAgent.py "why is checkout slow"   # Execute end-to-end incident investigation workflow
-- python src/agents/incidentAgent.py "is auth service degraded"
-- python src/agents/incidentAgent.py "payments latency spikes"
