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

MSP_USER_AGENT = "NicolePuzzleCoach/6.8.6"
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

def clear_api_cache():
    _API_CACHE.clear()

def api_cache_status():
    return {
        "entries": len(_API_CACHE),
        "blocked_until": _API_403_BLOCKED_UNTIL,
        "user_agent": MSP_USER_AGENT,
    }


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

async def get_profile(token, cache=True):
    return await api_get(token, "/me", cache=cache)

async def get_statistics(token, cache=True):
    return await api_get(token, "/me/statistics", cache=cache)

async def get_collections(token, cache=True):
    return await api_get(token, "/me/collections", cache=cache)

async def get_collection_items(token, collection_id, cache=True):
    return await api_get(token, f"/me/collections/{collection_id}/items", cache=cache)

async def get_library(token, cache=True):
    """
    Load the user's MySpeedPuzzling collections AND their puzzle items.
    /me/collections alone only returns collection metadata.
    """
    collections_payload = await get_collections(token, cache=cache)
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
            entry["items_payload"] = await get_collection_items(token, cid, cache=cache)
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

async def get_predicted_time(token, puzzle_id, cache=True):
    """Official MSP personalized prediction endpoint."""
    return await api_get(
        token,
        f"/me/puzzles/{puzzle_id}/predicted-time",
        cache=cache
    )

def normalize_predicted_time_response(payload):
    """Normalize official MSP predicted-time JSON without deriving values."""
    if not isinstance(payload, dict):
        return {"available": False, "source": "myspeedpuzzling_predicted_time"}

    def pick(*keys):
        for key in keys:
            if key in payload and payload.get(key) is not None:
                return payload.get(key)
        return None

    def to_int(value):
        try:
            return int(value) if value is not None else None
        except Exception:
            return None

    def to_float(value):
        try:
            return float(value) if value is not None else None
        except Exception:
            return None

    predicted=to_int(pick("predicted_seconds","predictedSeconds"))
    low=to_int(pick("range_low_seconds","rangeLowSeconds"))
    high=to_int(pick("range_high_seconds","rangeHighSeconds"))

    return {
        "available": predicted is not None,
        "puzzle_id": pick("puzzle_id","puzzleId"),
        "prediction_seconds": predicted,
        "prediction_text": f"{predicted//60}:{predicted%60:02d}" if predicted is not None else None,
        "prediction_range_from_seconds": low,
        "prediction_range_to_seconds": high,
        "is_personalized": pick("is_personalized","isPersonalized"),
        "personal_solve_count": to_int(pick("personal_solve_count","personalSolveCount")),
        "predicted_attempt_number": to_int(pick("predicted_attempt_number","predictedAttemptNumber")),
        "last_time_seconds": to_int(pick("last_time_seconds","lastTimeSeconds")),
        "difficulty_label": pick("difficulty_level","difficultyLevel"),
        "difficulty_percent": to_float(pick("difficulty_score","difficultyScore")),
        "difficulty_confidence": pick("difficulty_confidence","difficultyConfidence"),
        "source":"myspeedpuzzling_predicted_time",
    }

async def get_results(token, cache=True):
    out = {}
    for mode in ("solo", "duo", "team"):
        try:
            out[mode] = await api_get(token, "/me/results", {"type": mode}, cache=cache)
        except Exception as exc:
            out[mode] = {"error": str(exc)}
    return out

async def get_competitions(token, status="all", online=False, country=None, cache=True):
    params = {
        "status": status,
        "online": str(bool(online)).lower(),
    }
    if country:
        params["country"] = country
    return await api_get(token, "/competitions", params, cache=cache)

async def get_competition(token, competition_id, cache=True):
    return await api_get(token, f"/competitions/{competition_id}", cache=cache)

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
    payload=await get_competitions(token,status="all",online=False,cache=cache)
    candidates=upcoming_competitions(payload,limit=max(1,min(int(limit),60)))
    confirmed=[]; checked=[]
    for comp in candidates:
        cid=comp.get("id")
        if not cid: continue
        try:
            detail=await get_competition(token,cid,cache=cache)
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
    """
    Extract MySpeedPuzzling prediction/difficulty values ONLY when they already
    exist in the official API payload.

    V6.8.4 scans nested API objects recursively because collection items can
    wrap puzzle/statistics/prediction data several levels deep.
    """
    if not isinstance(payload,dict):
        return {"available":False,"source":"official_api_payload"}

    # V6.8.5: exact official MySpeedPuzzling Puzzle Insights schema.
    # CollectionItemResponse now contains statistics, difficulty, prediction and solves.
    # Prediction is self-only and members-only on /me/collections/{id}/items.
    prediction_obj = payload.get("prediction")
    difficulty_obj = payload.get("difficulty")
    statistics_obj = payload.get("statistics")
    solves_obj = payload.get("solves")
    if isinstance(prediction_obj, dict) or isinstance(difficulty_obj, dict):
        predicted = prediction_obj.get("predicted_seconds", prediction_obj.get("predictedSeconds")) if isinstance(prediction_obj, dict) else None
        low = prediction_obj.get("range_low_seconds", prediction_obj.get("rangeLowSeconds")) if isinstance(prediction_obj, dict) else None
        high = prediction_obj.get("range_high_seconds", prediction_obj.get("rangeHighSeconds")) if isinstance(prediction_obj, dict) else None
        level = difficulty_obj.get("level") if isinstance(difficulty_obj, dict) else None
        score = difficulty_obj.get("score") if isinstance(difficulty_obj, dict) else None
        try:
            predicted = int(predicted) if predicted is not None else None
        except Exception:
            predicted = None
        try:
            low = int(low) if low is not None else None
        except Exception:
            low = None
        try:
            high = int(high) if high is not None else None
        except Exception:
            high = None
        try:
            score = float(score) if score is not None else None
        except Exception:
            score = None
        prediction_text = None
        if predicted:
            prediction_text = f"{predicted//60}:{predicted%60:02d}"
        return {
            "available": bool(predicted or level or score is not None),
            "difficulty_label": level,
            "difficulty_percent": score,
            "difficulty_confidence": difficulty_obj.get("confidence") if isinstance(difficulty_obj, dict) else None,
            "difficulty_sample_size": difficulty_obj.get("sample_size", difficulty_obj.get("sampleSize")) if isinstance(difficulty_obj, dict) else None,
            "prediction_text": prediction_text,
            "prediction_seconds": predicted,
            "prediction_range_from_seconds": low,
            "prediction_range_to_seconds": high,
            "is_personalized": prediction_obj.get("is_personalized", prediction_obj.get("isPersonalized")) if isinstance(prediction_obj, dict) else None,
            "personal_solve_count": prediction_obj.get("personal_solve_count", prediction_obj.get("personalSolveCount")) if isinstance(prediction_obj, dict) else None,
            "predicted_attempt_number": prediction_obj.get("predicted_attempt_number", prediction_obj.get("predictedAttemptNumber")) if isinstance(prediction_obj, dict) else None,
            "last_time_seconds": prediction_obj.get("last_time_seconds", prediction_obj.get("lastTimeSeconds")) if isinstance(prediction_obj, dict) else None,
            "statistics": statistics_obj if isinstance(statistics_obj, dict) else None,
            "solves": solves_obj if isinstance(solves_obj, dict) else None,
            "cached": False,
            "source": "myspeedpuzzling_official_puzzle_insights",
            "prediction_source_path": "$.prediction" if isinstance(prediction_obj, dict) else None,
            "difficulty_source_path": "$.difficulty" if isinstance(difficulty_obj, dict) else None,
            "range_from_source_path": "$.prediction.range_low_seconds" if isinstance(prediction_obj, dict) else None,
            "range_to_source_path": "$.prediction.range_high_seconds" if isinstance(prediction_obj, dict) else None,
        }

    nodes=[]
    def walk(obj,path="$",depth=0):
        if depth>8:
            return
        if isinstance(obj,dict):
            nodes.append((path,obj))
            for k,v in obj.items():
                if isinstance(v,(dict,list)):
                    walk(v,f"{path}.{k}",depth+1)
        elif isinstance(obj,list):
            for i,v in enumerate(obj[:100]):
                if isinstance(v,(dict,list)):
                    walk(v,f"{path}[{i}]",depth+1)
    walk(payload)

    def first_value(keys):
        wanted={str(k).lower() for k in keys}
        for path,obj in nodes:
            for key,value in obj.items():
                if str(key).lower() in wanted and value is not None:
                    return value,f"{path}.{key}"
        return None,None

    difficulty_raw,difficulty_path=first_value((
        "difficulty_label","difficulty_name","difficulty_level","difficulty",
        "puzzle_difficulty","difficulty_rating","difficulty_score"
    ))
    difficulty_label=None
    difficulty_percent=None
    if isinstance(difficulty_raw,dict):
        difficulty_label=(
            difficulty_raw.get("label") or difficulty_raw.get("name")
            or difficulty_raw.get("level")
        )
        pct=(
            difficulty_raw.get("percent") or difficulty_raw.get("percentage")
            or difficulty_raw.get("percentile")
        )
        try:
            difficulty_percent=float(pct) if pct is not None else None
        except Exception:
            difficulty_percent=None
    elif isinstance(difficulty_raw,str):
        difficulty_label=difficulty_raw

    if difficulty_percent is None:
        pct,pct_path=first_value((
            "difficulty_percent","difficulty_percentage",
            "relative_difficulty_percent","difficulty_percentile"
        ))
        try:
            difficulty_percent=float(pct) if pct is not None else None
        except Exception:
            difficulty_percent=None
    else:
        pct_path=difficulty_path

    prediction_raw,prediction_path=first_value((
        "predictedseconds", "prediction_seconds",
        "personal_prediction_seconds",
        "player_prediction_seconds",
        "my_prediction_seconds",
        "predicted_time_seconds",
        "time_prediction_seconds",
        "estimated_time_seconds",
        "estimated_solve_time_seconds",
        "prediction",
        "personal_prediction",
        "player_prediction",
        "predicted_time",
        "time_prediction",
        "estimated_time",
        "estimated_solve_time",
    ))

    if isinstance(prediction_raw,dict):
        nested=prediction_raw
        prediction_raw=(
            nested.get("seconds")
            or nested.get("prediction_seconds")
            or nested.get("time_seconds")
            or nested.get("value")
            or nested.get("time")
        )

    prediction_seconds=_prediction_seconds_from_value(prediction_raw)
    prediction_text=None
    if prediction_raw is not None and not isinstance(prediction_raw,(dict,list)):
        prediction_text=str(prediction_raw)
    if prediction_seconds and (prediction_text is None or prediction_text.isdigit()):
        mm=prediction_seconds//60
        ss=prediction_seconds%60
        prediction_text=f"{mm}:{ss:02d}"

    rf_raw,rf_path=first_value((
        "rangelowseconds", "prediction_range_from_seconds","prediction_min_seconds",
        "predicted_time_min_seconds","prediction_lower_seconds",
        "estimated_time_min_seconds"
    ))
    rt_raw,rt_path=first_value((
        "rangehighseconds", "prediction_range_to_seconds","prediction_max_seconds",
        "predicted_time_max_seconds","prediction_upper_seconds",
        "estimated_time_max_seconds"
    ))
    rf=_prediction_seconds_from_value(rf_raw)
    rt=_prediction_seconds_from_value(rt_raw)

    available=bool(
        prediction_seconds or prediction_text
        or difficulty_label or difficulty_percent is not None
    )
    return {
        "available":available,
        "difficulty_label":difficulty_label,
        "difficulty_percent":difficulty_percent,
        "prediction_text":prediction_text,
        "prediction_seconds":prediction_seconds,
        "prediction_range_from_seconds":rf,
        "prediction_range_to_seconds":rt,
        "cached":False,
        "source":"official_api_payload",
        "prediction_source_path":prediction_path,
        "difficulty_source_path":difficulty_path or pct_path,
        "range_from_source_path":rf_path,
        "range_to_source_path":rt_path,
    }

def debug_prediction_fields(payload):
    """
    Return only key names/paths that may describe prediction or difficulty.
    Values are included only for scalar fields; no token/account data.
    """
    out=[]
    needles=("predict","difficult","estimate","rating","percentile")
    def walk(obj,path="$",depth=0):
        if depth>8 or len(out)>=200:
            return
        if isinstance(obj,dict):
            for k,v in obj.items():
                p=f"{path}.{k}"
                lk=str(k).lower()
                if any(n in lk for n in needles):
                    out.append({
                        "path":p,
                        "type":type(v).__name__,
                        "value":v if isinstance(v,(str,int,float,bool,type(None))) else None
                    })
                if isinstance(v,(dict,list)):
                    walk(v,p,depth+1)
        elif isinstance(obj,list):
            for i,v in enumerate(obj[:100]):
                if isinstance(v,(dict,list)):
                    walk(v,f"{path}[{i}]",depth+1)
    walk(payload)
    return out

async def get_puzzle_insights(puzzle_id, api_payload=None):
    if api_payload is not None: return extract_puzzle_insights_from_api_payload(api_payload)
    return {"available":False,"puzzle_id":str(puzzle_id) if puzzle_id else None,"difficulty_label":None,"difficulty_percent":None,"prediction_text":None,"prediction_seconds":None,"prediction_range_from_seconds":None,"prediction_range_to_seconds":None,"cached":False,"source":"official_api_only","reason":"Prediction/difficulty not present in current official API payload."}


def enrich_library_with_msp_insights(payload):
    """
    Walk an official MySpeedPuzzling library/collections payload and attach a
    normalized `msp_insights` object to each puzzle dict when prediction or
    difficulty values are already present in the API payload.

    This does not call HTML pages and does not invent any values.
    """
    def walk(obj):
        if isinstance(obj,dict):
            looks_like_puzzle = any(k in obj for k in ("pieces","piece_count","piecesCount")) and any(
                k in obj for k in ("name","title","puzzle_name","puzzleName")
            )
            if looks_like_puzzle:
                insights=extract_puzzle_insights_from_api_payload(obj)
                if insights.get("available"):
                    obj["msp_insights"]=insights
            for value in list(obj.values()):
                walk(value)
        elif isinstance(obj,list):
            for value in obj:
                walk(value)
    walk(payload)
    return payload
