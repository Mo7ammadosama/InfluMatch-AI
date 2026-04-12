"""Async HTTP client for InfluMatch API"""
import httpx
import streamlit as st

API_BASE = "http://localhost:8000"

def get_headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}

def api_get(path: str, params: dict = None):
    try:
        r = httpx.get(f"{API_BASE}{path}", headers=get_headers(), params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_post(path: str, data: dict = None, json: dict = None):
    try:
        r = httpx.post(f"{API_BASE}{path}", headers=get_headers(), data=data, json=json, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}

def api_put(path: str, json: dict = None):
    try:
        r = httpx.put(f"{API_BASE}{path}", headers=get_headers(), json=json, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}

def api_patch(path: str, json: dict = None, params: dict = None):
    try:
        r = httpx.patch(f"{API_BASE}{path}", headers=get_headers(),
                        json=json, params=params, timeout=10)
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}

def api_delete(path: str):
    try:
        r = httpx.delete(f"{API_BASE}{path}", headers=get_headers(), timeout=10)
        return r.status_code, r.json() if r.text else {}
    except Exception as e:
        return 500, {"detail": str(e)}

def check_api_health():
    try:
        r = httpx.get(f"{API_BASE}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False
