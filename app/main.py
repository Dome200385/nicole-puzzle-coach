import json
import secrets
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_BASE_URL, SESSION_SECRET, MSP_CLIENT_ID
from app.database import Base, engine, get_db
from app.db_models import OAuthToken, SyncSnapshot, Tournament, TrainingSession
from app.schemas import TournamentCreate, TrainingSessionCreate
from app.crypto import encrypt_text, decrypt_text
from app.myspeedpuzzling import (
    build_authorize_url, exchange_code, get_profile, get_results,
    get_statistics, get_collections
)
from app.coach import (
    performance_summary, owned_vs_history,
    tournament_readiness, next_puzzle_recommendation
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nicole Puzzle Coach API",
    version="3.0.0",
    description="Personal speed-puzzling coach and tournament preparation backend."
)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

def _latest_snapshot(db: Session):
    return (
        db.query(SyncSnapshot)
        .filter(SyncSnapshot.owner_key == "nicole")
        .order_by(SyncSnapshot.id.desc())
        .first()
    )

def _snapshot_payload(snapshot):
    return {
        "profile": json.loads(snapshot.profile_json),
        "results": json.loads(snapshot.results_json),
        "statistics": json.loads(snapshot.statistics_json),
        "collections": json.loads(snapshot.collections_json),
    }

@app.get("/")
def root():
    return {
        "app": "Nicole Puzzle Coach API",
        "version": "3.0.0",
        "status": "online",
        "oauth_configured": bool(MSP_CLIENT_ID and MSP_CLIENT_ID != "pending"),
        "database": "persistent",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}

@app.get("/db/health")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}

@app.get("/coach/status")
def coach_status(db: Session = Depends(get_db)):
    snapshot = _latest_snapshot(db)
    return {
        "version": "3.0.0",
        "database": "ok",
        "has_myspeedpuzzling_data": snapshot is not None,
        "oauth_configured": bool(MSP_CLIENT_ID and MSP_CLIENT_ID != "pending"),
        "next_step": (
            "Analyse verfügbar" if snapshot else
            "Auf MySpeedPuzzling OAuth-Freigabe warten und danach /auth/myspeedpuzzling/login öffnen."
        )
    }

@app.get("/auth/myspeedpuzzling/login")
def login(request: Request):
    if not MSP_CLIENT_ID or MSP_CLIENT_ID == "pending":
        raise HTTPException(503, "OAuth not approved/configured yet")
    state = secrets.token_urlsafe(24)
    request.session["oauth_state"] = state
    uri = f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"
    return RedirectResponse(build_authorize_url(uri, state))

@app.get("/auth/myspeedpuzzling/callback")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
):
    if not code or state != request.session.get("oauth_state"):
        raise HTTPException(400, "Invalid OAuth callback")

    token = await exchange_code(
        code,
        f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"
    )
    payload = encrypt_text(json.dumps(token))
    row = db.query(OAuthToken).filter(OAuthToken.owner_key == "nicole").first()

    if row:
        row.encrypted_payload = payload
    else:
        db.add(OAuthToken(owner_key="nicole", encrypted_payload=payload))

    db.commit()
    return HTMLResponse(
        "<h2>MySpeedPuzzling verbunden ✅</h2>"
        "<p><a href='/sync'>Daten synchronisieren</a></p>"
    )

def _load_token(db: Session):
    row = db.query(OAuthToken).filter(OAuthToken.owner_key == "nicole").first()
    if not row:
        raise HTTPException(401, "Noch nicht verbunden")
    return json.loads(decrypt_text(row.encrypted_payload))

@app.get("/sync")
async def sync(db: Session = Depends(get_db)):
    token = _load_token(db)
    access_token = token.get("access_token")
    if not access_token:
        raise HTTPException(401, "Kein Access Token")

    profile = await get_profile(access_token)
    results = await get_results(access_token)
    statistics = await get_statistics(access_token)
    collections = await get_collections(access_token)

    snapshot = SyncSnapshot(
        owner_key="nicole",
        profile_json=json.dumps(profile),
        results_json=json.dumps(results),
        statistics_json=json.dumps(statistics),
        collections_json=json.dumps(collections),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "status": "synced",
        "snapshot_id": snapshot.id,
        "coach_links": {
            "performance": "/coach/performance?mode=solo&pieces=500",
            "library": "/coach/library",
            "next_puzzle": "/coach/next-puzzle",
        }
    }

@app.get("/data/latest")
def latest_data(db: Session = Depends(get_db)):
    snapshot = _latest_snapshot(db)
    if not snapshot:
        raise HTTPException(404, "Noch keine Daten synchronisiert")
    return {
        "snapshot_id": snapshot.id,
        "synced_at": snapshot.synced_at,
        **_snapshot_payload(snapshot),
    }

@app.post("/tournaments")
def create_tournament(t: TournamentCreate, db: Session = Depends(get_db)):
    row = Tournament(**t.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, **t.model_dump()}

@app.get("/tournaments")
def list_tournaments(db: Session = Depends(get_db)):
    rows = db.query(Tournament).order_by(Tournament.date.asc()).all()
    return [
        {
            "id": r.id, "name": r.name, "date": r.date,
            "location": r.location, "mode": r.mode,
            "manufacturer": r.manufacturer, "piece_count": r.piece_count,
            "time_limit_minutes": r.time_limit_minutes,
            "priority": r.priority, "international": r.international,
            "notes": r.notes,
        }
        for r in rows
    ]

@app.post("/training-sessions")
def create_training_session(s: TrainingSessionCreate, db: Session = Depends(get_db)):
    row = TrainingSession(**s.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, **s.model_dump()}

@app.get("/training-sessions")
def list_training_sessions(db: Session = Depends(get_db)):
    rows = db.query(TrainingSession).order_by(TrainingSession.id.desc()).all()
    return [
        {
            "id": r.id, "date": r.date, "puzzle_name": r.puzzle_name,
            "puzzle_id": r.puzzle_id, "manufacturer": r.manufacturer,
            "piece_count": r.piece_count, "mode": r.mode,
            "duration_seconds": r.duration_seconds,
            "target_seconds": r.target_seconds,
            "tournament_id": r.tournament_id,
            "perceived_difficulty": r.perceived_difficulty,
            "focus": r.focus, "notes": r.notes,
        }
        for r in rows
    ]

@app.get("/coach/performance")
def coach_performance(
    mode: str = "solo",
    pieces: int | None = None,
    db: Session = Depends(get_db),
):
    snapshot = _latest_snapshot(db)
    if not snapshot:
        raise HTTPException(404, "Noch keine MySpeedPuzzling-Daten synchronisiert")
    payload = _snapshot_payload(snapshot)
    return performance_summary(payload["results"], mode=mode, pieces=pieces)

@app.get("/coach/library")
def coach_library(db: Session = Depends(get_db)):
    snapshot = _latest_snapshot(db)
    if not snapshot:
        raise HTTPException(404, "Noch keine MySpeedPuzzling-Daten synchronisiert")
    payload = _snapshot_payload(snapshot)
    return owned_vs_history(payload["results"], payload["collections"])

@app.get("/coach/readiness/{tournament_id}")
def coach_readiness(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(404, "Turnier nicht gefunden")

    sessions = db.query(TrainingSession).all()
    tournament_dict = {
        "mode": tournament.mode,
        "manufacturer": tournament.manufacturer,
        "piece_count": tournament.piece_count,
    }
    session_dicts = [
        {
            "mode": s.mode,
            "manufacturer": s.manufacturer,
            "piece_count": s.piece_count,
            "duration_seconds": s.duration_seconds,
            "target_seconds": s.target_seconds,
        }
        for s in sessions
    ]

    return {
        "tournament": {
            "id": tournament.id,
            "name": tournament.name,
            "date": tournament.date,
        },
        "readiness": tournament_readiness(session_dicts, tournament_dict),
    }

@app.get("/coach/next-puzzle")
def coach_next_puzzle(
    tournament_id: int | None = None,
    db: Session = Depends(get_db),
):
    snapshot = _latest_snapshot(db)
    if not snapshot:
        raise HTTPException(404, "Noch keine MySpeedPuzzling-Daten synchronisiert")
    payload = _snapshot_payload(snapshot)

    tournament_dict = None
    if tournament_id is not None:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        if not tournament:
            raise HTTPException(404, "Turnier nicht gefunden")
        tournament_dict = {
            "mode": tournament.mode,
            "manufacturer": tournament.manufacturer,
            "piece_count": tournament.piece_count,
        }

    return next_puzzle_recommendation(
        payload["results"],
        payload["collections"],
        tournament=tournament_dict,
    )
