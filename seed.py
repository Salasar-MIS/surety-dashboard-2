"""Seed the four default branches for FY 2026-27 (runs once on an empty DB)."""
from app.utils.queries import add_branch, ensure_indexes, get_branches

# Default branch names (order matches the source spreadsheet's intent).
DEFAULT_BRANCHES = ["Delhi (NCR)", "Ahmedabad", "Mumbai", "Naveen Aggarwal"]


def seed():
    """Ensure indexes exist and insert default branches only if none exist."""
    ensure_indexes()
    if not get_branches():
        for name in DEFAULT_BRANCHES:
            add_branch(name)


if __name__ == "__main__":
    seed()
    print("Seed complete.")
