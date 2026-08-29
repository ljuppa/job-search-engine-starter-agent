# ADR-004 — Explicit Agent Orchestration

**Status:** Accepted

## Decision
Agents never invoke other agents directly. Workflow orchestration determines execution order, thresholds, retries and state transitions.

## Consequences
Better testability, deterministic workflow control and failure attribution.
