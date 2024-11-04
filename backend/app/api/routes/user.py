import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse

from urllib.parse import urlencode

from app.core.config import settings

router = APIRouter()

@router.post("/login")
async def login(request: Request):
    params = {
        "response_type": "code",
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "scope": "openid",
    }
    auth_url = f"{settings.CILOGON_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    # Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.CILOGON_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.REDIRECT_URI,
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
            },
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch access token")

    token_response = response.json()
    access_token = token_response.get("access_token")

    # Fetch user information using the access token
    user_info_response = await client.get(
        settings.CILOGON_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    
    if user_info_response.status_code != 200:
        raise HTTPException(status_code=user_info_response.status_code, detail="Failed to fetch user info")

    user_info = user_info_response.json()

    # Store user info in session
    request.session["user_info"] = user_info

    return RedirectResponse(url="/")

@router.get("/logout")
async def logout(request: Request):
    # Clear the user info from session
    request.session.pop("user_info", None)
    return RedirectResponse(url="/")