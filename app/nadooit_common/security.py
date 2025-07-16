import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

# This should point to your Django authentication endpoint
AUTH_VALIDATION_URL = "http://localhost:8000/api/v1/nadooit_os/auth/validate-user/"

api_key_header = APIKeyHeader(name="NADOOIT-API-KEY", auto_error=False)

def get_user_code(request: Request):
    user_code = request.headers.get("NADOOIT-USER-CODE")
    if not user_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NADOOIT-USER-CODE header is required",
        )
    return user_code

async def get_current_active_user(request: Request, api_key: str = Depends(api_key_header), user_code: str = Depends(get_user_code)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authenticated: NADOOIT-API-KEY header is missing"
        )

    headers = {
        "NADOOIT-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    data = {"NADOOIT_USER_CODE": user_code}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(AUTH_VALIDATION_URL, headers=headers, json=data)

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("valid") is True:
                    return {"user_code": response_data.get("user_code")}
            
            # If the response is not 200 or not valid, raise an exception
            # Use the error message from the auth service if available
            try:
                detail = response.json().get("error", "Invalid credentials")
            except Exception:
                detail = "Invalid credentials or authentication service error"

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detail,
            )

        except httpx.RequestError as exc:
            # This catches network errors, like the auth service being down
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Authentication service is unavailable: {exc}",
            )

# Example of how to use it in a protected endpoint:
#
# from fastapi import FastAPI, Depends
# from .security import get_current_active_user
#
# app = FastAPI()
#
# @app.get("/users/me")
# async def read_users_me(current_user: dict = Depends(get_current_active_user)):
#     return current_user
