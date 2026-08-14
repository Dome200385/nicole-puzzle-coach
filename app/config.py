import os
APP_BASE_URL=os.getenv("APP_BASE_URL","http://localhost:8000").rstrip("/")
MSP_CLIENT_ID=os.getenv("MSP_CLIENT_ID","")
MSP_CLIENT_SECRET=os.getenv("MSP_CLIENT_SECRET","")
SESSION_SECRET=os.getenv("SESSION_SECRET","dev-only")
MSP_BASE_URL="https://myspeedpuzzling.com"
MSP_AUTHORIZE_URL=f"{MSP_BASE_URL}/oauth2/authorize"
MSP_TOKEN_URL=f"{MSP_BASE_URL}/oauth2/token"
MSP_API_BASE=f"{MSP_BASE_URL}/api/v1"
MSP_SCOPES=["profile:read","results:read","statistics:read","collections:read"]
