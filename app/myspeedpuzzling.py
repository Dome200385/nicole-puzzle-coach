from urllib.parse import urlencode
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
