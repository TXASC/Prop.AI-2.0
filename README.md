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

## Dashboard Explainability & Metrics
- Each pick now includes auto-generated **Handicapper Notes** and a **Key Factors** table, highlighting the main drivers of the projection and edge.
- A summary section at the bottom of the dashboard displays ROI, Net Profit, Closing Line Value (CLV), and Hit Rate for transparency and performance tracking.
- See `nba_dashboard.py` for implementation details.

## Methodology
- Model outputs are explained using top contributing features (e.g., projection vs. line, edge %, etc.).
- Notes and factors are generated automatically for each pick, improving user trust and system transparency.
- For more, see `docs/modeling.md` and `docs/metrics.md`.
