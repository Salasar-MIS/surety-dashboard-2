"""
Surety Dashboard - Summary (FY 2026-27)

Single page, three editable sections backed by MongoDB Atlas:
  1. Month Wise Branch Revenue   (branch list is managed here)
  2. Revenue in Lakhs            (Target + Achievement, both manual)
  3. Month Wise Proposal Conversions

All Grand Totals are computed at runtime, never stored.
"""
import pandas as pd
import streamlit as st
from pymongo.errors import DuplicateKeyError

from app.utils import queries as q
from app.utils.constants import FINANCIAL_YEAR, MONTHS

st.set_page_config(
    page_title="Surety Dashboard - Summary", page_icon="📊", layout="wide"
)


# Seed default branches + indexes once per server session.
@st.cache_resource
def _bootstrap():
    from seed import seed

    seed()


# Surface DB/connection problems as a readable message instead of a crash loop
# (a startup crash on Streamlit Cloud otherwise shows as a JS "failed to fetch
# module" error in the browser).
try:
    _bootstrap()
except Exception as exc:
    st.error(
        "Could not connect to the database.\n\n"
        "On Streamlit Cloud, check that **MONGO_URI** and **MONGO_DB** are set "
        "under **Settings → Secrets**, and that MongoDB Atlas **Network Access** "
        "allows connections from anywhere (`0.0.0.0/0`), since Streamlit Cloud "
        "IPs are dynamic.\n\n"
        f"Details: `{exc}`"
    )
    st.stop()


# ── small helpers ─────────────────────────────────────────────────────────────


def _num_col(label, integer=False):
    """Numeric column config: non-negative, with sensible step/format."""
    return st.column_config.NumberColumn(
        label,
        min_value=0,
        default=0,
        step=1 if integer else 0.01,
        format="%d" if integer else "%.2f",
    )


def _col_sum(df, column, integer=False):
    """Sum a column, treating blanks as 0."""
    total = pd.to_numeric(df[column], errors="coerce").fillna(0).sum()
    return int(total) if integer else float(total)


def _grand_total(first_col, value_map):
    """Render a read-only 'Grand Total' row beneath an editor."""
    row = {first_col: "Grand Total", **value_map}
    st.dataframe(pd.DataFrame([row]), use_container_width=True, hide_index=True)


# ── Section 1: Month Wise Branch Revenue ──────────────────────────────────────


def render_revenue(branches):
    st.subheader("Month Wise Branch Revenue")
    st.caption(
        "Branches are managed here: add a row to create one, edit a name to "
        "rename it, delete a row to remove it (removes it from all sections)."
    )

    # Build the grid: hidden _id, editable Name + 12 month columns.
    rows = []
    for b in branches:
        row = {"_id": str(b["_id"]), "Name": b["name"]}
        row.update({m: b["monthly_revenue"].get(m, 0) for m in MONTHS})
        rows.append(row)
    df = pd.DataFrame(rows, columns=["_id", "Name"] + MONTHS)

    cfg = {"_id": None, "Name": st.column_config.TextColumn("Name", required=True)}
    cfg.update({m: _num_col(m) for m in MONTHS})

    edited = st.data_editor(
        df, column_config=cfg, num_rows="dynamic",
        hide_index=True, use_container_width=True, key="ed_revenue",
    )

    # Live column totals (reflect unsaved edits).
    _grand_total("Name", {m: _col_sum(edited, m) for m in MONTHS})

    if st.button("Save revenue", key="save_revenue"):
        _save_revenue(df, edited)


def _save_revenue(original, edited):
    """Diff original vs edited rows to apply renames, inserts and deletions."""
    orig_ids = set(original["_id"].dropna())
    kept_ids = set(edited["_id"].dropna())
    try:
        # Hard-delete branches whose rows were removed in the editor.
        for bid in orig_ids - kept_ids:
            q.delete_branch(bid)

        # Upsert each remaining/new row.
        for _, r in edited.iterrows():
            name = str(r.get("Name") or "").strip()
            if not name:
                continue  # ignore blank rows (e.g. an empty added row)
            monthly = {m: (float(r[m]) if pd.notna(r[m]) else 0) for m in MONTHS}
            bid = r.get("_id")
            if pd.notna(bid):  # existing branch
                q.rename_branch(bid, name)
                q.set_monthly_revenue(bid, monthly)
            else:  # newly added row
                q.add_branch(name, monthly)
    except DuplicateKeyError:
        st.error("Branch names must be unique — fix duplicates and save again.")
        return

    st.success("Revenue saved.")
    st.rerun()


# ── Section 2: Revenue in Lakhs ───────────────────────────────────────────────


def render_lakhs(branches):
    st.subheader("Revenue in Lakhs")
    st.caption(
        "Target and Achievement are entered manually. Names mirror the "
        "Revenue section and are managed there."
    )

    rows = [
        {
            "_id": str(b["_id"]),
            "Name": b["name"],
            "Target": b.get("target", 0),
            "Achievement": b.get("achievement", 0),
        }
        for b in branches
    ]
    df = pd.DataFrame(rows, columns=["_id", "Name", "Target", "Achievement"])

    cfg = {
        "_id": None,
        "Name": st.column_config.TextColumn("Name", disabled=True),
        "Target": _num_col("Target"),
        "Achievement": _num_col("Achievement"),
    }
    edited = st.data_editor(
        df, column_config=cfg, num_rows="fixed",
        hide_index=True, use_container_width=True, key="ed_lakhs",
    )

    _grand_total(
        "Name",
        {"Target": _col_sum(edited, "Target"),
         "Achievement": _col_sum(edited, "Achievement")},
    )

    if st.button("Save target / achievement", key="save_lakhs"):
        for _, r in edited.iterrows():
            target = float(r["Target"]) if pd.notna(r["Target"]) else 0
            achievement = float(r["Achievement"]) if pd.notna(r["Achievement"]) else 0
            q.set_target_achievement(r["_id"], target, achievement)
        st.success("Target / achievement saved.")
        st.rerun()


# ── Section 3: Month Wise Proposal Conversions ────────────────────────────────


def render_proposals(branches):
    st.subheader("Month Wise Proposal Conversions")
    st.caption(
        "Proposals and Converted are entered manually per month. "
        "Names mirror the Revenue section."
    )

    # Two value columns per month: "<Month> - Proposals" / "<Month> - Converted".
    value_cols = []
    for m in MONTHS:
        value_cols += [f"{m} - Proposals", f"{m} - Converted"]

    rows = []
    for b in branches:
        row = {"_id": str(b["_id"]), "Name": b["name"]}
        for m in MONTHS:
            pc = b.get("proposal_conversions", {}).get(m, {})
            row[f"{m} - Proposals"] = pc.get("proposals", 0)
            row[f"{m} - Converted"] = pc.get("converted", 0)
        rows.append(row)
    df = pd.DataFrame(rows, columns=["_id", "Name"] + value_cols)

    cfg = {"_id": None, "Name": st.column_config.TextColumn("Name", disabled=True)}
    cfg.update({c: _num_col(c, integer=True) for c in value_cols})

    edited = st.data_editor(
        df, column_config=cfg, num_rows="fixed",
        hide_index=True, use_container_width=True, key="ed_proposals",
    )

    _grand_total("Name", {c: _col_sum(edited, c, integer=True) for c in value_cols})

    if st.button("Save proposals", key="save_proposals"):
        for _, r in edited.iterrows():
            conversions = {}
            for m in MONTHS:
                p = r[f"{m} - Proposals"]
                c = r[f"{m} - Converted"]
                conversions[m] = {
                    "proposals": int(p) if pd.notna(p) else 0,
                    "converted": int(c) if pd.notna(c) else 0,
                }
            q.set_proposals(r["_id"], conversions)
        st.success("Proposals saved.")
        st.rerun()


# ── Page ──────────────────────────────────────────────────────────────────────

st.title("Surety Dashboard — Summary")
st.markdown(f"**Financial Year {FINANCIAL_YEAR}**")

branches = q.get_branches()

tab1, tab2, tab3 = st.tabs(
    ["Month Wise Branch Revenue", "Revenue in Lakhs", "Month Wise Proposal Conversions"]
)
with tab1:
    render_revenue(branches)
with tab2:
    render_lakhs(branches)
with tab3:
    render_proposals(branches)
