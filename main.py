"""
Surety Dashboard - Summary (FY 2026-27)

A modern, glassmorphism Streamlit dashboard with three sections backed by
MongoDB Atlas. Each section shows a fully-branded read-only table (the "view")
and an editable grid behind an "Edit" expander (the "edit"):
  1. Month Wise Branch Revenue   (branch list is managed in its editor)
  2. Revenue in Lakhs            (Target + Achievement, both manual)
  3. Month Wise Proposal Conversions

All Grand Totals are computed at runtime, never stored.
"""
import html

import pandas as pd
import streamlit as st
from pymongo.errors import DuplicateKeyError

from app.utils import queries as q
from app.utils.constants import FINANCIAL_YEAR, MONTHS
from app.utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="Surety Dashboard - Summary", page_icon="📊", layout="wide"
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

LOGO_URL = "https://www.salasarservices.com/assets/Frontend/images/Salasar-New-Logo.png"


# Seed default branches + indexes once per server session.
@st.cache_resource
def _bootstrap():
    from seed import seed

    seed()


# Surface DB/connection problems as a readable message instead of a crash loop.
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
        label, min_value=0, default=0,
        step=1 if integer else 0.01,
        format="%d" if integer else "%.2f",
    )


def _fmt(value, integer=False):
    """Format a number with thousands separators for display."""
    return f"{int(round(value)):,}" if integer else f"{value:,.2f}"


def _esc(text):
    """Escape branch names before placing them in HTML."""
    return html.escape(str(text))


def _section_head(label, title, subtitle):
    """Render the small label + title + subtitle at the top of a section."""
    st.markdown(
        f'<div class="section-label">{label}</div>'
        f'<div class="section-title">{title}</div>'
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def _render_table(head_html, body_html, foot_html):
    """Render a branded read-only table from pre-built header/body/footer HTML."""
    st.markdown(
        f'<div class="table-scroll"><table class="dash-table">'
        f"<thead>{head_html}</thead><tbody>{body_html}</tbody>"
        f"<tfoot><tr>{foot_html}</tr></tfoot></table></div>",
        unsafe_allow_html=True,
    )


# ── Section 1: Month Wise Branch Revenue ──────────────────────────────────────


def render_revenue(branches):
    with st.container(border=True):
        _section_head(
            "Section 01",
            "Month Wise Branch Revenue",
            "Monthly revenue per branch. Use the editor below to add, rename or "
            "delete branches (changes apply across all three sections).",
        )

        # ── View: branded read-only table with a Grand Total row ──
        head = "<tr class='main-header'>" + "".join(
            f"<th>{h}</th>" for h in ["Name"] + MONTHS
        ) + "</tr>"
        body, totals = "", {m: 0 for m in MONTHS}
        for b in branches:
            body += f"<tr><td>{_esc(b['name'])}</td>"
            for m in MONTHS:
                v = b["monthly_revenue"].get(m) or 0
                totals[m] += v
                body += f"<td>{_fmt(v)}</td>"
            body += "</tr>"
        foot = "<td>Grand Total</td>" + "".join(f"<td>{_fmt(totals[m])}</td>" for m in MONTHS)
        _render_table(head, body, foot)

        # ── Edit: dynamic grid (also where branches are managed) ──
        with st.expander("✏️  Edit branch revenue", expanded=False):
            rows = []
            for b in branches:
                row = {"_id": str(b["_id"]), "Name": b["name"]}
                row.update({m: (b["monthly_revenue"].get(m) or 0) for m in MONTHS})
                rows.append(row)
            df = pd.DataFrame(rows, columns=["_id", "Name"] + MONTHS)

            cfg = {"_id": None, "Name": st.column_config.TextColumn("Name", required=True)}
            cfg.update({m: _num_col(m) for m in MONTHS})
            edited = st.data_editor(
                df, column_config=cfg, num_rows="dynamic",
                hide_index=True, use_container_width=True, key="ed_revenue",
            )
            if st.button("💾  Save revenue", key="save_revenue"):
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
    with st.container(border=True):
        _section_head(
            "Section 02",
            "Revenue in Lakhs",
            "Target and Achievement are entered manually. Branch names mirror the "
            "Revenue section.",
        )

        # ── View: read-only table + KPI cards ──
        head = "<tr class='main-header'><th>Name</th><th>Target</th><th>Achievement</th></tr>"
        body, total_target, total_ach = "", 0, 0
        for b in branches:
            t = b.get("target") or 0
            a = b.get("achievement") or 0
            total_target += t
            total_ach += a
            body += f"<tr><td>{_esc(b['name'])}</td><td>{_fmt(t)}</td><td>{_fmt(a)}</td></tr>"
        foot = f"<td>Grand Total</td><td>{_fmt(total_target)}</td><td>{_fmt(total_ach)}</td>"
        _render_table(head, body, foot)

        pct = (total_ach / total_target * 100) if total_target else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Target", _fmt(total_target))
        c2.metric("Total Achievement", _fmt(total_ach))
        c3.metric("Achievement %", f"{pct:,.1f}%")

        # ── Edit ──
        with st.expander("✏️  Edit target / achievement", expanded=False):
            rows = [
                {
                    "_id": str(b["_id"]),
                    "Name": b["name"],
                    "Target": b.get("target") or 0,
                    "Achievement": b.get("achievement") or 0,
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
            if st.button("💾  Save target / achievement", key="save_lakhs"):
                for _, r in edited.iterrows():
                    target = float(r["Target"]) if pd.notna(r["Target"]) else 0
                    achievement = float(r["Achievement"]) if pd.notna(r["Achievement"]) else 0
                    q.set_target_achievement(r["_id"], target, achievement)
                st.success("Target / achievement saved.")
                st.rerun()


# ── Section 3: Month Wise Proposal Conversions ────────────────────────────────


def render_proposals(branches):
    with st.container(border=True):
        _section_head(
            "Section 03",
            "Month Wise Proposal Conversions",
            "Proposals and Converted per month, entered manually. Branch names "
            "mirror the Revenue section.",
        )

        # ── View: read-only table with two-level (month → Proposals/Converted) header ──
        main = "<th rowspan='2'>Name</th>" + "".join(
            f"<th colspan='2'>{m}</th>" for m in MONTHS
        )
        sub = "".join("<th>Proposals</th><th>Converted</th>" for _ in MONTHS)
        head = f"<tr class='main-header'>{main}</tr><tr class='sub-header'>{sub}</tr>"

        body = ""
        prop_tot = [0] * len(MONTHS)
        conv_tot = [0] * len(MONTHS)
        for b in branches:
            body += f"<tr><td>{_esc(b['name'])}</td>"
            for i, m in enumerate(MONTHS):
                pc = b.get("proposal_conversions", {}).get(m, {})
                p = pc.get("proposals") or 0
                c = pc.get("converted") or 0
                prop_tot[i] += p
                conv_tot[i] += c
                body += f"<td>{_fmt(p, True)}</td><td>{_fmt(c, True)}</td>"
            body += "</tr>"
        foot = "<td>Grand Total</td>" + "".join(
            f"<td>{_fmt(prop_tot[i], True)}</td><td>{_fmt(conv_tot[i], True)}</td>"
            for i in range(len(MONTHS))
        )
        _render_table(head, body, foot)

        # ── Edit ──
        with st.expander("✏️  Edit proposals / converted", expanded=False):
            value_cols = []
            for m in MONTHS:
                value_cols += [f"{m} - Proposals", f"{m} - Converted"]

            rows = []
            for b in branches:
                row = {"_id": str(b["_id"]), "Name": b["name"]}
                for m in MONTHS:
                    pc = b.get("proposal_conversions", {}).get(m, {})
                    row[f"{m} - Proposals"] = pc.get("proposals") or 0
                    row[f"{m} - Converted"] = pc.get("converted") or 0
                rows.append(row)
            df = pd.DataFrame(rows, columns=["_id", "Name"] + value_cols)

            cfg = {"_id": None, "Name": st.column_config.TextColumn("Name", disabled=True)}
            cfg.update({c: _num_col(c, integer=True) for c in value_cols})
            edited = st.data_editor(
                df, column_config=cfg, num_rows="fixed",
                hide_index=True, use_container_width=True, key="ed_proposals",
            )
            if st.button("💾  Save proposals", key="save_proposals"):
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

# Glass hero header with brand logo + FY badge.
st.markdown(
    f"""
    <div class="app-hero">
      <div class="hero-left">
        <img src="{LOGO_URL}" class="hero-logo" alt="Salasar" />
        <div>
          <div class="hero-title">Surety Dashboard — Summary</div>
          <div class="hero-sub">Centralised surety bond performance overview</div>
        </div>
      </div>
      <div class="hero-badge">FY {FINANCIAL_YEAR}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

branches = q.get_branches()

tab1, tab2, tab3 = st.tabs(
    ["📈  Month Wise Branch Revenue", "🎯  Revenue in Lakhs", "🔄  Proposal Conversions"]
)
with tab1:
    render_revenue(branches)
with tab2:
    render_lakhs(branches)
with tab3:
    render_proposals(branches)
