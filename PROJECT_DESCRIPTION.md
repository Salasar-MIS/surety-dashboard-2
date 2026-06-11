# Surety Dashboard — Summary (FY 2026-27)

**Status:** Built — all decisions resolved; not yet run/deployed (no local Python)
**Last Updated:** 2026-06-11

---

## Purpose

An **independent**, low-code web app that digitises the single-sheet
"Surety Dashboard - Summary" spreadsheet for Financial Year 2026-27. It is a
branch-level summary only — it does **not** reuse or share data with the
existing `Surety-Dashboard-Claude` project (which is RM / sub-branch level).

Source of truth analysed: `Surety Dashboard - Summary.xlsx`
(sheet `Surety Dash Board`, labelled "FY 26-27").

---

## The three sections (as they actually appear in the Excel)

### 1. Month Wise Branch Revenue
- Rows = branch names (seed: Delhi (NCR), Ahmedabad, Mumbai, Naveen Aggarwal),
  with spare rows so users can add branches.
- Columns = 12 months, **April → March** (Indian FY order).
- Data entered manually per branch per month.
- Each month column is summed at the bottom in a **Grand Total** row.

### 2. Revenue in Lakhs
- Columns = `Names`, `Target`, `Achievement`.
- `Names` mirror the branches from Section 1 (single shared list).
- `Target` — entered manually.
- `Achievement` — entered manually by the user, independently. It is **not**
  populated or derived from monthly revenue or any other section/branch.
  (This overrides the Excel formula, per the user's decision on 2026-06-11.)
- `Grand Total` row sums Target and Achievement.

### 3. Month Wise Proposal Conversions
- Rows = the same shared branches.
- Columns = 12 months, each split into `Proposals` and `Converted`.
- Data entered manually.
- `Grand Total` row sums each Proposals/Converted column.

---

## Key insight

Branch names are defined **once** (Section 1) and reused by Sections 2 & 3
(the Excel mirrors them with formulas). A branch is therefore a single shared
dimension across all three tables — rename/add once, reflected everywhere.

---

## Open questions (must resolve before coding)

1. ~~**Achievement** — derive or manual?~~ **RESOLVED 2026-06-11:** Achievement
   is entered **manually**; never populated from any other source/branch.
2. **Units** — Section 2 is "in Lakhs"; what unit is Section 1's monthly
   revenue in? (No longer affects Achievement, but worth confirming for labels.)
3. ~~**Multi-year**?~~ **RESOLVED 2026-06-11:** **FY 2026-27 only.** No year
   picker in the UI. Schema still carries `financial_year` (fixed constant) so
   a year selector could be added later without migration, but it is not built.
4. ~~**Proposal validation**?~~ **RESOLVED 2026-06-11:** Allow freely — no
   constraint between `converted` and `proposals`, no warning.
5. ~~**Deletion**?~~ **RESOLVED 2026-06-11:** **Hard delete** — the branch
   document is permanently removed. No `is_active` soft-delete flag.

---

## Tech stack & infrastructure

- **Backend:** Python
- **Frontend:** Streamlit
- **Database:** MongoDB Atlas (via pymongo)
- **GitHub repo:** https://github.com/Salasar-MIS/surety-dashboard-2
- **Cluster:** shared Atlas cluster `suretydb.6jj3uxh.mongodb.net` (same one the
  existing `Surety-Dashboard-Claude` app uses).
- **Database (isolated):** `surety_dashboard_summary` — a **separate database**
  on that shared cluster, so this app's data never mixes with the existing
  app's `surety_dashboard` database.
- **Collection:** `branch_summary`
- Credentials live in a git-ignored `.env` (and Streamlit Cloud secrets for
  deployment) — never committed.

## Best-practice constraints (from the brief)

- Keep the app low-code; high code quality; simple comments over each block.
- Handle edge cases (blank cells = 0, duplicate names, etc.).
- Do not write unnecessary code; ask before implementing any unspecified logic.
- Keep this project entirely separate from `Surety-Dashboard-Claude`.
