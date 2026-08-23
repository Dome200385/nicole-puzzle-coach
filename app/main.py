import json
import secrets
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, Response, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_BASE_URL, SESSION_SECRET, MSP_CLIENT_ID
from app.database import get_db
from app.db_models import OAuthToken, SyncSnapshot, Tournament, TrainingSession
from app.schemas import TournamentCreate, TrainingSessionCreate
from app.crypto import encrypt_text, decrypt_text
from app.myspeedpuzzling import (
    build_authorize_url, exchange_code, refresh_access_token,
    get_profile, get_results, get_statistics, get_collections, get_library,
    get_competitions, get_competition, upcoming_competitions,
    detect_participation, get_my_confirmed_competitions, get_swiss_motivation_ranking, get_puzzle_insights,
    enrich_library_with_msp_insights, clear_api_cache, api_cache_status, debug_prediction_fields, extract_puzzle_insights_from_api_payload, get_predicted_time, normalize_predicted_time_response
)
from app.coach import (
    performance_summary, owned_vs_history, tournament_readiness,
    next_puzzle_recommendation, manual_training_overview, tournament_countdown
)
from app.msp_analytics import build_training_summary, normalize_results
from app.wm_coach import build_wm_plan, _median_normalized_performance
from app.ui import dashboard

app = FastAPI(
    title="Nicole Puzzle Coach API",
    version="6.10.8",
    description="Personal speed-puzzling coach and tournament preparation."
)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)


def _legacy_payload_from_db(db):
    """
    Reconstruct a coach payload from pre-snapshot/legacy persisted data.
    This is intentionally best-effort and only uses data already in our DB.
    """
    payload={"profile":{}, "results":[], "statistics":{}, "collections":{}, "confirmed_competitions":[]}

    # Training sessions are the most reliable legacy fallback for recent
    # personal training history. Convert them into normalize_results-compatible
    # rows where possible.
    try:
        sessions=db.query(TrainingSession).order_by(TrainingSession.id.asc()).all()
    except Exception:
        sessions=[]

    legacy_results=[]
    for s in sessions:
        try:
            pieces=getattr(s,"pieces",None) or getattr(s,"piece_count",None)
            seconds=getattr(s,"seconds",None)
            if seconds is None:
                seconds=getattr(s,"time_seconds",None)
            if seconds is None:
                mins=getattr(s,"minutes",None)
                if mins is not None:
                    seconds=int(float(mins)*60)
            name=getattr(s,"puzzle_name",None) or getattr(s,"name",None) or "Manuelles Training"
            manufacturer=getattr(s,"manufacturer",None)
            mode=(getattr(s,"mode",None) or getattr(s,"category",None) or "solo").lower()
            finished=getattr(s,"date",None) or getattr(s,"created_at",None)
            if hasattr(finished,"isoformat"):
                finished=finished.isoformat()
            row={
                "puzzle_name":name,
                "manufacturer":manufacturer,
                "pieces":int(pieces) if pieces else None,
                "seconds":int(seconds) if seconds else None,
                "mode":"solo" if "solo" in mode else mode,
                "finished_at":finished,
                "source":"legacy_training_session",
            }
            if row["seconds"] and row["pieces"]:
                legacy_results.append(row)
        except Exception:
            continue

    payload["results"]=legacy_results

    # Legacy tournament rows can still provide confirmed upcoming competitions.
    try:
        tournaments=db.query(Tournament).order_by(Tournament.id.asc()).all()
    except Exception:
        tournaments=[]

    comps=[]
    for t in tournaments:
        try:
            date_from=getattr(t,"date",None) or getattr(t,"date_from",None)
            date_to=getattr(t,"date_to",None)
            if hasattr(date_from,"isoformat"): date_from=date_from.isoformat()
            if hasattr(date_to,"isoformat"): date_to=date_to.isoformat()
            comps.append({
                "id":str(getattr(t,"id","legacy")),
                "name":getattr(t,"name",None) or getattr(t,"title",None) or "Turnier",
                "date_from":date_from,
                "date_to":date_to,
                "location":getattr(t,"location",None) or getattr(t,"place",None),
                "country_code":getattr(t,"country_code",None),
                "registered":True,
                "registration_source":"legacy_db",
            })
        except Exception:
            continue
    payload["confirmed_competitions"]=comps

    return payload



def _local_confirmed_competitions():
    """
    Stable local fallback for known upcoming competitions.
    Used only when MySpeedPuzzling live competition data is unavailable.
    """
    return [
        {
            "id":"local-wjpc-2026",
            "name":"World Jigsaw Puzzle Championship 2026",
            "slug":"world-jigsaw-puzzle-championship-2026",
            "location":"Valladolid",
            "country_code":"es",
            "is_online":False,
            "date_from":"2026-09-16T09:00:00+02:00",
            "date_to":"2026-09-20T20:00:00+02:00",
            "status":"upcoming",
            "registered":True,
            "registration_source":"local_fallback",
        },
        {
            "id":"local-swiss-2026",
            "name":"Swiss Puzzle Championship 2026",
            "slug":"swiss-puzzle-championship-2026",
            "location":"Winterthur",
            "country_code":"ch",
            "is_online":False,
            "date_from":"2026-10-10T09:00:00+02:00",
            "date_to":"2026-10-11T20:00:00+02:00",
            "status":"upcoming",
            "registered":True,
            "registration_source":"local_fallback",
        },
    ]


def _merge_competitions(primary, fallback):
    """
    Merge without duplicating the same event. Primary wins.
    """
    def _key(c):
        return (
            str(c.get("slug") or "").strip().lower()
            or str(c.get("name") or "").strip().lower()
        )

    out=[]
    seen=set()
    for source in (primary or [], fallback or []):
        for comp in source:
            if not isinstance(comp,dict):
                continue
            key=_key(comp)
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(comp)

    out.sort(key=lambda c: str(c.get("date_from") or "9999"))
    return out


def _best_available_payload(db):
    """
    Prefer latest real SyncSnapshot.
    If none exists, reconstruct from legacy DB rows.
    """
    snap=_latest_snapshot(db)
    if snap:
        return _snapshot_payload(snap), "snapshot", snap.id

    legacy=_legacy_payload_from_db(db)
    if legacy.get("results") or legacy.get("confirmed_competitions"):
        return legacy, "legacy", None

    return None, "none", None

def _latest_snapshot(db):
    return db.query(SyncSnapshot).filter(
        SyncSnapshot.owner_key=="nicole"
    ).order_by(SyncSnapshot.id.desc()).first()

def _snapshot_payload(s):
    statistics=json.loads(s.statistics_json)
    confirmed=[]
    if isinstance(statistics,dict) and statistics.get("_npc_wrapper_version") in (1,2):
        confirmed=statistics.get("confirmed_competitions") or []
        statistics=statistics.get("msp_statistics") or {}
    return {
        "profile": json.loads(s.profile_json),
        "results": json.loads(s.results_json),
        "statistics": statistics,
        "collections": json.loads(s.collections_json),
        "confirmed_competitions": confirmed,
    }

def _training_dicts(rows):
    return [{
        "id":r.id,"date":r.date,"puzzle_name":r.puzzle_name,"puzzle_id":r.puzzle_id,
        "manufacturer":r.manufacturer,"piece_count":r.piece_count,"mode":r.mode,
        "duration_seconds":r.duration_seconds,"target_seconds":r.target_seconds,
        "tournament_id":r.tournament_id,"perceived_difficulty":r.perceived_difficulty,
        "focus":r.focus,"notes":r.notes
    } for r in rows]

def _tournament_dicts(rows):
    return [{
        "id":r.id,"name":r.name,"date":r.date,"location":r.location,"mode":r.mode,
        "manufacturer":r.manufacturer,"piece_count":r.piece_count,
        "time_limit_minutes":r.time_limit_minutes,"priority":r.priority,
        "international":r.international,"notes":r.notes
    } for r in rows]

def _pat_token():
    token=(os.getenv("MSP_PERSONAL_ACCESS_TOKEN") or os.getenv("MSP_PAT") or "").strip()
    return token if token.startswith("msp_pat_") else None

def _load_token_row(db):
    row=db.query(OAuthToken).filter(OAuthToken.owner_key=="nicole").first()
    if not row:
        raise HTTPException(401,"Noch nicht verbunden")
    return row

async def _valid_access_token(db):
    # For this single-user coach, the official MySpeedPuzzling Personal Access
    # Token is preferred. It avoids the OAuth token exchange that can be
    # challenged by CrowdSec on server-to-server requests.
    pat=_pat_token()
    if pat:
        try:
            await get_profile(pat)
            return pat
        except Exception as exc:
            raise HTTPException(401,f"MySpeedPuzzling PAT ungültig oder nicht erreichbar: {exc}")

    row=_load_token_row(db)
    token=json.loads(decrypt_text(row.encrypted_payload))
    access=token.get("access_token")
    if not access:
        raise HTTPException(401,"Kein Access Token")
    try:
        await get_profile(access)
        return access
    except Exception:
        refresh=token.get("refresh_token")
        if not refresh:
            raise HTTPException(401,"Access Token abgelaufen und kein Refresh Token vorhanden")
        try:
            refreshed=await refresh_access_token(refresh)
        except Exception as exc:
            raise HTTPException(401,f"Token konnte nicht erneuert werden: {exc}")
        if not refreshed.get("refresh_token"):
            refreshed["refresh_token"]=refresh
        row.encrypted_payload=encrypt_text(json.dumps(refreshed))
        db.commit()
        return refreshed.get("access_token")

@app.get("/", include_in_schema=False)
def root(): return RedirectResponse("/dashboard")

@app.get("/dashboard", include_in_schema=False)
def dashboard_route(): return dashboard()

@app.get("/api")
def api_root():
    return {"app":"Nicole Puzzle Coach API","version":"6.10.8","status":"online","dashboard":"/dashboard","docs":"/docs"}


def _ensure_readiness_history_table(db):
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS readiness_history (
            day VARCHAR(10) PRIMARY KEY,
            readiness FLOAT NOT NULL,
            form_signal FLOAT NULL,
            consistency FLOAT NULL,
            median_hits INTEGER NULL,
            comparable_count INTEGER NULL
        )
    """))
    db.commit()

def _readiness_history_rows(db, limit=180):
    _ensure_readiness_history_table(db)
    rows=db.execute(text("""
        SELECT day, readiness, form_signal, consistency, median_hits, comparable_count
        FROM readiness_history
        ORDER BY day ASC
    """)).mappings().all()
    rows=list(rows)[-max(1,min(int(limit or 180),365)):]
    return [dict(r) for r in rows]

@app.get("/coach/readiness-history")
def readiness_history(limit:int=180, db:Session=Depends(get_db)):
    return {"items":_readiness_history_rows(db,limit)}

@app.post("/coach/readiness-history/capture")
async def capture_readiness_history(request:Request, db:Session=Depends(get_db)):
    from datetime import datetime
    body=await request.json()
    if body.get("readiness") is None:
        raise HTTPException(status_code=400, detail="readiness required")
    _ensure_readiness_history_table(db)
    day=datetime.utcnow().date().isoformat()

    existing=db.execute(
        text("SELECT day FROM readiness_history WHERE day=:day"),
        {"day":day}
    ).first()

    values={
        "day":day,
        "readiness":float(body.get("readiness")),
        "form_signal":body.get("form_signal"),
        "consistency":body.get("consistency"),
        "median_hits":body.get("median_hits"),
        "comparable_count":body.get("comparable_count"),
    }
    if existing:
        db.execute(text("""
            UPDATE readiness_history
            SET readiness=:readiness,
                form_signal=:form_signal,
                consistency=:consistency,
                median_hits=:median_hits,
                comparable_count=:comparable_count
            WHERE day=:day
        """), values)
    else:
        db.execute(text("""
            INSERT INTO readiness_history
            (day, readiness, form_signal, consistency, median_hits, comparable_count)
            VALUES (:day, :readiness, :form_signal, :consistency, :median_hits, :comparable_count)
        """), values)
    db.commit()
    return {"status":"captured","items":_readiness_history_rows(db,180)}


@app.get("/manifest.webmanifest")
def pwa_manifest():
    return Response(
        content='{"id": "/dashboard", "name": "Nicole Puzzle Coach", "short_name": "Puzzle Coach", "description": "Speed-Puzzling Training & Turniervorbereitung", "start_url": "/dashboard?source=pwa", "scope": "/", "display": "standalone", "background_color": "#f5f7fb", "theme_color": "#f5f7fb", "orientation": "portrait-primary", "icons": [{"src": "/pwa/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"}, {"src": "/pwa/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}, {"src": "/pwa/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}',
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache"},
    )

@app.get("/sw.js")
def pwa_service_worker():
    return Response(content="""const CACHE_NAME='nicole-puzzle-coach-v6108';
const SHELL=['/manifest.webmanifest','/pwa/icon-192.png','/pwa/icon-512.png','/pwa/icon-maskable-512.png'];
self.addEventListener('install',event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(SHELL)).catch(()=>{}));
  self.skipWaiting();
});
self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_NAME).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET') return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin) return;
  if(req.mode==='navigate'){
    event.respondWith(fetch(req).catch(()=>caches.match('/dashboard')));
    return;
  }
  if(url.pathname.startsWith('/pwa/')||url.pathname==='/manifest.webmanifest'){
    event.respondWith(caches.match(req).then(hit=>hit||fetch(req).then(resp=>{
      const copy=resp.clone();
      caches.open(CACHE_NAME).then(cache=>cache.put(req,copy)).catch(()=>{});
      return resp;
    })));
  }
});""", media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"})

@app.get("/pwa/{filename}")
def pwa_asset(filename:str):
    allowed={"icon-192.png","icon-512.png","icon-maskable-512.png"}
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Not Found")
    path=os.path.join(os.path.dirname(os.path.dirname(__file__)),"pwa_assets",filename)
    return FileResponse(path, headers={"Cache-Control": "public, max-age=86400"})

@app.get("/health")
def health(): return {"status":"ok","version":"6.10.8"}

@app.get("/db/health")
def db_health(db:Session=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database":"ok"}

@app.get("/coach/status")
def coach_status(db:Session=Depends(get_db)):
    snap=_latest_snapshot(db)
    legacy=_legacy_payload_from_db(db) if not snap else None
    has_legacy=bool(legacy and (legacy.get("results") or legacy.get("confirmed_competitions")))
    configured=bool(MSP_CLIENT_ID and MSP_CLIENT_ID!="pending")
    pat_configured=bool(_pat_token())
    return {
        "version":"6.10.8",
        "database":"ok",
        "has_myspeedpuzzling_data":snap is not None or has_legacy,
        "latest_snapshot_id":snap.id if snap else None,
        "data_source":"snapshot" if snap else ("legacy" if has_legacy else "none"),
        "myspeedpuzzling_connected":pat_configured or configured,
        "myspeedpuzzling_auth_mode":"pat" if pat_configured else ("oauth" if configured else "none"),
        "pat_configured":pat_configured,
        "oauth_configured":configured
    }

@app.get("/coach/manual-summary")
def manual_summary(db:Session=Depends(get_db)):
    rows=db.query(TrainingSession).order_by(
        TrainingSession.date.asc(),TrainingSession.id.asc()
    ).all()
    return manual_training_overview(_training_dicts(rows))

@app.get("/coach/countdown")
def countdown(db:Session=Depends(get_db)):
    db_rows=_tournament_dicts(db.query(Tournament).all())
    local=[
        {
            "id":c["id"],
            "name":c["name"],
            "date":c["date_from"],
            "location":c.get("location"),
            "mode":"solo",
            "manufacturer":"Ravensburger",
            "piece_count":500,
            "time_limit_minutes":None,
            "priority":"high",
            "international":c.get("country_code")!="ch",
            "notes":"lokaler Fallback",
        }
        for c in _local_confirmed_competitions()
    ]
    merged=_merge_competitions(
        [{"name":x.get("name"),"date_from":x.get("date"),**x} for x in db_rows],
        [{"name":x.get("name"),"date_from":x.get("date"),**x} for x in local],
    )
    rows=[]
    for x in merged:
        y=dict(x)
        y["date"]=x.get("date") or x.get("date_from")
        rows.append(y)
    return tournament_countdown(rows)

@app.get("/coach/local-competitions")
def local_competitions():
    return {
        "source":"local_fallback",
        "competitions":_local_confirmed_competitions()
    }

@app.get("/auth/myspeedpuzzling/login")
def login(request:Request):
    if not MSP_CLIENT_ID or MSP_CLIENT_ID=="pending":
        raise HTTPException(503,"OAuth not approved/configured yet")
    state=secrets.token_urlsafe(24)
    request.session["oauth_state"]=state
    uri=f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"
    return RedirectResponse(build_authorize_url(uri,state))

@app.get("/auth/myspeedpuzzling/callback")
async def callback(request:Request,code:str|None=None,state:str|None=None,db:Session=Depends(get_db)):
    if not code or state!=request.session.get("oauth_state"):
        raise HTTPException(400,"Invalid OAuth callback")
    redirect_uri=f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"
    try:
        token=await exchange_code(code,redirect_uri)
    except Exception as exc:
        # Keep the failure readable in the browser instead of returning a generic 500.
        safe = str(exc).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return HTMLResponse(
            "<h2>MySpeedPuzzling Token-Austausch fehlgeschlagen</h2>"
            f"<p><b>Diagnose:</b> {safe}</p>"
            "<p>Der Login war erfolgreich, aber der Token-Endpunkt hat kein gültiges OAuth-JSON geliefert.</p>"
            "<p><a href='/auth/myspeedpuzzling/login'>Neue Verbindung starten</a></p>",
            status_code=502,
        )
    payload=encrypt_text(json.dumps(token))
    row=db.query(OAuthToken).filter(OAuthToken.owner_key=="nicole").first()
    if row:
        row.encrypted_payload=payload
    else:
        db.add(OAuthToken(owner_key="nicole",encrypted_payload=payload))
    db.commit()
    return HTMLResponse("<h2>MySpeedPuzzling verbunden ✅</h2><p><a href='/sync'>Daten synchronisieren</a></p>")

@app.get("/sync")
async def sync(db:Session=Depends(get_db)):
    previous=_latest_snapshot(db)
    legacy=_legacy_payload_from_db(db) if not previous else None
    previous_rows=[]
    if previous:
        try:
            previous_rows=normalize_results(_snapshot_payload(previous).get("results") or {})
        except Exception:
            previous_rows=[]
    try:
        token=await _valid_access_token(db)

        # Explicit /sync means "refresh now": bypass the short-lived API cache
        # exactly once. All normal dashboard reads remain cached.
        clear_api_cache()

        profile=await get_profile(token, cache=False)
        results=await get_results(token, cache=False)
        statistics=await get_statistics(token, cache=False)
        collections=await get_library(token, cache=False)

        # Normalize MSP-provided prediction/difficulty fields already present
        # in the official library payload. No values are invented.
        collections=enrich_library_with_msp_insights(collections)

        confirmed=[]
        try:
            confirmed_payload=await get_my_confirmed_competitions(token,limit=30,cache=False)
            confirmed=(confirmed_payload or {}).get("competitions",[]) if isinstance(confirmed_payload,dict) else []
        except Exception:
            # Local tournament fallback remains responsible for continuity.
            confirmed=[]

        stored_statistics={
            "_npc_wrapper_version":2,
            "msp_statistics":statistics,
            "confirmed_competitions":confirmed,
            "sync_source":"official_api",
            "api_only":True,
        }
        snap=SyncSnapshot(
            owner_key="nicole",
            profile_json=json.dumps(profile),
            results_json=json.dumps(results),
            statistics_json=json.dumps(stored_statistics),
            collections_json=json.dumps(collections)
        )
        db.add(snap); db.commit(); db.refresh(snap)
        current_rows=normalize_results(results)

        def result_key(row):
            return (
                str(row.get("id") or row.get("result_id") or ""),
                str(row.get("puzzle_id") or ""),
                str(row.get("puzzle_name") or "").strip().lower(),
                str(row.get("finished_at") or ""),
                str(row.get("seconds") or ""),
                str(row.get("mode") or ""),
            )

        previous_keys={result_key(r) for r in previous_rows}
        new_rows=[r for r in current_rows if result_key(r) not in previous_keys]
        new_rows.sort(key=lambda r:str(r.get("finished_at") or ""),reverse=True)

        return {
            "status":"synced",
            "data_mode":"live",
            "api_only":True,
            "snapshot_id":snap.id,
            "results_count":len(current_rows),
            "previous_results_count":len(previous_rows),
            "new_results_count":len(new_rows),
            "new_results":[
                {
                    "puzzle_id":r.get("puzzle_id"),
                    "puzzle_name":r.get("puzzle_name"),
                    "mode":r.get("mode"),
                    "seconds":r.get("seconds"),
                    "finished_at":r.get("finished_at"),
                } for r in new_rows[:20]
            ],
            "dashboard":"/dashboard"
        }
    except Exception as exc:
        if previous:
            return {
                "status":"stale","data_mode":"snapshot","snapshot_id":previous.id,"dashboard":"/dashboard",
                "warning":"MySpeedPuzzling aktuell nicht erreichbar. Letzter erfolgreicher Snapshot bleibt aktiv.",
                "live_error":str(exc)
            }
        if legacy and (legacy.get("results") or legacy.get("confirmed_competitions")):
            return {
                "status":"stale","data_mode":"legacy","snapshot_id":None,"dashboard":"/dashboard",
                "warning":"MySpeedPuzzling aktuell nicht erreichbar. Historische Datenbankdaten werden verwendet.",
                "live_error":str(exc)
            }
        raise

@app.get("/msp/api-test")
async def msp_api_test(db:Session=Depends(get_db)):
    token=_pat_token()
    if not token:
        return {"ok":False,"mode":"pat","reason":"MSP_PERSONAL_ACCESS_TOKEN not configured"}
    try:
        profile=await get_profile(token)
        return {"ok":True,"mode":"pat","api_only":True,"user_agent":"NicolePuzzleCoach/6.8.18","player_id":profile.get("id") if isinstance(profile,dict) else None,"player_name":profile.get("name") if isinstance(profile,dict) else None}
    except Exception as exc:
        return {"ok":False,"mode":"pat","api_only":True,"user_agent":"NicolePuzzleCoach/6.8.18","error":str(exc)}

@app.get("/msp/sync-status")
def msp_sync_status(db:Session=Depends(get_db)):
    snap=_latest_snapshot(db)
    return {
        "version":"6.10.8",
        "snapshot_id":snap.id if snap else None,
        "synced_at":snap.synced_at if snap else None,
        "data_available":snap is not None,
        "api_cache":api_cache_status(),
        "api_only":True,
    }

@app.get("/msp/predicted-time/{puzzle_id}")
async def msp_predicted_time(puzzle_id:str, db:Session=Depends(get_db)):
    token=await _valid_access_token(db)
    try:
        raw=await get_predicted_time(token,puzzle_id,cache=False)
        return {
            "ok":True,
            "api_only":True,
            "endpoint":f"/api/v1/me/puzzles/{puzzle_id}/predicted-time",
            "raw":raw,
            "normalized":normalize_predicted_time_response(raw),
        }
    except Exception as exc:
        return {"ok":False,"api_only":True,"error":str(exc)}

@app.get("/msp/prediction-debug")
def prediction_debug(
    puzzle_id:str|None=None,
    puzzle_name:str|None=None,
    db:Session=Depends(get_db)
):
    """
    Diagnose official API fields present in the latest synced library payload.
    Does not call HTML pages and does not expose tokens.
    """
    snap=_latest_snapshot(db)
    if not snap:
        raise HTTPException(404,"Noch kein Snapshot")
    payload=_snapshot_payload(snap)
    library=payload.get("collections") or {}
    wanted_name=(puzzle_name or "").strip().lower()
    wanted_id=str(puzzle_id).strip() if puzzle_id else None
    matches=[]

    def walk(obj,path="$",depth=0):
        if depth>10 or len(matches)>=20:
            return
        if isinstance(obj,dict):
            oid=obj.get("id") or obj.get("puzzle_id") or obj.get("uuid")
            name=obj.get("name") or obj.get("title") or obj.get("puzzle_name")
            id_match=bool(wanted_id and oid is not None and str(oid)==wanted_id)
            name_match=bool(wanted_name and name and wanted_name in str(name).lower())
            if id_match or name_match:
                matches.append({
                    "path":path,
                    "id":oid,
                    "name":name,
                    "prediction_fields":debug_prediction_fields(obj),
                    "normalized":extract_puzzle_insights_from_api_payload(obj),
                })
            for k,v in obj.items():
                if isinstance(v,(dict,list)):
                    walk(v,f"{path}.{k}",depth+1)
        elif isinstance(obj,list):
            for i,v in enumerate(obj[:1000]):
                if isinstance(v,(dict,list)):
                    walk(v,f"{path}[{i}]",depth+1)

    # If no explicit puzzle is supplied, return first few puzzle-shaped items.
    if not wanted_id and not wanted_name:
        def sample(obj,path="$",depth=0):
            if depth>10 or len(matches)>=5:
                return
            if isinstance(obj,dict):
                name=obj.get("name") or obj.get("title") or obj.get("puzzle_name")
                pieces=obj.get("pieces") or obj.get("piece_count")
                if name and pieces:
                    matches.append({
                        "path":path,
                        "id":obj.get("id") or obj.get("puzzle_id"),
                        "name":name,
                        "prediction_fields":debug_prediction_fields(obj),
                        "normalized":extract_puzzle_insights_from_api_payload(obj),
                    })
                for k,v in obj.items():
                    if isinstance(v,(dict,list)):
                        sample(v,f"{path}.{k}",depth+1)
            elif isinstance(obj,list):
                for i,v in enumerate(obj[:1000]):
                    if isinstance(v,(dict,list)):
                        sample(v,f"{path}[{i}]",depth+1)
        sample(library)
    else:
        walk(library)

    return {
        "snapshot_id":snap.id,
        "query":{"puzzle_id":puzzle_id,"puzzle_name":puzzle_name},
        "matches":matches,
        "count":len(matches),
        "api_only":True,
    }

@app.get("/msp/library")
async def msp_library(db:Session=Depends(get_db)):
    """Return MySpeedPuzzling collections including the actual puzzle items."""
    token=await _valid_access_token(db)
    try:
        return await get_library(token)
    except Exception as exc:
        raise HTTPException(502,f"MySpeedPuzzling library request failed: {exc}")

@app.get("/msp/competitions")
async def msp_competitions(
    status:str="all",
    online:bool=False,
    country:str|None=None,
    db:Session=Depends(get_db)
):
    token=await _valid_access_token(db)
    try:
        return await get_competitions(token,status=status,online=online,country=country)
    except Exception as exc:
        raise HTTPException(502,f"MySpeedPuzzling competitions request failed: {exc}")

@app.get("/msp/competitions/upcoming")
async def msp_upcoming_competitions(
    limit:int=20,
    country:str|None=None,
    db:Session=Depends(get_db)
):
    token=await _valid_access_token(db)
    try:
        payload=await get_competitions(token,status="all",online=False,country=country)
        return {"competitions":upcoming_competitions(payload,limit=max(1,min(limit,100)))}
    except Exception as exc:
        raise HTTPException(502,f"MySpeedPuzzling upcoming competitions request failed: {exc}")

@app.get("/msp/competitions/{competition_id}")
async def msp_competition_detail(competition_id:str,db:Session=Depends(get_db)):
    token=await _valid_access_token(db)
    try:
        return await get_competition(token,competition_id)
    except Exception as exc:
        raise HTTPException(502,f"MySpeedPuzzling competition detail request failed: {exc}")

@app.get("/msp/my-competitions")
async def my_competitions(
    limit:int=30,
    refresh:bool=False,
    db:Session=Depends(get_db)
):
    """
    API-first tournament list with stable local fallback.
    Live API-confirmed registrations win; known local confirmed tournaments are
    retained whenever the API returns none or incomplete participation data.
    """
    api_list=[]
    api_meta={}
    try:
        token=await _valid_access_token(db)
        result=await get_my_confirmed_competitions(
            token,
            limit=max(1,min(limit,60)),
            cache=not refresh
        )
        if isinstance(result,dict):
            api_list=result.get("competitions") or []
            api_meta={k:v for k,v in result.items() if k!="competitions"}
        elif isinstance(result,list):
            api_list=result
    except Exception as exc:
        api_meta={"api_error":str(exc)}

    merged=_merge_competitions(api_list,_local_confirmed_competitions())
    return {
        **api_meta,
        "competitions":merged,
        "count":len(merged),
        "api_count":len(api_list),
        "local_fallback_count":len(_local_confirmed_competitions()),
        "source":"api_plus_local_fallback",
    }

@app.get("/msp/participation-check")
async def participation_check(limit:int=12,db:Session=Depends(get_db)):
    token=await _valid_access_token(db)
    try:
        payload=await get_competitions(token,status="all",online=False)
        upcoming=upcoming_competitions(payload,limit=max(1,min(limit,30)))
        checked=[]
        for comp in upcoming:
            cid=comp.get("id")
            if not cid:
                continue
            try:
                detail=await get_competition(token,cid)
                signal=detect_participation(detail)
            except Exception as exc:
                signal={"detected":False,"error":str(exc)}
            checked.append({
                "id":cid,
                "name":comp.get("name"),
                "date_from":comp.get("date_from"),
                "location":comp.get("location"),
                "participation":signal
            })
        return {
            "checked":checked,
            "note":"If has_participation_fields is false for all competitions, the current Competition API does not expose Nicole's registration status."
        }
    except Exception as exc:
        raise HTTPException(502,f"Participation check failed: {exc}")


def _fmt_seconds(value):
    if value is None:
        return None
    value=int(round(value)); h=value//3600; m=(value%3600)//60; s=value%60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

def _msp_only_prediction(insights):
    """Return only prediction values supplied by MySpeedPuzzling.

    No Nicole/WM goal, form, manufacturer, history or local difficulty factor is
    allowed to alter a concrete puzzle prediction.
    """
    insights=insights or {}
    seconds=insights.get("prediction_seconds")
    text=insights.get("prediction_text")
    range_from=insights.get("prediction_range_from_seconds")
    range_to=insights.get("prediction_range_to_seconds")
    if not text and seconds:
        text=_fmt_seconds(seconds)
    if not (text or seconds):
        return None
    return {
        "seconds":seconds,
        "text":text,
        "range_from_seconds":range_from,
        "range_to_seconds":range_to,
        "range_from":_fmt_seconds(range_from) if range_from else None,
        "range_to":_fmt_seconds(range_to) if range_to else None,
        "source":"myspeedpuzzling",
    }

async def _enrich_plan_puzzle_predictions(plan, token=None):
    """
    Enrich concrete training puzzles with official MSP prediction + median.

    Concrete target policy:
    - Personal expected time comes only from MSP predicted-time.
    - MSP Solo median is shown as an additional benchmark.
    - If Nicole's latest time is slower than the MSP median, the puzzle is
      explicitly marked as needing continued work.
    """
    targets=[]
    for key in ("next_puzzle","simulation_puzzle"):
        p=plan.get(key) or {}
        if p.get("available"):
            targets.append(p)
    for item in plan.get("weekly_plan",[]):
        p=item.get("puzzle") or {}
        if p.get("available"):
            targets.append(p)

    seen={}
    for puzzle in targets:
        pid=puzzle.get("id")
        if not pid:
            continue
        cache_key=str(pid)

        if cache_key not in seen:
            # Preserve statistics/solves already received in the official
            # collection payload, then overlay the dedicated prediction.
            base=puzzle.get("msp_insights") if isinstance(puzzle,dict) else None
            insights=dict(base) if isinstance(base,dict) else {}

            if token:
                try:
                    raw=await get_predicted_time(token,pid)
                    normalized=normalize_predicted_time_response(raw)
                    if normalized.get("available"):
                        # Keep collection statistics/solves while dedicated
                        # predicted-time values take priority.
                        statistics=insights.get("statistics")
                        solves=insights.get("solves")
                        insights.update(normalized)
                        if statistics is not None:
                            insights["statistics"]=statistics
                        if solves is not None:
                            insights["solves"]=solves
                except Exception:
                    pass

            if not insights.get("available"):
                insights=await get_puzzle_insights(pid,api_payload=puzzle)

            seen[cache_key]=insights or {}

        insights=seen[cache_key]
        puzzle["msp_insights"]=insights
        prediction=_msp_only_prediction(insights)

        if prediction:
            puzzle["msp_prediction_seconds"]=prediction["seconds"]
            puzzle["msp_prediction"]=prediction["text"]
            puzzle["msp_prediction_range_from_seconds"]=prediction["range_from_seconds"]
            puzzle["msp_prediction_range_to_seconds"]=prediction["range_to_seconds"]
            puzzle["msp_prediction_range_from"]=prediction["range_from"]
            puzzle["msp_prediction_range_to"]=prediction["range_to"]
            puzzle["prediction_source"]="myspeedpuzzling_predicted_time"
        else:
            puzzle["msp_prediction_seconds"]=None
            puzzle["msp_prediction"]=None
            puzzle["msp_prediction_range_from_seconds"]=None
            puzzle["msp_prediction_range_to_seconds"]=None
            puzzle["msp_prediction_range_from"]=None
            puzzle["msp_prediction_range_to"]=None
            puzzle["prediction_source"]="myspeedpuzzling_unavailable"

        # Official MSP median benchmark.
        stats=insights.get("statistics") or puzzle.get("statistics") or {}
        solves=insights.get("solves") or puzzle.get("solves") or {}
        solo_stats=stats.get("solo") if isinstance(stats,dict) else {}
        solo_solves=solves.get("solo") if isinstance(solves,dict) else {}

        median_seconds=None
        last_seconds=None
        try:
            if isinstance(solo_stats,dict) and solo_stats.get("median_seconds") is not None:
                median_seconds=int(solo_stats.get("median_seconds"))
        except Exception:
            median_seconds=None
        try:
            if isinstance(solo_solves,dict) and solo_solves.get("last_time_seconds") is not None:
                last_seconds=int(solo_solves.get("last_time_seconds"))
        except Exception:
            last_seconds=None

        # Dedicated predicted-time also supplies last_time_seconds.
        if last_seconds is None:
            try:
                if insights.get("last_time_seconds") is not None:
                    last_seconds=int(insights.get("last_time_seconds"))
            except Exception:
                last_seconds=None

        needs_median_work=bool(
            median_seconds is not None and last_seconds is not None
            and median_seconds < last_seconds
        )

        puzzle["msp_median_seconds"]=median_seconds
        puzzle["msp_median"]=_fmt_seconds(median_seconds) if median_seconds is not None else None
        puzzle["msp_last_time_seconds"]=last_seconds
        puzzle["msp_last_time"]=_fmt_seconds(last_seconds) if last_seconds is not None else None
        puzzle["median_training_required"]=needs_median_work
        puzzle["median_gap_seconds"]=(last_seconds-median_seconds) if needs_median_work else None
        puzzle["median_gap"]=_fmt_seconds(last_seconds-median_seconds) if needs_median_work else None

        # Per-puzzle session target: the personal MSP prediction is the primary
        # target; median is an explicit additional benchmark, never a hidden
        # replacement for the personal prediction.
        puzzle["training_target_seconds"]=puzzle.get("msp_prediction_seconds")
        puzzle["training_target"]=puzzle.get("msp_prediction")
        if puzzle.get("msp_prediction"):
            target_text=f"MSP-Ziel {puzzle['msp_prediction']}"
            if puzzle.get("msp_prediction_range_from") and puzzle.get("msp_prediction_range_to"):
                target_text+=f" (Korridor {puzzle['msp_prediction_range_from']}–{puzzle['msp_prediction_range_to']})"
        else:
            target_text="MSP-Ziel derzeit nicht verfügbar"

        if median_seconds is not None:
            target_text+=f" · Median-Benchmark {_fmt_seconds(median_seconds)}"
            if needs_median_work and last_seconds is not None:
                target_text+=f" · weiter trainieren: letzte Zeit {_fmt_seconds(last_seconds)} liegt über Median"
            elif last_seconds is not None and last_seconds <= median_seconds:
                target_text+=f" · Median erreicht"

        puzzle["training_target_text"]=target_text

    return plan


@app.get("/coach/repeat-priority")
def repeat_priority(limit:int=5, db:Session=Depends(get_db)):
    payload,source,snapshot_id=_best_available_payload(db)
    if not payload:return {"available":False,"items":[],"count":0,"message":"Noch keine synchronisierten MySpeedPuzzling-Daten vorhanden."}
    try:
        rows=normalize_results(payload.get("results") or {})
        from app.wm_coach import _extract_library_puzzles,_history_for_puzzle,_days_since_last_solve
        items=[]
        for p in _extract_library_puzzles(payload.get("collections") or {}):
            if not isinstance(p,dict):continue
            try:
                if int(p.get("pieces") or 0)!=500:continue
            except Exception:continue
            hist=_history_for_puzzle(rows,p)
            if not hist:continue
            vals=[]
            for r in hist:
                try:vals.append(int(r.get("seconds")))
                except Exception:pass
            if not vals:continue
            latest=vals[0];previous=vals[1] if len(vals)>1 else None;best=min(vals);solves=len(vals);days=_days_since_last_solve(hist)
            ins=p.get("msp_insights") or {};stats=ins.get("statistics") or p.get("statistics") or {}
            solo=stats.get("solo") if isinstance(stats,dict) else {}
            try:median=int((solo or {}).get("median_seconds")) if (solo or {}).get("median_seconds") is not None else None
            except Exception:median=None
            score=0.0;reasons=[]
            gap=latest-median if median is not None else None
            if gap is not None:
                if gap>0:
                    score+=min(42.0,12.0+(gap/max(1,median))*70.0);reasons.append(f"{_fmt_seconds(gap)} über MSP-Median")
                else:
                    score-=12;reasons.append("MSP-Median bereits erreicht")
            delta=latest-previous if previous is not None else None
            if delta is not None:
                if delta<0:score+=min(22.0,7.0+(-delta)/90.0);reasons.append(f"zuletzt {_fmt_seconds(-delta)} verbessert")
                elif delta>0:score+=4;reasons.append(f"zuletzt {_fmt_seconds(delta)} langsamer")
            if solves==1:score+=18;reasons.append("erst 1 Solo-Lauf")
            elif solves==2:score+=14;reasons.append("erst 2 Solo-Läufe")
            elif solves<=4:score+=8;reasons.append(f"erst {solves} Solo-Läufe")
            elif solves>=8:score-=6;reasons.append(f"bereits {solves} Solo-Läufe")
            if days is not None:
                if days<3:score-=28;reasons.append(f"erst vor {days} Tagen gelöst")
                elif days<7:score-=10;reasons.append(f"vor {days} Tagen gelöst")
                elif days>=30:score+=8;reasons.append(f"seit {days} Tagen nicht gelöst")
                elif days>=14:score+=5;reasons.append(f"seit {days} Tagen nicht gelöst")
            pbgap=latest-best
            if pbgap>0:score+=min(10.0,pbgap/120.0);reasons.append(f"{_fmt_seconds(pbgap)} über eigener Bestzeit")
            score=max(0,min(100,score))
            label="Sehr hoch" if score>=70 else "Hoch" if score>=50 else "Mittel" if score>=30 else "Niedrig"
            items.append({"id":p.get("id"),"name":p.get("name"),"manufacturer":p.get("manufacturer"),"image_url":p.get("image_url"),"score":round(score,1),"label":label,
                          "latest":_fmt_seconds(latest),"previous":_fmt_seconds(previous) if previous is not None else None,"best":_fmt_seconds(best),
                          "solo_solves":solves,"days_since_last_solve":days,"median":_fmt_seconds(median) if median is not None else None,
                          "median_gap":_fmt_seconds(gap) if gap is not None and gap>0 else None,"reasons":reasons[:5]})
        items.sort(key=lambda x:x["score"],reverse=True);items=items[:max(1,min(limit,10))]
        return {"available":bool(items),"items":items,"count":len(items),"snapshot_id":snapshot_id,"data_source":source,
                "message":"Priorisierung bereits gelöster 500er – Trainingsnutzen aus MSP-Daten, keine eigene Zeitprognose."}
    except Exception as exc:return {"available":False,"items":[],"count":0,"message":"Wiederholungs-Priorität derzeit nicht verfügbar.","error":str(exc)}

@app.get("/coach/unsolved-library")
def unsolved_library(db:Session=Depends(get_db)):
    payload,source,snapshot_id=_best_available_payload(db)
    if not payload:return {"available":False,"items":[],"count":0,"message":"Noch keine synchronisierten MySpeedPuzzling-Daten vorhanden."}
    try:
        rows=normalize_results(payload.get("results") or {})
        from app.wm_coach import _extract_library_puzzles,_history_for_puzzle
        items=[]
        for p in _extract_library_puzzles(payload.get("collections") or {}):
            if not isinstance(p,dict):continue
            try:
                if int(p.get("pieces") or 0) != 500:
                    continue
            except (TypeError, ValueError):
                continue
            hist=_history_for_puzzle(rows,p)
            if any(r.get("mode")=="solo" for r in hist):continue
            ins=p.get("msp_insights") or {}
            diff=ins.get("difficulty") if isinstance(ins,dict) else {}
            pred=ins.get("prediction") if isinstance(ins,dict) else {}
            diff=diff if isinstance(diff,dict) else {}
            pred=pred if isinstance(pred,dict) else {}
            ps=pred.get("predicted_seconds") or pred.get("seconds") or p.get("predicted_seconds")
            lo=pred.get("range_low_seconds") or pred.get("rangeLowSeconds") or p.get("prediction_range_low_seconds")
            hi=pred.get("range_high_seconds") or pred.get("rangeHighSeconds") or p.get("prediction_range_high_seconds")
            items.append({"id":p.get("id"),"name":p.get("name"),"manufacturer":p.get("manufacturer"),"pieces":p.get("pieces"),"image_url":p.get("image_url"),
              "difficulty_label":diff.get("label") or diff.get("level") or p.get("difficulty_label"),"difficulty_percent":diff.get("percent") if diff.get("percent") is not None else p.get("difficulty_percent"),
              "prediction":_fmt_seconds(int(ps)) if ps else None,"prediction_low":_fmt_seconds(int(lo)) if lo else None,"prediction_high":_fmt_seconds(int(hi)) if hi else None})
        items.sort(key=lambda p:(int(p.get("pieces") or 99999),str(p.get("name") or "").lower()))
        return {"available":bool(items),"items":items,"count":len(items),"snapshot_id":snapshot_id,"data_source":source,
          "message":f"{len(items)} Puzzle in der Library haben noch kein Solo-Ergebnis." if items else "Alle Puzzle in der Library haben bereits ein Solo-Ergebnis."}
    except Exception as exc:return {"available":False,"items":[],"count":0,"message":"Ungelöste Library derzeit nicht verfügbar.","error":str(exc)}

@app.get("/coach/puzzle-progress")
def puzzle_progress(limit:int=8, db:Session=Depends(get_db)):
    """
    Recent repeated 500-piece Solo puzzles with progress against own history
    and official MSP median. Uses only the latest synced snapshot.
    """
    payload,source,snapshot_id=_best_available_payload(db)
    if not payload:
        return {"available":False,"items":[],"message":"Noch keine synchronisierten Daten vorhanden."}

    try:
        rows=normalize_results(payload.get("results") or {})
        rows=[
            r for r in rows
            if r.get("mode")=="solo"
            and r.get("pieces")==500
            and isinstance(r.get("seconds"),(int,float))
        ]
        from app.wm_coach import _extract_library_puzzles
        library=_extract_library_puzzles(payload.get("collections") or {})
        by_id={str(p.get("id")):p for p in library if p.get("id")}
        by_name={(p.get("name") or "").strip().lower():p for p in library if p.get("name")}

        groups={}
        for r in rows:
            key=str(r.get("puzzle_id") or "").strip() or (r.get("puzzle_name") or "").strip().lower()
            if not key:
                continue
            groups.setdefault(key,[]).append(r)

        def dt_key(r):
            return str(r.get("finished_at") or "")

        items=[]
        for key,hist in groups.items():
            if len(hist)<2:
                continue
            hist=sorted(hist,key=dt_key,reverse=True)
            latest=hist[0]
            previous=hist[1]
            best=min(int(r["seconds"]) for r in hist)
            latest_sec=int(latest["seconds"])
            previous_sec=int(previous["seconds"])
            delta=latest_sec-previous_sec

            puzzle=by_id.get(str(latest.get("puzzle_id") or "")) or by_name.get((latest.get("puzzle_name") or "").strip().lower()) or {}
            insights=puzzle.get("msp_insights") or {}
            stats=insights.get("statistics") or puzzle.get("statistics") or {}
            solo_stats=stats.get("solo") if isinstance(stats,dict) else {}
            median_seconds=None
            try:
                if isinstance(solo_stats,dict) and solo_stats.get("median_seconds") is not None:
                    median_seconds=int(solo_stats.get("median_seconds"))
            except Exception:
                median_seconds=None

            items.append({
                "id":latest.get("puzzle_id") or puzzle.get("id"),
                "name":latest.get("puzzle_name") or puzzle.get("name"),
                "manufacturer":latest.get("manufacturer") or puzzle.get("manufacturer"),
                "image_url":puzzle.get("image_url"),
                "attempts":len(hist),
                "latest_seconds":latest_sec,
                "latest":_fmt_seconds(latest_sec),
                "previous_seconds":previous_sec,
                "previous":_fmt_seconds(previous_sec),
                "best_seconds":best,
                "best":_fmt_seconds(best),
                "delta_seconds":delta,
                "delta":_fmt_seconds(abs(delta)),
                "improved":delta<0,
                "median_seconds":median_seconds,
                "median":_fmt_seconds(median_seconds) if median_seconds is not None else None,
                "vs_median_seconds":(latest_sec-median_seconds) if median_seconds is not None else None,
                "finished_at":latest.get("finished_at"),
            })

        items.sort(key=lambda x:str(x.get("finished_at") or ""),reverse=True)
        items=items[:max(1,min(limit,20))]
        return {
            "available":bool(items),
            "items":items,
            "count":len(items),
            "snapshot_id":snapshot_id,
            "data_source":source,
            "message":"Fortschritt bei zuletzt erneut gelösten 500er-Puzzles."
        }
    except Exception as exc:
        return {"available":False,"items":[],"message":"Puzzle-Fortschritt derzeit nicht verfügbar.","error":str(exc)}

@app.get("/coach/median-gap-focus")
def median_gap_focus(db:Session=Depends(get_db)):
    """
    Independent Top-5 median benchmark endpoint.
    Returns the five 500-piece library puzzles where Nicole's latest solo time
    is furthest above the official MSP solo median. Pure in-memory calculation.
    """
    payload,source,snapshot_id=_best_available_payload(db)
    if not payload:
        return {
            "available":False,
            "items":[],
            "message":"Noch keine synchronisierten MySpeedPuzzling-Daten vorhanden."
        }

    try:
        rows=normalize_results(payload.get("results") or {})
        from app.wm_coach import (
            _extract_library_puzzles,
            _history_for_puzzle,
            _msp_median_training_signal,
        )

        library=_extract_library_puzzles(payload.get("collections") or {})
        candidates=[]

        for puzzle in library:
            if not isinstance(puzzle,dict):
                continue
            try:
                if int(puzzle.get("pieces") or 0) != 500:
                    continue
            except Exception:
                continue

            hist=_history_for_puzzle(rows,puzzle)
            sig=_msp_median_training_signal(puzzle,hist)
            gap=sig.get("gap_seconds")
            if not sig.get("needs_work") or gap is None:
                continue

            candidates.append({
                "id":puzzle.get("id"),
                "name":puzzle.get("name"),
                "manufacturer":puzzle.get("manufacturer"),
                "image_url":puzzle.get("image_url"),
                "median":sig.get("median"),
                "last_time":sig.get("last"),
                "gap":sig.get("gap"),
                "gap_seconds":gap,
            })

        candidates.sort(key=lambda item:item.get("gap_seconds") or 0, reverse=True)
        top5=candidates[:5]

        if top5:
            # Keep legacy first-item fields so older clients remain compatible.
            first=top5[0]
            return {
                "available":True,
                "items":top5,
                "count":len(top5),
                **first,
                "message":"Die fünf größten Abstände zum MSP-Solo-Median – wähle heute das Puzzle, auf das du Lust hast.",
                "snapshot_id":snapshot_id,
                "data_source":source,
            }

        return {
            "available":False,
            "items":[],
            "snapshot_id":snapshot_id,
            "data_source":source,
            "message":"Aktuell kein 500er-Puzzle mit einer letzten Solo-Zeit über dem MSP-Median gefunden."
        }
    except Exception as exc:
        return {
            "available":False,
            "items":[],
            "snapshot_id":snapshot_id,
            "data_source":source,
            "message":"Medianvergleich derzeit nicht verfügbar.",
            "error":str(exc),
        }

@app.get("/coach/wm-plan")
async def wm_plan(exclude_puzzle_ids:str|None=None, db:Session=Depends(get_db)):
    payload,source,snapshot_id=_best_available_payload(db)
    if not payload:
        raise HTTPException(404,"Noch keine verwertbaren Trainingsdaten vorhanden")

    rows=normalize_results(payload["results"])
    excluded=[]
    if exclude_puzzle_ids:
        excluded=[x.strip() for x in exclude_puzzle_ids.split(",") if x.strip()]

    comps=_merge_competitions(
        payload.get("confirmed_competitions") or [],
        _local_confirmed_competitions()
    )
    data_mode="snapshot" if source=="snapshot" else "legacy"
    live_warning=None

    try:
        token=await _valid_access_token(db)
        fresh=await get_my_confirmed_competitions(token,limit=30)
        if fresh:
            fresh_list=fresh.get("competitions",[]) if isinstance(fresh,dict) else fresh
            comps=_merge_competitions(fresh_list,_local_confirmed_competitions())
        data_mode="live"
    except Exception as exc:
        live_warning=f"MySpeedPuzzling Live-Zugriff derzeit nicht möglich: {exc}"

    competition_payload = comps if isinstance(comps,dict) else {"competitions": comps}
    plan=build_wm_plan(
        rows,
        competition_payload,
        library_payload=payload.get("collections") or {},
        target_pieces=500,
        excluded_puzzle_ids=excluded
    )

    # Puzzle enrichment only if a real library is available.
    if payload.get("collections"):
        try:
            token_for_predictions=None
            try:
                token_for_predictions=await _valid_access_token(db)
            except Exception:
                token_for_predictions=None
            plan=await _enrich_plan_puzzle_predictions(plan,token=token_for_predictions)
        except Exception as exc:
            if not live_warning:
                live_warning=f"Live-Puzzle-Insights derzeit nicht möglich: {exc}"

    plan["data_mode"]=data_mode
    plan["data_source"]=source
    plan["snapshot_id"]=snapshot_id
    plan["live_warning"]=live_warning
    plan["resilient"]=True
    plan["legacy_result_count"]=len(rows) if source=="legacy" else None
    return plan


@app.get("/coach/training-feedback")
async def training_feedback(
    puzzle_id:str|None=None,
    puzzle_name:str|None=None,
    started_at:str|None=None,
    target_seconds:int|None=None,
    db:Session=Depends(get_db)
):
    """
    Check current MySpeedPuzzling results for the planned puzzle after a
    locally stored start timestamp and evaluate the time against the target.
    No new DB table is required.
    """
    token=await _valid_access_token(db)
    try:
        results=await get_results(token)
    except Exception as exc:
        raise HTTPException(502,f"Result check failed: {exc}")

    rows=normalize_results(results)
    start_dt=None
    if started_at:
        try:
            from datetime import datetime, timezone
            start_dt=datetime.fromisoformat(started_at.replace("Z","+00:00"))
            if start_dt.tzinfo is None:
                start_dt=start_dt.replace(tzinfo=timezone.utc)
        except Exception:
            start_dt=None

    wanted=(puzzle_name or "").strip().lower()
    matches=[]
    for row in rows:
        if row.get("mode")!="solo":
            continue
        id_match=bool(puzzle_id and row.get("puzzle_id") and str(row.get("puzzle_id"))==str(puzzle_id))
        name_match=bool(wanted and (row.get("puzzle_name") or "").strip().lower()==wanted)
        if not (id_match or name_match):
            continue
        if start_dt:
            try:
                dt=datetime.fromisoformat(str(row.get("finished_at")).replace("Z","+00:00"))
                if dt.tzinfo is None:
                    dt=dt.replace(tzinfo=timezone.utc)
                # MySpeedPuzzling may store day precision only. Accept same-day
                # result even when its normalized timestamp is midnight.
                if dt.date() < start_dt.date():
                    continue
            except Exception:
                pass
        matches.append(row)

    if not matches:
        return {
            "found":False,
            "puzzle_name":puzzle_name,
            "message":"Noch kein passendes neues Solo-Ergebnis gefunden."
        }

    result=matches[0]
    seconds=result.get("seconds")
    delta=None
    status="erfasst"
    label="Ergebnis erfasst"
    if target_seconds and seconds:
        delta=round(seconds-target_seconds)
        ratio=seconds/target_seconds
        if ratio <= 1.00:
            status="ziel_erreicht"; label="✅ Ziel erreicht"
        elif ratio <= 1.03:
            status="knapp"; label="🟡 Ziel knapp verfehlt"
        else:
            status="verfehlt"; label="🔴 Ziel verfehlt"

    return {
        "found":True,
        "status":status,
        "label":label,
        "target_seconds":target_seconds,
        "actual_seconds":seconds,
        "delta_seconds":delta,
        "result":result,
        "message":label,
    }


@app.get("/coach/swiss-ranking")
async def swiss_ranking(db:Session=Depends(get_db)):
    try:
        token=await _valid_access_token(db)
        result=await get_swiss_motivation_ranking(token)
        result["data_mode"]="live"
        return result
    except Exception as exc:
        return {
            "title":"Schweizer Motivationsranking",
            "subtitle":"Live-Vergleich derzeit nicht verfügbar. Der WM-Coach arbeitet weiter mit dem letzten synchronisierten Trainingsstand.",
            "players":[],"count":0,"data_mode":"unavailable","error":str(exc)
        }


@app.get("/coach/wm-simulation-feedback")
async def wm_simulation_feedback(
    puzzle_id:str|None=None,
    puzzle_name:str|None=None,
    started_at:str|None=None,
    target_seconds:int|None=None,
    realistic_goal_seconds:int|None=None,
    stretch_goal_seconds:int|None=None,
    db:Session=Depends(get_db)
):
    """Evaluate a newly completed 500-piece Solo result as a WM simulation."""
    token=await _valid_access_token(db)
    try:
        results=await get_results(token)
    except Exception as exc:
        raise HTTPException(502,f"Result check failed: {exc}")

    rows=normalize_results(results)
    wanted=(puzzle_name or "").strip().lower()
    from datetime import datetime, timezone
    start_dt=None
    if started_at:
        try:
            start_dt=datetime.fromisoformat(started_at.replace("Z","+00:00"))
            if start_dt.tzinfo is None:
                start_dt=start_dt.replace(tzinfo=timezone.utc)
        except Exception:
            start_dt=None

    matches=[]
    for row in rows:
        if row.get("mode")!="solo" or row.get("pieces")!=500:
            continue
        id_match=bool(puzzle_id and row.get("puzzle_id") and str(row.get("puzzle_id"))==str(puzzle_id))
        name_match=bool(wanted and (row.get("puzzle_name") or "").strip().lower()==wanted)
        if not (id_match or name_match):
            continue
        if start_dt:
            try:
                dt=datetime.fromisoformat(str(row.get("finished_at")).replace("Z","+00:00"))
                if dt.tzinfo is None:
                    dt=dt.replace(tzinfo=timezone.utc)
                if dt.date() < start_dt.date():
                    continue
            except Exception:
                pass
        matches.append(row)

    if not matches:
        return {"found":False,"message":"Noch kein neues passendes 500er-Solo-Ergebnis gefunden."}

    result=matches[0]
    actual=result.get("seconds")
    if not actual:
        return {"found":False,"message":"Ergebnis gefunden, aber keine auswertbare Zeit vorhanden."}

    target=target_seconds or realistic_goal_seconds
    if target:
        if actual <= target:
            outcome="ziel_erreicht"; label="✅ Ziel erreicht"
        elif actual <= target*1.03:
            outcome="knapp"; label="🟡 Ziel knapp verfehlt"
        else:
            outcome="verfehlt"; label="🔴 Ziel verfehlt"
    else:
        outcome="erfasst"; label="Ergebnis erfasst"

    anchor=realistic_goal_seconds or target or actual
    score=round(max(0,min(100,100-(actual-anchor)/anchor*120))) if anchor else None
    if stretch_goal_seconds and actual <= stretch_goal_seconds:
        score=100

    return {
        "found":True,
        "status":outcome,
        "label":label,
        "actual_seconds":actual,
        "target_seconds":target,
        "realistic_goal_seconds":realistic_goal_seconds,
        "stretch_goal_seconds":stretch_goal_seconds,
        "delta_target_seconds":actual-target if target else None,
        "delta_realistic_seconds":actual-realistic_goal_seconds if realistic_goal_seconds else None,
        "delta_stretch_seconds":actual-stretch_goal_seconds if stretch_goal_seconds else None,
        "simulation_score":score,
        "result":result,
    }

@app.get("/coach/msp-training-summary")
def msp_training_summary(db:Session=Depends(get_db)):
    """Analyse the latest synchronized real MySpeedPuzzling solve results."""
    s=_latest_snapshot(db)
    if not s:
        raise HTTPException(404,"Noch keine MySpeedPuzzling-Daten synchronisiert")
    payload=_snapshot_payload(s)
    summary=build_training_summary(payload["results"])
    normalized=_median_normalized_performance(
        normalize_results(payload["results"]),
        payload.get("collections") or {},
        target_pieces=500,
        limit=10
    )
    if normalized.get("available"):
        form=normalized.get("form_percent")
        summary["form_percent"]=form
        summary["consistency_score"]=normalized.get("consistency_score")
        summary["median_hit_rate"]=normalized.get("median_hit_rate")
        summary["median_normalized_sample_count"]=normalized.get("sample_count")
        summary["median_normalized_samples"]=normalized.get("samples")
        if form is None:
            recommendation="Weitere median-normalisierte 500er-Ergebnisse sammeln."
        elif form>=5:
            recommendation="Sehr starke aktuelle Form: die letzten Puzzle liegen im Schnitt klar unter ihrem MSP-Median."
        elif form>=0:
            recommendation="Gute aktuelle Form: die letzten Puzzle liegen im Schnitt auf oder unter ihrem MSP-Median."
        elif form>-5:
            recommendation="Solide Form auf schwierigkeitsbereinigter Basis; einzelne Median-Lücken gezielt bearbeiten."
        else:
            recommendation="Aktuell liegen mehrere letzte Versuche über ihrem jeweiligen MSP-Median; gezielte Wiederholungen priorisieren."
        summary["recommendation"]=recommendation
        summary["method"]["form"]="Latest Solo attempt per 500-piece puzzle vs official MSP Solo median; one sample per puzzle."
        summary["method"]["consistency"]="Variation of recent puzzle-specific median-relative performance, not raw solve time."
    return summary

@app.get("/coach/msp-training-live")
async def msp_training_live(db:Session=Depends(get_db)):
    """Fetch current MySpeedPuzzling results and return an immediate analysis."""
    token=await _valid_access_token(db)
    try:
        results=await get_results(token)
        summary=build_training_summary(results)
        snap=_latest_snapshot(db)
        if snap:
            payload=_snapshot_payload(snap)
            normalized=_median_normalized_performance(
                normalize_results(results),
                payload.get("collections") or {},
                target_pieces=500,
                limit=10
            )
            if normalized.get("available"):
                summary["form_percent"]=normalized.get("form_percent")
                summary["consistency_score"]=normalized.get("consistency_score")
                summary["median_hit_rate"]=normalized.get("median_hit_rate")
                summary["median_normalized_sample_count"]=normalized.get("sample_count")
        return summary
    except Exception as exc:
        raise HTTPException(502,f"MySpeedPuzzling training analysis failed: {exc}")

@app.get("/data/latest")
def latest_data(db:Session=Depends(get_db)):
    s=_latest_snapshot(db)
    if not s:
        raise HTTPException(404,"Noch keine Daten synchronisiert")
    return {"snapshot_id":s.id,"synced_at":s.synced_at,**_snapshot_payload(s)}

@app.post("/tournaments")
def create_tournament(t:TournamentCreate,db:Session=Depends(get_db)):
    row=Tournament(**t.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id":row.id,**t.model_dump()}

@app.get("/tournaments")
def list_tournaments(db:Session=Depends(get_db)):
    return _tournament_dicts(db.query(Tournament).order_by(Tournament.date.asc()).all())

@app.post("/training-sessions")
def create_training_session(s:TrainingSessionCreate,db:Session=Depends(get_db)):
    row=TrainingSession(**s.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id":row.id,**s.model_dump()}

@app.get("/training-sessions")
def list_training_sessions(db:Session=Depends(get_db)):
    return _training_dicts(db.query(TrainingSession).order_by(TrainingSession.id.desc()).all())

@app.get("/coach/performance")
def coach_performance(mode:str="solo",pieces:int|None=None,db:Session=Depends(get_db)):
    s=_latest_snapshot(db)
    if not s:
        raise HTTPException(404,"Noch keine MySpeedPuzzling-Daten synchronisiert")
    p=_snapshot_payload(s)
    return performance_summary(p["results"],mode=mode,pieces=pieces)

@app.get("/coach/library")
def coach_library(db:Session=Depends(get_db)):
    s=_latest_snapshot(db)
    if not s:
        raise HTTPException(404,"Noch keine MySpeedPuzzling-Daten synchronisiert")
    p=_snapshot_payload(s)
    return owned_vs_history(p["results"],p["collections"])

@app.get("/coach/readiness/{tournament_id}")
def coach_readiness(tournament_id:int,db:Session=Depends(get_db)):
    t=db.query(Tournament).filter(Tournament.id==tournament_id).first()
    if not t:
        raise HTTPException(404,"Turnier nicht gefunden")
    sessions=_training_dicts(db.query(TrainingSession).all())
    return {
        "tournament":{"id":t.id,"name":t.name,"date":t.date},
        "readiness":tournament_readiness(
            sessions,
            {"mode":t.mode,"manufacturer":t.manufacturer,"piece_count":t.piece_count}
        )
    }

@app.get("/coach/next-puzzle")
def coach_next_puzzle(tournament_id:int|None=None,db:Session=Depends(get_db)):
    s=_latest_snapshot(db)
    if not s:
        raise HTTPException(404,"Noch keine MySpeedPuzzling-Daten synchronisiert")
    p=_snapshot_payload(s)
    td=None
    if tournament_id is not None:
        t=db.query(Tournament).filter(Tournament.id==tournament_id).first()
        if not t:
            raise HTTPException(404,"Turnier nicht gefunden")
        td={"mode":t.mode,"manufacturer":t.manufacturer,"piece_count":t.piece_count}
    return next_puzzle_recommendation(p["results"],p["collections"],tournament=td)
