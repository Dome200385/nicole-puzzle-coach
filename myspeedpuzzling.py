from urllib.parse import urlencode
from datetime import datetime, timezone
import asyncio
import time
import re
import httpx
from app.config import (
    MSP_AUTHORIZE_URL, MSP_TOKEN_URL, MSP_API_BASE,
    MSP_CLIENT_ID, MSP_CLIENT_SECRET, MSP_SCOPES
)

MSP_USER_AGENT = "NicolePuzzleCoach/6.8.1"
_API_CACHE = {}
_API_CACHE_DEFAULT_SECONDS = 5 * 60
_API_403_BLOCKED_UNTIL = 0.0
_API_403_COOLDOWN_SECONDS = 15 * 60

def _cache_key(path, params):
    items=tuple(sorted((str(k),str(v)) for k,v in (params or {}).items()))
    return (str(path),items)

def _cache_ttl(path):
    if path == "/me": return 15 * 60
    if path.startswith("/me/collections"): return 15 * 60
    if path.startswith("/me/results"): return 5 * 60
    if path.startswith("/competitions"): return 15 * 60
    return _API_CACHE_DEFAULT_SECONDS

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
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": MSP_USER_AGENT,
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        response = await client.post(MSP_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "json" not in content_type:
            preview = response.text[:240].replace("\n", " ").replace("\r", " ")
            raise RuntimeError(
                "MySpeedPuzzling token endpoint returned non-JSON "
                f"(HTTP {response.status_code}, content-type={content_type or 'unknown'}, "
                f"location={response.headers.get('location')!r}, body={preview!r})"
            )
        payload = response.json()
        if not isinstance(payload, dict) or not payload.get("access_token"):
            raise RuntimeError("MySpeedPuzzling token response contains no access_token")
        return payload

async def refresh_access_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": MSP_CLIENT_ID,
        "client_secret": MSP_CLIENT_SECRET,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": MSP_USER_AGENT,
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        response = await client.post(MSP_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        content_type = (response.headers.get("content-type") or "").lower()
        if "json" not in content_type:
            preview = response.text[:240].replace("\n", " ").replace("\r", " ")
            raise RuntimeError(
                "MySpeedPuzzling refresh endpoint returned non-JSON "
                f"(HTTP {response.status_code}, content-type={content_type or 'unknown'}, "
                f"location={response.headers.get('location')!r}, body={preview!r})"
            )
        payload = response.json()
        if not isinstance(payload, dict) or not payload.get("access_token"):
            raise RuntimeError("MySpeedPuzzling refresh response contains no access_token")
        return payload

async def api_get(token, path, params=None, cache=True):
    global _API_403_BLOCKED_UNTIL
    now=time.time()
    key=_cache_key(path,params)
    cached=_API_CACHE.get(key)
    if cache and cached and now-cached["ts"] < _cache_ttl(path):
        return cached["data"]
    if now < _API_403_BLOCKED_UNTIL:
        wait=max(1,int(_API_403_BLOCKED_UNTIL-now))
        raise RuntimeError(f"MySpeedPuzzling API 403 cooldown active ({wait}s remaining)")
    auth_scheme = "Token" if str(token).startswith("msp_pat_") else "Bearer"
    headers={"Authorization":f"{auth_scheme} {token}","Accept":"application/json","User-Agent":MSP_USER_AGENT}
    async with httpx.AsyncClient(timeout=30,follow_redirects=False) as client:
        response=await client.get(MSP_API_BASE+path,headers=headers,params=params)
    if response.status_code == 403:
        _API_403_BLOCKED_UNTIL=time.time()+_API_403_COOLDOWN_SECONDS
        try: detail=response.json()
        except Exception: detail={"detail":"403 Forbidden"}
        raise RuntimeError(f"MySpeedPuzzling API 403: {detail}")
    response.raise_for_status()
    ctype=(response.headers.get("content-type") or "").lower()
    if "json" not in ctype:
        raise RuntimeError(f"MySpeedPuzzling API returned non-JSON for {path}: HTTP {response.status_code}, content-type={ctype or 'unknown'}")
    data=response.json()
    if cache: _API_CACHE[key]={"ts":time.time(),"data":data}
    return data

async def get_profile(token):
    return await api_get(token, "/me")

async def get_statistics(token):
    return await api_get(token, "/me/statistics")

async def get_collections(token):
    return await api_get(token, "/me/collections")

async def get_collection_items(token, collection_id):
    return await api_get(token, f"/me/collections/{collection_id}/items")

async def get_library(token):
    """
    Load the user's MySpeedPuzzling collections AND their puzzle items.
    /me/collections alone only returns collection metadata.
    """
    collections_payload = await get_collections(token)
    collections = (
        collections_payload.get("collections", [])
        if isinstance(collections_payload, dict) else []
    )
    enriched = []
    errors = []
    for collection in collections:
        if not isinstance(collection, dict):
            continue
        cid = collection.get("collection_id") or collection.get("id")
        entry = dict(collection)
        if not cid:
            entry["items_payload"] = {"error": "missing_collection_id"}
            enriched.append(entry)
            continue
        try:
            entry["items_payload"] = await get_collection_items(token, cid)
        except Exception as exc:
            entry["items_payload"] = {"error": str(exc)}
            errors.append({"collection_id": cid, "error": str(exc)})
        enriched.append(entry)

    return {
        "collections": enriched,
        "player_id": collections_payload.get("player_id") if isinstance(collections_payload, dict) else None,
        "count": len(enriched),
        "item_fetch_errors": errors,
    }

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
            "slug": row.get("slug"),
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


# --- V6.8.1: confirmed tournaments — official API only ----------------------

_MY_COMP_CACHE={"ts":0.0,"player_id":None,"data":None}
_MY_COMP_CACHE_SECONDS=30*60

async def get_my_confirmed_competitions(token, limit=30, cache=True):
    profile=await get_profile(token)
    player_id=profile.get("id") if isinstance(profile,dict) else None
    now=time.time()
    if cache and _MY_COMP_CACHE["data"] is not None and _MY_COMP_CACHE["player_id"]==player_id and now-_MY_COMP_CACHE["ts"]<_MY_COMP_CACHE_SECONDS:
        out=dict(_MY_COMP_CACHE["data"]); out["cached"]=True; return out
    payload=await get_competitions(token,status="all",online=False)
    candidates=upcoming_competitions(payload,limit=max(1,min(int(limit),60)))
    confirmed=[]; checked=[]
    for comp in candidates:
        cid=comp.get("id")
        if not cid: continue
        try:
            detail=await get_competition(token,cid)
            signal=detect_participation(detail)
        except Exception as exc:
            checked.append({"id":cid,"name":comp.get("name"),"error":str(exc)})
            if "403" in str(exc) or "cooldown" in str(exc).lower(): break
            continue
        checked.append({"id":cid,"name":comp.get("name"),"registered":bool(signal.get("detected")),"participation":signal})
        if signal.get("detected"):
            clean={k:v for k,v in comp.items() if k!="raw"}; clean["registered"]=True; clean["registration_source"]="competition_api"; confirmed.append(clean)
    result={"player_id":player_id,"player_name":profile.get("name") if isinstance(profile,dict) else None,"competitions":confirmed,"count":len(confirmed),"checked":len(checked),"cached":False,"source":"official_api"}
    _MY_COMP_CACHE.update({"ts":now,"player_id":player_id,"data":result})
    return result

# --- V6.8.1: Swiss motivational ranking — API only --------------------------

async def get_swiss_motivation_ranking(token, cache=True):
    return {"title":"Schweizer Motivationsranking","subtitle":"Vorübergehend deaktiviert, bis die benötigten Vergleichsdaten über die offizielle MySpeedPuzzling API verfügbar sind.","players":[],"count":0,"nicole":None,"source":"official_api_only","available":False}

# --- V6.8.1: puzzle insights — official API payload only ---------------------

def _prediction_seconds_from_value(value):
    if value is None: return None
    if isinstance(value,(int,float)): return int(round(value))
    text=str(value).strip().lower()
    if not text: return None
    h=re.search(r'(\d+)\s*h',text); mi=re.search(r'(\d+)\s*min',text); sec=re.search(r'(\d+)\s*s(?:ec)?',text)
    total=(int(h.group(1))*3600 if h else 0)+(int(mi.group(1))*60 if mi else 0)+(int(sec.group(1)) if sec else 0)
    if total: return total
    mm=re.search(r'(?:(\d+):)?(\d{1,2}):(\d{2})',text)
    if mm:
        a,b,c=mm.groups(); return (int(a)*3600 if a else 0)+int(b)*60+int(c)
    return None

def extract_puzzle_insights_from_api_payload(payload):
    if not isinstance(payload,dict): return {"available":False,"source":"official_api_payload"}
    candidates=[payload]
    for key in ("puzzle","statistics","stats","difficulty","prediction","metadata"):
        value=payload.get(key)
        if isinstance(value,dict): candidates.append(value)
    def first(keys):
        for obj in candidates:
            for key in keys:
                if key in obj and obj.get(key) is not None: return obj.get(key)
        return None
    difficulty_label=first(("difficulty_label","difficulty_name","difficulty_level","difficulty"))
    if isinstance(difficulty_label,dict): difficulty_label=difficulty_label.get("label") or difficulty_label.get("name")
    difficulty_percent=first(("difficulty_percent","difficulty_percentage","relative_difficulty_percent"))
    try: difficulty_percent=float(difficulty_percent) if difficulty_percent is not None else None
    except Exception: difficulty_percent=None
    prediction_raw=first(("prediction_seconds","time_prediction_seconds","predicted_time_seconds","prediction","time_prediction","predicted_time"))
    prediction_seconds=_prediction_seconds_from_value(prediction_raw)
    prediction_text=None
    if prediction_raw is not None and not isinstance(prediction_raw,(dict,list)): prediction_text=str(prediction_raw)
    if prediction_seconds and (prediction_text is None or prediction_text.isdigit()):
        mm=prediction_seconds//60; ss=prediction_seconds%60; prediction_text=f"{mm}:{ss:02d}"
    rf=_prediction_seconds_from_value(first(("prediction_range_from_seconds","prediction_min_seconds","predicted_time_min_seconds")))
    rt=_prediction_seconds_from_value(first(("prediction_range_to_seconds","prediction_max_seconds","predicted_time_max_seconds")))
    return {"available":bool(difficulty_label or difficulty_percent is not None or prediction_seconds),"difficulty_label":difficulty_label,"difficulty_percent":difficulty_percent,"prediction_text":prediction_text,"prediction_seconds":prediction_seconds,"prediction_range_from_seconds":rf,"prediction_range_to_seconds":rt,"cached":False,"source":"official_api_payload"}

async def get_puzzle_insights(puzzle_id, api_payload=None):
    if api_payload is not None: return extract_puzzle_insights_from_api_payload(api_payload)
    return {"available":False,"puzzle_id":str(puzzle_id) if puzzle_id else None,"difficulty_label":None,"difficulty_percent":None,"prediction_text":None,"prediction_seconds":None,"prediction_range_from_seconds":None,"prediction_range_to_seconds":None,"cached":False,"source":"official_api_only","reason":"Prediction/difficulty not present in current official API payload."}
