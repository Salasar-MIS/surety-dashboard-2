# Surety Dashboard — Summary (FY 2026-27)

A low-code Streamlit + MongoDB Atlas app that digitises the single-sheet
"Surety Dashboard - Summary" spreadsheet for FY 2026-27. Independent of the
`Surety-Dashboard-Claude` project; uses a separate database on the shared
Atlas cluster.

See [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) and
[ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## Sections

1. **Month Wise Branch Revenue** — branches × 12 months (Apr→Mar); branches are
   added / renamed / deleted here.
2. **Revenue in Lakhs** — Target and Achievement per branch (both manual).
3. **Month Wise Proposal Conversions** — Proposals & Converted per month.

Grand Totals are computed at runtime.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` (not committed):

```ini
MONGO_URI=<your Atlas srv connection string>
MONGO_DB=surety_dashboard_summary
```

## Run

```bash
streamlit run main.py
```

Default branches (Delhi (NCR), Ahmedabad, Mumbai, Naveen Aggarwal) are seeded
automatically on first run against an empty database.

## Deploy (Streamlit Cloud)

Set `MONGO_URI` and `MONGO_DB` in the app's **Secrets**; the entry point is
`main.py`.
