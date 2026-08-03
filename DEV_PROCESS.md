# Surety Dashboard — Summary · Development Process & Handoff

**Purpose:** a self-contained record of the entire development process for this
project, written so a new developer (or a different Claude session with no prior
context) can continue work without re-deriving anything.

**Last Updated:** 2026-06-11
**Status:** Built and pushed to GitHub; deployed on Streamlit Cloud. Not run
locally (no Python interpreter on the original build machine).

> Companion docs: [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) (what & why),
> [ARCHITECTURE.md](ARCHITECTURE.md) (how), [README.md](README.md) (setup/run).
> This file is the *narrative* of how it was built and every decision made.

---

## 1. Project snapshot

| Item | Value |
|---|---|
| App name | Surety Dashboard - Summary (FY 2026-27) |
| Goal | Digitise a single-sheet summary spreadsheet into a web app |
| GitHub repo | https://github.com/Salasar-MIS/surety-dashboard-2 |
| Default branch | `main` |
| Tech stack | Python · Streamlit (frontend) · MongoDB Atlas (pymongo) |
| Deploy target | Streamlit Cloud (entry point `main.py`) |
| Atlas cluster | `suretydb.6jj3uxh.mongodb.net` (shared with the sibling app) |
| Database | `surety_dashboard_summary` (isolated — separate from `surety_dashboard`) |
| Collection | `branch_summary` |
| Relationship to sibling | Independent of `Surety-Dashboard-Claude`; **no shared code or data** |

---

## 2. What the app is

A one-page dashboard for FY 2026-27 with three sections, all manually entered:

1. **Month Wise Branch Revenue** — branches × 12 months (April→March). Branches
   are added / renamed / deleted here.
2. **Revenue in Lakhs** — `Target` and `Achievement` per branch (both manual).
3. **Month Wise Proposal Conversions** — `Proposals` + `Converted` per month.

Branch names are a **single shared dimension**: defined once, reused by all
three sections. All Grand Totals are computed at runtime, never stored.

---

## 3. Requirements analysis (source of truth)

Two inputs were analysed:
- The prose brief (`Surety Dashboard - Manual.txt`).
- The actual Excel file `Surety Dashboard - Summary.xlsx` (sheet
  `Surety Dash Board`, labelled "FY 26-27`), read at the cell/formula level.

**Key finding from the Excel formulas:** the branch names live only in Section 1;
Sections 2 & 3 mirror them with `=A3`-style formulas. → model a branch as one
shared entity, not three independent name lists.

**Discrepancies found (Excel vs prose) and how they were resolved:**

| # | Conflict | Resolution |
|---|---|---|
| 1 | Prose said `Achievement` is manual; Excel derived it as `SUM(months)` | **User decision: manual** (never derived) |
| 2 | Prose point 9 said Proposal-Conversions total sums "Target & Achievement" | Copy-paste slip; Excel sums Proposals/Converted (authoritative) |
| 3 | Name spellings/order differ (`NCR` vs `Delhi (NCR)`, `Ahemdabad`) | Seed with clean spellings; names are editable anyway |

---

## 4. Decision log (all confirmed with the user)

| Decision | Choice | Rationale |
|---|---|---|
| Achievement value | **Manual entry**, never derived | Explicit user instruction (overrides Excel formula) |
| Financial year | **FY 2026-27 only**, no year picker | Single-year scope; schema still carries `financial_year` for future |
| Branch delete | **Hard delete** | User preference; no `is_active` soft-delete flag |
| Proposals vs Converted | **No constraint / no warning** | User preference |
| DB isolation | **Separate database on shared cluster** | User said "separate cluster" but supplied the shared URI; isolation achieved via a distinct DB name (no new infra) |
| Schema shape | **Single `branch_summary` collection**, one doc per branch | Tiny dataset; branch is the natural aggregate root; makes shared names automatic |
| Table UI | **Always-inline editable grid** (not view/edit split) | User tried the split and reverted it |

---

## 5. Data model

Single collection **`branch_summary`**, one document per branch per FY:

```jsonc
{
  "_id": ObjectId,
  "financial_year": "2026-27",
  "name": "Delhi (NCR)",
  "display_order": 1,
  "monthly_revenue": { "April": 0, ... "March": 0 },       // Section 1 (manual)
  "target": 0,                                             // Section 2 (manual)
  "achievement": 0,                                        // Section 2 (manual)
  "proposal_conversions": {                                // Section 3 (manual)
    "April": { "proposals": 0, "converted": 0 }, ... "March": {...}
  }
}
```

- **Indexes:** unique `(financial_year, name)`; `(financial_year, display_order)`.
- **Computed at runtime (never stored):** all column totals, all Grand Totals,
  and the Achievement % (Section 2).
- **Seeded defaults:** Delhi (NCR), Ahmedabad, Mumbai, Naveen Aggarwal (only when
  the collection is empty).

---

## 6. File map

```
Surety-Dashboard-Summary/
├── main.py                 # Streamlit entry: hero, 3 tabs, editable grids, totals
├── seed.py                 # Seed default branches + indexes (idempotent)
├── requirements.txt        # streamlit, pymongo[srv], python-dotenv, pandas
├── .env                    # MONGO_URI / MONGO_DB  (GIT-IGNORED — not in repo)
├── .env.example            # template for .env (safe, committed)
├── .gitignore
├── README.md
├── .streamlit/
│   └── config.toml         # native theme: light base + Salasar brand colours
├── app/
│   ├── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── constants.py    # FINANCIAL_YEAR = "2026-27", MONTHS (Apr→Mar)
│       ├── db.py           # cached Atlas client → surety_dashboard_summary
│       ├── queries.py      # CRUD on branch_summary
│       └── styles.py       # GLOBAL_CSS — glassmorphism, brand, HTML totals tables
├── PROJECT_DESCRIPTION.md
├── ARCHITECTURE.md
└── DEV_PROCESS.md          # this file
```

Runtime totals are computed inline in `main.py` (small helpers); no
`transforms.py` was needed at this scale.

---

## 7. Development timeline (git history)

| Commit | Summary | Notes |
|---|---|---|
| `15e333a` | Initial commit — full app (schema, CRUD, 3 tabs) | MVP |
| `96a250d` | Fail fast on DB connection + readable startup error | 5s server-selection timeout; catches boot errors |
| `fbe5d36` | Redesign UI: glassmorphism dashboard + Salasar branding | hero, pill tabs, glass cards, KPI cards, HTML totals |
| `58509ba` | Theme data grids to brand colours + fix "None" cells | config.toml palette; coerce null → 0 |
| `c0d0702` | View/edit split (branded read-only tables + edit expander) | experiment |
| `b9771b1` | **Revert** the view/edit split | back to always-inline grid (current `HEAD`) |

**Current `HEAD` = `b9771b1`** (functionally identical to `58509ba`).

---

## 8. Deployment & operations knowledge

- **Streamlit Cloud secrets** (Settings → Secrets) must contain:
  ```toml
  MONGO_URI = "mongodb+srv://<user>:<pass>@suretydb.6jj3uxh.mongodb.net/?appName=SuretyDB"
  MONGO_DB  = "surety_dashboard_summary"
  ```
- **MongoDB Atlas → Network Access** must allow `0.0.0.0/0` (Streamlit Cloud IPs
  are dynamic). This is the #1 cause of a boot loop.
- `db.py` reads settings from Streamlit secrets first, then `.env` (via
  `python-dotenv`) for local runs.

### Troubleshooting log
- **"Failed to fetch dynamically imported module … Button.*.js"** — a Streamlit
  Cloud *frontend* error, not a Python bug. Causes: (a) stale browser cache after
  a redeploy → **hard refresh** (Ctrl+Shift+R); (b) the app crash-looping on
  startup (bad secrets / Atlas network) → fixed by the fail-fast timeout in
  `96a250d`, which now shows a readable DB error instead.

---

## 9. UI/UX notes (important for future styling work)

- **Aesthetic:** light glassmorphism (frosted translucent panels over a soft
  brand-tinted gradient). Salasar palette: navy `#172962`, deep blue `#2d448d`,
  lime `#a6ce39`, sky `#459fda`. Inter font.
- **Hard limitation:** `st.data_editor` / `st.dataframe` render on an HTML
  **canvas** (glide-data-grid). CSS **cannot** style individual cells/headers.
  Only `config.toml` theme colours (cell bg, header tint, text, selection) apply.
  Everything glassy lives *around* the grid (hero, tabs, cards, HTML totals
  tables, KPI cards).
- **shadcn/ui** is React-only and cannot back Streamlit's editable grids; the
  shadcn-like look is achieved with native theme + custom CSS (no extra dep).
- The **view/edit split** (pretty read-only HTML table + edit-behind-expander)
  was implemented and reverted — the user preferred always-inline editing. If
  revisited, the read-only table CSS still exists in `styles.py` (`.dash-table`).

---

## 10. Known limitations & possible next steps

- **Not run locally** — no Python on the build machine; logic reviewed but never
  executed there. First real run is on Streamlit Cloud.
- **No authentication** — open app (matches the sibling project's Phase 1).
- **Concurrency** — `st.data_editor` saves are last-write-wins per section; fine
  for a small single-team tool.
- **Partial save on duplicate name** — if a rename collides mid-save, earlier
  writes in that batch persist; user re-saves. Acceptable at this scale.
- Potential future work: auth, multi-year (schema already supports it), reorder
  UI for `display_order`, CSV/Excel export, per-branch drill-downs.

---

## 11. Running & deploying

```bash
# Local (requires Python 3.9+)
pip install -r requirements.txt
# create .env with MONGO_URI and MONGO_DB (see §8)
streamlit run main.py        # seeds 4 default branches on first run
```

Deploy: point Streamlit Cloud at the repo, entry point `main.py`, set the two
secrets, ensure Atlas network access allows `0.0.0.0/0`.

---

## 12. Handoff checklist (for the receiving developer / Claude id)

- [ ] Get **repo access** to https://github.com/Salasar-MIS/surety-dashboard-2
      and clone `main`.
- [ ] Obtain **`.env` values** (`MONGO_URI`, `MONGO_DB`) — they are **not** in
      the repo (git-ignored). Get them from the Salasar admin / Atlas.
- [ ] Confirm **Atlas access** (cluster `suretydb`, DB `surety_dashboard_summary`)
      and that Network Access allows `0.0.0.0/0`.
- [ ] Confirm **Streamlit Cloud** app owner/secrets if taking over the deploy.
- [ ] **Security:** the DB password was shared in chat during initial setup —
      rotate `surety_db_user`'s password in Atlas and update secrets/`.env`.
- [ ] Read §4 (decisions) before changing behaviour — several defaults were
      explicit user choices, not accidents.

---

## Appendix A — Original spreadsheet layout (preserved for reference)

Source files (kept **outside** the repo on the build machine):
`D:\Surety Dashboard - Summary (Manual)\`
- `Surety Dashboard - Summary.xlsx` — the source spreadsheet.
- `Surety Dashboard - Manual.txt` — the written requirements brief.

The Excel (sheet `Surety Dash Board`, "FY 26-27`) laid out three tables. The
structure below is what the app reproduces:

- **Month Wise Branch Rev** — col A `Name`; cols B–M = April…March; rows =
  branches (Naveen Aggarwal, NCR, Ahemdabad, Mumbai + blank rows); row 9 =
  `Grand Total` = `SUM` per month column.
- **Revenue in lacs** (top-right block) — `Names` (=A3… mirror of Section 1),
  `Target` (manual), `Achievement` (`=SUM(months)` in Excel — **overridden to
  manual per user decision**); `Grand Total` row.
- **Month Wise Proposal Conversions** — `Name` (mirror), each month spans two
  columns `Proposals` + `Converted`; `Grand Total` row = `SUM` per column.

If the receiving developer wants the raw source files committed into a `docs/`
folder, they can be added — they were left out to keep the repo code-only.

---

## Appendix B — Local build environment (original machine)

- **OS:** Windows 11; shells used: PowerShell + Git Bash.
- **No Python interpreter** was installed on the build machine (only Microsoft
  Store shims) — so the app was **never run locally**; it was reviewed
  statically and validated via the Streamlit Cloud deploy.
- **Local folder nesting:** this project folder lives *inside* the sibling
  project's working directory
  (`D:\Surety-Dashboard-Claude\Surety-Dashboard-Summary`) but is its **own
  independent git repo** (its own `.git`, remote `surety-dashboard-2`). The two
  repos share nothing. When cloning fresh, clone `surety-dashboard-2` on its own.
- **Git identity used:** `Salasar-MIS <ambarish@salasarservices.co.in>`; auth via
  Git Credential Manager (cached GitHub creds).

---

## Appendix C — Relationship to the sibling project

`Surety-Dashboard-Claude` (repo `SuretyDashboard`) is a **separate, more complex**
app: RM-level and sub-branch data, with Naveen Aggarwal as an aggregator of 12
sub-branches, stored in the `surety_dashboard` database. **This Summary app is
deliberately independent**: flat branch-level only, its own repo, its own
`surety_dashboard_summary` database. Do not merge, share code, or point one at
the other's data. The only thing borrowed was the visual brand palette.
```
