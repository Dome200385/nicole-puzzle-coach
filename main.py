import json,secrets
from fastapi import FastAPI,HTTPException,Request,Depends
from fastapi.responses import RedirectResponse,HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from app.config import APP_BASE_URL,SESSION_SECRET,MSP_CLIENT_ID
from app.database import Base,engine,get_db
from app.models.db_models import OAuthToken,SyncSnapshot,Tournament,TrainingSession
from app.models.schemas import TournamentCreate,TrainingSessionCreate
from app.services.crypto import encrypt_text,decrypt_text
from app.services.myspeedpuzzling import *
from app.services.coach import readiness_score
Base.metadata.create_all(bind=engine)
app=FastAPI(title="Nicole Puzzle Coach API",version="2.0.0")
app.add_middleware(SessionMiddleware,secret_key=SESSION_SECRET)
@app.get("/")
def root(): return {"app":"Nicole Puzzle Coach API","version":"2.0.0","status":"online","oauth_configured":bool(MSP_CLIENT_ID),"database":"persistent","docs":"/docs"}
@app.get("/health")
def health(): return {"status":"ok","version":"2.0.0"}
@app.get("/db/health")
def db_health(db:Session=Depends(get_db)): db.execute(text("SELECT 1")); return {"database":"ok"}
@app.get("/auth/myspeedpuzzling/login")
def login(request:Request):
    if not MSP_CLIENT_ID or MSP_CLIENT_ID=="pending": raise HTTPException(503,"OAuth not approved/configured yet")
    state=secrets.token_urlsafe(24); request.session["oauth_state"]=state
    uri=f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"; return RedirectResponse(build_authorize_url(uri,state))
@app.get("/auth/myspeedpuzzling/callback")
async def callback(request:Request,code:str|None=None,state:str|None=None,db:Session=Depends(get_db)):
    if not code or state!=request.session.get("oauth_state"): raise HTTPException(400,"Invalid OAuth callback")
    token=await exchange_code(code,f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"); payload=encrypt_text(json.dumps(token))
    row=db.query(OAuthToken).filter(OAuthToken.owner_key=="nicole").first()
    if row: row.encrypted_payload=payload
    else: db.add(OAuthToken(owner_key="nicole",encrypted_payload=payload))
    db.commit(); return HTMLResponse("<h2>MySpeedPuzzling verbunden ✅</h2><p><a href='/sync'>Daten synchronisieren</a></p>")
def _token(db):
    row=db.query(OAuthToken).filter(OAuthToken.owner_key=="nicole").first()
    if not row: raise HTTPException(401,"Noch nicht verbunden")
    return json.loads(decrypt_text(row.encrypted_payload))
@app.get("/sync")
async def sync(db:Session=Depends(get_db)):
    t=_token(db).get("access_token")
    if not t: raise HTTPException(401,"Kein Access Token")
    p=await get_profile(t); r=await get_results(t); s=await get_statistics(t); c=await get_collections(t)
    snap=SyncSnapshot(owner_key="nicole",profile_json=json.dumps(p),results_json=json.dumps(r),statistics_json=json.dumps(s),collections_json=json.dumps(c))
    db.add(snap); db.commit(); db.refresh(snap)
    return {"status":"synced","snapshot_id":snap.id,"profile":p,"results":r,"statistics":s,"collections":c}
@app.get("/data/latest")
def latest(db:Session=Depends(get_db)):
    x=db.query(SyncSnapshot).filter(SyncSnapshot.owner_key=="nicole").order_by(SyncSnapshot.id.desc()).first()
    if not x: raise HTTPException(404,"Noch keine Daten")
    return {"snapshot_id":x.id,"synced_at":x.synced_at,"profile":json.loads(x.profile_json),"results":json.loads(x.results_json),"statistics":json.loads(x.statistics_json),"collections":json.loads(x.collections_json)}
@app.post("/tournaments")
def add_t(t:TournamentCreate,db:Session=Depends(get_db)):
    row=Tournament(**t.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id":row.id,**t.model_dump()}
@app.get("/tournaments")
def list_t(db:Session=Depends(get_db)):
    return [{"id":r.id,"name":r.name,"date":r.date,"location":r.location,"mode":r.mode,"manufacturer":r.manufacturer,"piece_count":r.piece_count,"time_limit_minutes":r.time_limit_minutes,"priority":r.priority,"international":r.international,"notes":r.notes} for r in db.query(Tournament).order_by(Tournament.date.asc()).all()]
@app.post("/training-sessions")
def add_s(s:TrainingSessionCreate,db:Session=Depends(get_db)):
    row=TrainingSession(**s.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id":row.id,**s.model_dump()}
@app.get("/training-sessions")
def list_s(db:Session=Depends(get_db)):
    return [{"id":r.id,"date":r.date,"puzzle_name":r.puzzle_name,"puzzle_id":r.puzzle_id,"manufacturer":r.manufacturer,"piece_count":r.piece_count,"mode":r.mode,"duration_seconds":r.duration_seconds,"target_seconds":r.target_seconds,"tournament_id":r.tournament_id,"perceived_difficulty":r.perceived_difficulty,"focus":r.focus,"notes":r.notes} for r in db.query(TrainingSession).order_by(TrainingSession.id.desc()).all()]
@app.get("/coach/readiness/{tournament_id}")
def ready(tournament_id:int,db:Session=Depends(get_db)):
    t=db.query(Tournament).filter(Tournament.id==tournament_id).first()
    if not t: raise HTTPException(404,"Turnier nicht gefunden")
    ss=db.query(TrainingSession).all()
    return {"tournament":{"id":t.id,"name":t.name,"date":t.date},"readiness":readiness_score([{"manufacturer":s.manufacturer,"piece_count":s.piece_count,"mode":s.mode,"duration_seconds":s.duration_seconds,"target_seconds":s.target_seconds} for s in ss],{"manufacturer":t.manufacturer,"piece_count":t.piece_count,"mode":t.mode})}
