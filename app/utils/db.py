"""MongoDB Atlas connection for the Summary app.

Uses the shared cluster but an isolated database (`surety_dashboard_summary`),
so this app's data never mixes with the existing Surety-Dashboard-Claude app.
"""
import os

import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env for local runs; harmless no-op when the file is absent (e.g. cloud).
load_dotenv()

# Default database — separate from the existing app. Override via MONGO_DB.
_DEFAULT_DB = "surety_dashboard_summary"


def _setting(key, default=None):
    """Read a setting from Streamlit secrets first, then the environment."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        # No secrets.toml present (typical in local dev) — fall through to env.
        pass
    return os.environ.get(key, default)


@st.cache_resource
def _client():
    """One pooled MongoClient per server session (cached)."""
    uri = _setting("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI is not set (check .env or Streamlit secrets).")
    # Fail fast (5s) instead of hanging when the cluster is unreachable — a hang
    # on Streamlit Cloud surfaces as a confusing "failed to fetch module" error.
    return MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)


def get_db():
    """Return the isolated database handle for this app."""
    return _client()[_setting("MONGO_DB", _DEFAULT_DB)]
