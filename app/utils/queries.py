"""All read/write operations on the single `branch_summary` collection."""
from bson import ObjectId

from .constants import FINANCIAL_YEAR, MONTHS
from .db import get_db

COLLECTION = "branch_summary"


def _col():
    return get_db()[COLLECTION]


def _zero_monthly():
    """Empty monthly-revenue map (one entry per month, all zero)."""
    return {m: 0 for m in MONTHS}


def _zero_proposals():
    """Empty proposal-conversion map (proposals/converted per month)."""
    return {m: {"proposals": 0, "converted": 0} for m in MONTHS}


def ensure_indexes():
    """Create indexes (idempotent). Unique name per FY prevents duplicates."""
    _col().create_index([("financial_year", 1), ("name", 1)], unique=True)
    _col().create_index([("financial_year", 1), ("display_order", 1)])


def get_branches():
    """All branches for the fixed FY, ordered for display."""
    return list(
        _col().find({"financial_year": FINANCIAL_YEAR}).sort("display_order", 1)
    )


def _next_order():
    """Next display_order value (append new branches at the end)."""
    last = _col().find_one(
        {"financial_year": FINANCIAL_YEAR}, sort=[("display_order", -1)]
    )
    return (last["display_order"] + 1) if last else 1


def add_branch(name, monthly=None):
    """Insert a new branch with all sections zeroed; return its _id."""
    doc = {
        "financial_year": FINANCIAL_YEAR,
        "name": name.strip(),
        "display_order": _next_order(),
        "monthly_revenue": monthly or _zero_monthly(),
        "target": 0,
        "achievement": 0,
        "proposal_conversions": _zero_proposals(),
    }
    return _col().insert_one(doc).inserted_id


def rename_branch(branch_id, name):
    _col().update_one({"_id": ObjectId(branch_id)}, {"$set": {"name": name.strip()}})


def delete_branch(branch_id):
    """Hard delete — permanently removes the branch from all sections."""
    _col().delete_one({"_id": ObjectId(branch_id)})


def set_monthly_revenue(branch_id, monthly):
    """monthly: dict of month -> number (Section 1)."""
    _col().update_one(
        {"_id": ObjectId(branch_id)}, {"$set": {"monthly_revenue": monthly}}
    )


def set_target_achievement(branch_id, target, achievement):
    """Both values are entered manually (Section 2)."""
    _col().update_one(
        {"_id": ObjectId(branch_id)},
        {"$set": {"target": target, "achievement": achievement}},
    )


def set_proposals(branch_id, proposals):
    """proposals: dict of month -> {'proposals': int, 'converted': int} (Section 3)."""
    _col().update_one(
        {"_id": ObjectId(branch_id)}, {"$set": {"proposal_conversions": proposals}}
    )
