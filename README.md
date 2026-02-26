# NBA Prop Analytics

## Quick Start (Unified Workflow)

1. Copy `.env.example` to `.env` and fill in your keys (THEODDS_API_KEY, etc).
2. Create and activate your Python virtual environment:
   - Windows: `python -m venv .venv` then `& ".venv/Scripts/Activate.ps1"`
   - Mac/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the full system (pipeline + dashboard) with:
   - `python run_dashboard.py`

This will:
- Ingest and model today's NBA props
- Generate the board artifact
- Launch the Streamlit dashboard for visual selection

## Environment Variables
- THEODDS_API_KEY
- OPENAI_API_KEY
- DATABASE_URL (for advanced use)
- REDIS_URL (for advanced use)

## Directory Structure
- See `docs/architecture.md` for module breakdown.
