from urllib.parse import urlencode
import httpx
from app.config import *
def build_authorize_url(redirect_uri,state):
    return MSP_AUTHORIZE_URL+"?"+urlencode({"client_id":MSP_CLIENT_ID,"response_type":"code","redirect_uri":redirect_uri,"scope":" ".join(MSP_SCOPES),"state":state})
async def exchange_code(code,redirect_uri):
    d={"grant_type":"authorization_code","code":code,"redirect_uri":redirect_uri,"client_id":MSP_CLIENT_ID,"client_secret":MSP_CLIENT_SECRET}
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.post(MSP_TOKEN_URL,data=d); r.raise_for_status(); return r.json()
async def api_get(t,path,params=None):
    async with httpx.AsyncClient(timeout=30) as c:
        r=await c.get(MSP_API_BASE+path,headers={"Authorization":f"Bearer {t}"},params=params); r.raise_for_status(); return r.json()
async def get_profile(t): return await api_get(t,"/me")
async def get_statistics(t): return await api_get(t,"/me/statistics")
async def get_collections(t): return await api_get(t,"/me/collections")
async def get_results(t):
    out={}
    for mode in ("solo","duo","team"):
        try: out[mode]=await api_get(t,"/me/results",{"type":mode})
        except Exception as e: out[mode]={"error":str(e)}
    return out
