# Architecture

## Pipeline Diagram

```mermaid
graph TD
    ingest[Ingest Odds/Lines] --> normalize[Normalize Markets]
    normalize --> store[Store in DB]
    store --> model[Model Projections]
    model --> edge[Edge Calculation]
    edge --> track[Tracking/Grading]
    track --> artifacts[Artifacts Output]
```

## Module Responsibilities
- api/: FastAPI endpoints
- cli/: Typer CLI commands
- core/: Business logic modules
- migrations/: Alembic migrations
- tests/: Unit tests
- docs/: Documentation
- output/: Daily artifacts
