import secrets
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import RedirectResponse,HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import APP_BASE_URL,SESSION_SECRET,MSP_CLIENT_ID
from app.services.myspeedpuzzling import build_authorize_url,exchange_code,get_profile,get_results,get_statistics,get_collections
from app.models.schemas import TournamentCreate

app=FastAPI(title="Nicole Puzzle Coach API",version="1.0.0")
app.add_middleware(SessionMiddleware,secret_key=SESSION_SECRET)
TOKENS={}; DATA={}; TOURNAMENTS=[]

@app.get("/")
def root(): return {"app":"Nicole Puzzle Coach API","status":"online","oauth_configured":bool(MSP_CLIENT_ID),"docs":"/docs"}
@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/auth/myspeedpuzzling/login")
def login(request:Request):
    if not MSP_CLIENT_ID: raise HTTPException(503,"MSP_CLIENT_ID not configured")
    state=secrets.token_urlsafe(24); request.session["oauth_state"]=state
    uri=f"{APP_BASE_URL}/auth/myspeedpuzzling/callback"
    return RedirectResponse(build_authorize_url(uri,state))

@app.get("/auth/myspeedpuzzling/callback")
async def callback(request:Request,code:str|None=None,state:str|None=None):
    if not code or state!=request.session.get("oauth_state"): raise HTTPException(400,"Invalid OAuth callback")
    token=await exchange_code(code,f"{APP_BASE_URL}/auth/myspeedpuzzling/callback")
    TOKENS["nicole"]=token
    return HTMLResponse("<h2>MySpeedPuzzling verbunden ✅</h2><p><a href='/sync'>Daten synchronisieren</a></p>")

@app.get("/sync")
async def sync():
    token=TOKENS.get("nicole",{}).get("access_token")
    if not token: raise HTTPException(401,"Noch nicht verbunden")
    DATA["nicole"]={"profile":await get_profile(token),"results":await get_results(token),"statistics":await get_statistics(token),"collections":await get_collections(token)}
    return {"status":"synced","data":DATA["nicole"]}

@app.get("/data")
def data():
    if "nicole" not in DATA: raise HTTPException(404,"Noch keine Daten synchronisiert")
    return DATA["nicole"]

@app.post("/tournaments")
def add_tournament(t:TournamentCreate):
    row=t.model_dump(); row["id"]=len(TOURNAMENTS)+1; TOURNAMENTS.append(row); return row
@app.get("/tournaments")
def tournaments(): return TOURNAMENTS
