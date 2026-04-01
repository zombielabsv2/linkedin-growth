"""
Cloud Store — Supabase backend via direct httpx REST calls.
Uses the linkedin_content_store table with simple key-value storage.
No auth.users FK — this is a single-user tool using service key.
Falls back gracefully to local-only if Supabase is not configured.

Table: linkedin_content_store (id UUID PK, key TEXT UNIQUE, data JSONB, updated_at)
Run setup_supabase.sql to create the table before first use.
"""

import json
import os
from datetime import datetime

import httpx


_url = None
_key = None
_available = None

_TABLE = "linkedin_content_store"
_TIMEOUT = httpx.Timeout(connect=5.0, read=15.0, write=15.0, pool=5.0)


def _get_config():
    """Read Supabase URL and service key. Returns (url, key) or None.

    Checks in order: env vars, streamlit secrets, local secrets.toml file.
    """
    global _url, _key, _available

    if _available is not None:
        return (_url, _key) if _available else None

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")

    # Try streamlit secrets (works when app is running)
    if not url:
        try:
            import streamlit as st
            url = st.secrets.get("SUPABASE_URL", "")
            key = st.secrets.get("SUPABASE_KEY", "")
        except Exception:
            pass

    # Fallback: read secrets.toml directly (for CLI scripts)
    if not url:
        try:
            from pathlib import Path
            secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
            if secrets_path.exists():
                import re as _re
                text = secrets_path.read_text(encoding="utf-8")
                m_url = _re.search(r'SUPABASE_URL\s*=\s*"([^"]+)"', text)
                m_key = _re.search(r'SUPABASE_KEY\s*=\s*"([^"]+)"', text)
                if m_url and m_key:
                    url = m_url.group(1)
                    key = m_key.group(1)
        except Exception:
            pass

    if not url or not key:
        _available = False
        return None

    _url = url.rstrip("/")
    _key = key
    _available = True
    return (_url, _key)


def _rest_headers():
    """Build headers for Supabase REST API (PostgREST)."""
    config = _get_config()
    if not config:
        return {}
    _, key = config
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def is_cloud_available():
    """Check if Supabase is configured."""
    return _get_config() is not None


def cloud_put(key, data):
    """Store a JSON-serializable value in the cloud, keyed by string.
    Upserts on key (UNIQUE constraint).
    """
    config = _get_config()
    if not config:
        return False
    url, _ = config
    try:
        record = {
            "key": key,
            "data": json.dumps(data, ensure_ascii=False),
            "updated_at": datetime.now().isoformat(),
        }
        resp = httpx.post(
            f"{url}/rest/v1/{_TABLE}?on_conflict=key",
            headers={**_rest_headers(), "Prefer": "resolution=merge-duplicates,return=representation"},
            json=record,
            timeout=_TIMEOUT,
        )
        if resp.status_code >= 400:
            print(f"[cloud_store] cloud_put HTTP {resp.status_code} for key={key}: {resp.text[:200]}")
        return resp.status_code < 400
    except Exception as e:
        print(f"[cloud_store] cloud_put error for key={key}: {e}")
        return False


def cloud_get(key):
    """Retrieve a value from the cloud by key. Returns parsed JSON or None."""
    config = _get_config()
    if not config:
        return None
    url, _ = config
    try:
        resp = httpx.get(
            f"{url}/rest/v1/{_TABLE}",
            params={
                "key": f"eq.{key}",
                "select": "data",
            },
            headers=_rest_headers(),
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            rows = resp.json()
            if rows:
                return json.loads(rows[0]["data"])
        return None
    except Exception as e:
        print(f"[cloud_store] cloud_get error for key={key}: {e}")
        return None


def cloud_list(prefix):
    """List all keys matching a prefix."""
    config = _get_config()
    if not config:
        return []
    url, _ = config
    try:
        resp = httpx.get(
            f"{url}/rest/v1/{_TABLE}",
            params={
                "key": f"like.{prefix}%",
                "select": "key",
                "order": "key",
            },
            headers=_rest_headers(),
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            return [r["key"] for r in resp.json()]
        return []
    except Exception as e:
        print(f"[cloud_store] cloud_list error for prefix={prefix}: {e}")
        return []


def cloud_list_with_data(prefix):
    """List all keys matching a prefix and return key + data pairs."""
    config = _get_config()
    if not config:
        return []
    url, _ = config
    try:
        resp = httpx.get(
            f"{url}/rest/v1/{_TABLE}",
            params={
                "key": f"like.{prefix}%",
                "select": "key,data,updated_at",
                "order": "key",
            },
            headers=_rest_headers(),
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            results = []
            for r in resp.json():
                try:
                    results.append({
                        "key": r["key"],
                        "data": json.loads(r["data"]),
                        "updated_at": r.get("updated_at", ""),
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
            return results
        return []
    except Exception as e:
        print(f"[cloud_store] cloud_list_with_data error for prefix={prefix}: {e}")
        return []


def cloud_delete(key):
    """Delete a key from the cloud."""
    config = _get_config()
    if not config:
        return False
    url, _ = config
    try:
        resp = httpx.delete(
            f"{url}/rest/v1/{_TABLE}",
            params={"key": f"eq.{key}"},
            headers=_rest_headers(),
            timeout=_TIMEOUT,
        )
        return resp.status_code < 400
    except Exception as e:
        print(f"[cloud_store] cloud_delete error for key={key}: {e}")
        return False
