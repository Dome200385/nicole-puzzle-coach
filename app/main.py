import json
import secrets
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
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
    detect_participation, get_my_confirmed_competitions, get_swiss_motivation_ranking
)
from app.coach import (
    performance_summary, owned_vs_history, tournament_readiness,
    next_puzzle_recommendation, manual_training_overview, tournament_countdown
)
from app.msp_analytics import build_training_summary, normalize_results
from app.wm_coach import build_wm_plan
from app.ui import dashboard

app = FastAPI(
    title="Nicole Puzzle Coach API",
    version="6.7.3",
    description="Personal speed-puzzling coach and tournament preparation."
)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

def _latest_snapshot(db):
    return db.query(SyncSnapshot).filter(
        SyncSnapshot.owner_key=="nicole"
    ).order_by(SyncSnapshot.id.desc()).first()

def _snapshot_payload(s):
    return {
        "profile": json.loads(s.profile_json),
        "results": json.loads(s.results_json),
        "statistics": json.loads(s.statistics_json),
        "collections": json.loads(s.collections_json)
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

def _load_token_row(db):
    row=db.query(OAuthToken).filter(OAuthToken.owner_key=="nicole").first()
    if not row:
        raise HTTPException(401,"Noch nicht verbunden")
    return row

async def _valid_access_token(db):
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
    return {"app":"Nicole Puzzle Coach API","version":"6.7.3","status":"online","dashboard":"/dashboard","docs":"/docs"}

@app.get("/health")
def health(): return {"status":"ok","version":"6.7.3"}

@app.get("/db/health")
def db_health(db:Session=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database":"ok"}

@app.get("/coach/status")
def coach_status(db:Session=Depends(get_db)):
    snap=_latest_snapshot(db)
    configured=bool(MSP_CLIENT_ID and MSP_CLIENT_ID!="pending")
    return {
        "version":"6.7.3",
        "database":"ok",
        "has_myspeedpuzzling_data":snap is not None,
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
    return tournament_countdown(_tournament_dicts(db.query(Tournament).all()))

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
    token=await exchange_code(code,f"{APP_BASE_URL}/auth/myspeedpuzzling/callback")
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
    token=await _valid_access_token(db)
    profile=await get_profile(token)
    results=await get_results(token)
    statistics=await get_statistics(token)
    collections=await get_library(token)
    snap=SyncSnapshot(
        owner_key="nicole",
        profile_json=json.dumps(profile),
        results_json=json.dumps(results),
        statistics_json=json.dumps(statistics),
        collections_json=json.dumps(collections)
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return {"status":"synced","snapshot_id":snap.id,"dashboard":"/dashboard"}

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
    Returns only future competitions where Nicole's unique MySpeedPuzzling
    player ID is present in the event's Connected participants list.
    """
    token=await _valid_access_token(db)
    try:
        return await get_my_confirmed_competitions(
            token,
            limit=max(1,min(limit,60)),
            cache=not refresh
        )
    except Exception as exc:
        raise HTTPException(502,f"My tournament check failed: {exc}")

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

@app.get("/coach/wm-plan")
async def wm_plan(exclude_puzzle_ids:str|None=None, db:Session=Depends(get_db)):
    s=_latest_snapshot(db)
    if not s:
        raise HTTPException(404,"Noch keine MySpeedPuzzling-Daten synchronisiert")
    payload=_snapshot_payload(s)
    rows=normalize_results(payload["results"])
    token=await _valid_access_token(db)
    comps=await get_my_confirmed_competitions(token, limit=30)
    excluded=[]
    if exclude_puzzle_ids:
        excluded=[x.strip() for x in exclude_puzzle_ids.split(",") if x.strip()]
    return build_wm_plan(rows, comps, library_payload=payload["collections"], target_pieces=500, excluded_puzzle_ids=excluded)


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
    token=await _valid_access_token(db)
    try:
        return await get_swiss_motivation_ranking(token)
    except Exception as exc:
        return {
            "title":"Schweizer Motivationsranking",
            "subtitle":"Vergleichsgruppe derzeit nicht verfügbar – kein Einfluss auf den WM-Coach.",
            "players":[],
            "count":0,
            "error":str(exc),
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
    return build_training_summary(payload["results"])

@app.get("/coach/msp-training-live")
async def msp_training_live(db:Session=Depends(get_db)):
    """Fetch current MySpeedPuzzling results and return an immediate analysis."""
    token=await _valid_access_token(db)
    try:
        results=await get_results(token)
        return build_training_summary(results)
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
