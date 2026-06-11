# Surety Dashboard — Summary — Architecture

**Status:** Implemented (code written; pending first run / deploy)
**Last Updated:** 2026-06-11

---

## High-Level Architecture

```
[ User (Browser) ]
        │
        ▼
[ Streamlit App ]
   - One page, three sections (tabs or stacked tables)
   - Editable data grids (st.data_editor) for manual entry
   - Branch add / rename / reorder / (soft) delete
        │
        ▼
[ Python Backend Layer ]
   - db.py        : MongoDB Atlas connection (pymongo, cached)
   - queries.py   : read/write one collection
   - transforms.py: runtime totals (achievement, column sums, grand totals)
        │
        ▼
[ MongoDB Atlas ]
   - branch_summary   (one document per branch per financial year)
```

---

## Recommended schema — single collection `branch_summary`

The dataset is tiny (a few branches × 12 months) and a branch carries data for
all three sections, so the branch is the natural aggregate root. One document
per branch per FY keeps the shared-name behaviour automatic and the app
low-code.

```jsonc
{
  "_id": ObjectId,
  "financial_year": "2026-27",
  "name": "Delhi (NCR)",
  "display_order": 1,

  // Section 1 — Month Wise Branch Revenue (manual)
  "monthly_revenue": {
    "April": 0, "May": 0, "June": 0, "July": 0,
    "August": 0, "September": 0, "October": 0, "November": 0,
    "December": 0, "January": 0, "February": 0, "March": 0
  },

  // Section 2 — Revenue in Lakhs (both entered manually, independently)
  "target": 0,            // manual
  "achievement": 0,       // manual — NOT derived from any other source/branch

  // Section 3 — Month Wise Proposal Conversions (manual)
  "proposal_conversions": {
    "April":    { "proposals": 0, "converted": 0 },
    "May":      { "proposals": 0, "converted": 0 },
    "June":     { "proposals": 0, "converted": 0 },
    "July":     { "proposals": 0, "converted": 0 },
    "August":   { "proposals": 0, "converted": 0 },
    "September": { "proposals": 0, "converted": 0 },
    "October":  { "proposals": 0, "converted": 0 },
    "November": { "proposals": 0, "converted": 0 },
    "December": { "proposals": 0, "converted": 0 },
    "January":  { "proposals": 0, "converted": 0 },
    "February": { "proposals": 0, "converted": 0 },
    "March":    { "proposals": 0, "converted": 0 }
  }
}
```

### Indexes
- Unique `(financial_year, name)` — prevents duplicate branches per year.
- `(financial_year, display_order)` — stable ordering for display.

### Derived at runtime (never stored)
| Value | Derivation |
|---|---|
| Month column total (Sec 1) | sum of that month across all branches |
| Target / Achievement grand total (Sec 2) | sum across all branches |
| Proposals / Converted column totals (Sec 3) | sum across all branches |

> Note: branch-level `target` and `achievement` are stored manual values.
> Only the **Grand Total** row of Section 2 is computed (column sums).

### Branch operations
- **Add** → insert one document with zeroed sub-structures.
- **Rename** → update `name` (reflected in all sections automatically).
- **Reorder** → change `display_order`.
- **Remove** → hard delete: permanently remove the branch document.

---

## Alternative schema (normalized) — not recommended at this scale

`branches` + `monthly_revenue` + `revenue_targets` + `proposal_conversions`
(closer to the existing project). More collections and joins for no benefit
given the data volume. Consider only if many branches or per-month audit
history become requirements.

---

## Configuration & deployment

- **GitHub repo:** https://github.com/Salasar-MIS/surety-dashboard-2
- **Atlas cluster:** `suretydb.6jj3uxh.mongodb.net` (shared with the existing
  app — same connection string / DB user).
- **Database:** `surety_dashboard_summary` (separate DB on the shared cluster →
  full isolation from the existing app's `surety_dashboard`).
- **Environment variables** (in git-ignored `.env`; Streamlit Cloud secrets in
  deployment):

  ```ini
  MONGO_URI=<srv connection string>   # do not commit the real value
  MONGO_DB=surety_dashboard_summary
  ```

- `.gitignore` excludes `.env`, `__pycache__/`, `*.pyc`,
  `.streamlit/secrets.toml`.

---

## Constants (fixed in code, not DB)

```python
MONTHS = ["April", "May", "June", "July", "August", "September",
          "October", "November", "December", "January", "February", "March"]
FINANCIAL_YEAR = "2026-27"   # fixed — single-year app, no year picker in UI
```

---

## Folder structure (as built)

```
Surety-Dashboard-Summary/
├── main.py                 # Streamlit entry point: hero, 3 tabs, editable grids, totals
├── seed.py                 # Seed default branches + indexes (idempotent)
├── requirements.txt
├── .env                    # MONGO_URI / MONGO_DB (git-ignored)
├── .gitignore
├── README.md
├── .streamlit/
│   └── config.toml         # native theme (light base + Salasar brand colours)
├── app/
│   ├── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── constants.py    # FINANCIAL_YEAR, MONTHS
│       ├── db.py           # Atlas connection (cached) → surety_dashboard_summary
│       ├── queries.py      # CRUD on branch_summary
│       └── styles.py       # GLOBAL_CSS — glassmorphism, brand, modern tables
├── PROJECT_DESCRIPTION.md
└── ARCHITECTURE.md
```

> Note: runtime totals are computed inline in `main.py` (a few small helpers);
> no separate `transforms.py` was needed at this scale.

---

## UI / UX design

- **Aesthetic:** light, modern dashboard with **glassmorphism** panels (frosted
  translucent cards) over a soft brand-tinted gradient background.
- **Brand palette (Salasar):** navy `#172962`, deep blue `#2d448d`,
  lime `#a6ce39`, sky `#459fda`. Set in `.streamlit/config.toml` (native widget
  theme) and `app/utils/styles.py` (custom CSS).
- **Layout:** a glass hero header (logo + title + FY badge); three pill-style
  tabs, one per section; each section is a glass card with a label/title/subtitle.
- **View / edit split:** each section shows a fully-branded **read-only HTML
  table** (the canvas grid can't be deep-styled), with the editable
  `st.data_editor` grid tucked behind an **"✏️ Edit" expander**. This gives a
  full theme match for the default view while keeping inline editing on demand.
- **Totals:** read-only tables include a Grand Total footer row (brand header,
  green accent line, sticky first column). Section 2 also shows KPI metric cards
  (Total Target, Total Achievement, Achievement %).
- **Branch management** (add / rename / delete) lives in Section 1's editor.
- **Note on shadcn/ui:** it is a React library and cannot back Streamlit's
  editable grids, so the shadcn-style look is achieved with the native theme +
  custom CSS instead (no extra dependency).
```

---

## Edge cases to handle

- Blank / `None` cell → treated as 0 in all sums.
- Duplicate branch name within a FY → blocked by unique index + UI check.
- `converted` and `proposals` accepted freely (no relationship enforced).
- Deleting the last branch → keep Grand Total row showing zeros, not an error.
- Non-numeric input in a numeric cell → validated before write.
```
