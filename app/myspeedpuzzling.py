from urllib.parse import urlencode
from datetime import datetime, timezone
import httpx
from app.config import (
    MSP_AUTHORIZE_URL, MSP_TOKEN_URL, MSP_API_BASE,
    MSP_CLIENT_ID, MSP_CLIENT_SECRET, MSP_SCOPES
)

def build_authorize_url(redirect_uri, state):
    return MSP_AUTHORIZE_URL + "?" + urlencode({
        "client_id": MSP_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(MSP_SCOPES),
        "state": state,
    })

async def exchange_code(code, redirect_uri):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": MSP_CLIENT_ID,
        "client_secret": MSP_CLIENT_SECRET,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(MSP_TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()

async def refresh_access_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": MSP_CLIENT_ID,
        "client_secret": MSP_CLIENT_SECRET,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(MSP_TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()

async def api_get(token, path, params=None):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            MSP_API_BASE + path,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
        )
        response.raise_for_status()
        return response.json()

async def get_profile(token):
    return await api_get(token, "/me")

async def get_statistics(token):
    return await api_get(token, "/me/statistics")

async def get_collections(token):
    return await api_get(token, "/me/collections")

async def get_results(token):
    out = {}
    for mode in ("solo", "duo", "team"):
        try:
            out[mode] = await api_get(token, "/me/results", {"type": mode})
        except Exception as exc:
            out[mode] = {"error": str(exc)}
    return out

async def get_competitions(token, status="all", online=False, country=None):
    params = {
        "status": status,
        "online": str(bool(online)).lower(),
    }
    if country:
        params["country"] = country
    return await api_get(token, "/competitions", params)

async def get_competition(token, competition_id):
    return await api_get(token, f"/competitions/{competition_id}")

def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None

def normalize_competitions(payload):
    rows = payload.get("competitions", []) if isinstance(payload, dict) else []
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append({
            "id": row.get("id"),
            "name": row.get("name"),
            "shortcode": row.get("shortcode"),
            "url": row.get("url"),
            "logo": row.get("logo"),
            "location": row.get("location"),
            "country_code": row.get("country_code"),
            "is_online": row.get("is_online"),
            "date_from": row.get("date_from"),
            "date_to": row.get("date_to"),
            "status": row.get("status"),
            "link": row.get("link"),
            "registration_link": row.get("registration_link"),
            "results_link": row.get("results_link"),
            "raw": row,
        })
    return out

def upcoming_competitions(payload, limit=20):
    now = datetime.now(timezone.utc)
    rows = []
    for row in normalize_competitions(payload):
        end = _parse_dt(row.get("date_to")) or _parse_dt(row.get("date_from"))
        if end and end < now:
            continue
        start = _parse_dt(row.get("date_from")) or datetime.max.replace(tzinfo=timezone.utc)
        row["_sort"] = start
        rows.append(row)
    rows.sort(key=lambda r: r["_sort"])
    for r in rows:
        r.pop("_sort", None)
    return rows[:limit]

PARTICIPATION_KEYS = (
    "is_registered", "registered", "is_participant", "participating",
    "is_attending", "attending", "my_registration", "registration_status",
    "participation_status", "user_registration", "my_participation"
)

def detect_participation(detail):
    if not isinstance(detail, dict):
        return {"detected": False, "reason": "Competition detail is not an object."}

    found = {}
    stack = [("", detail)]
    while stack:
        prefix, obj = stack.pop()
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{prefix}.{key}" if prefix else key
                low = key.lower()
                if low in PARTICIPATION_KEYS or any(k in low for k in ("register", "participat", "attend")):
                    found[path] = value
                if isinstance(value, (dict, list)):
                    stack.append((path, value))
        elif isinstance(obj, list):
            for idx, value in enumerate(obj[:100]):
                if isinstance(value, (dict, list)):
                    stack.append((f"{prefix}[{idx}]", value))

    positive = False
    for value in found.values():
        if value is True:
            positive = True
        elif isinstance(value, str) and value.lower() in (
            "registered", "confirmed", "participating", "attending", "yes", "active"
        ):
            positive = True

    return {
        "detected": positive,
        "signals": found,
        "has_participation_fields": bool(found),
    }
