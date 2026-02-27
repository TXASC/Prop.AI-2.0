# Modeling

## Assumptions
- Market-based consensus mean
- Normal distribution per stat with tuned stdev priors

## Distribution Choices
- Normal (Phase A)
- Empirical/Player archetype (Phase B+)

## Roadmap
- Improve stdev priors
- Add correlation modeling
- Integrate news/injury factors

## Explainability & Transparency
- Each pick is now accompanied by a "Handicapper Notes" section and a "Key Factors" table, summarizing the main reasons and data points behind the recommendation.
- The dashboard includes a summary of ROI, Net Profit, CLV, and Hit Rate for ongoing performance review.
- See `nba_dashboard.py` for code and logic.
