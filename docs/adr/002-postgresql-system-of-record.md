# ADR-002 — PostgreSQL as System of Record

**Status:** Accepted

## Decision
Use PostgreSQL for canonical and derived application state. Add pgvector later if semantic retrieval requires it. Avoid MongoDB, Elasticsearch and a separate vector DB until justified.
