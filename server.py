import base64
import hashlib
import hmac
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import Response


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

users = {
    "balancy": {
        "name": "Павел",
        "password": "balancy",
        "balance": 100_000,
    },
    "random_user": {
        "name": "Василий",
        "password": "random_user",
        "balance": 200_000,
    },
}

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def sign_data(data: str) -> str:
    """Returns signed data."""
    
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest().upper()


def fetch_user_greetings(user):
    return Response(
        f"Привет, {user['name']}. Баланс: {user['balance']}", 
        media_type="text/html",
    )


def fetch_template(request):
    return templates.TemplateResponse(
        "login.html", 
        {"request": request}
    )


def extract_username_from_signed_string(username_signed: str) -> Optional[str]:
    """Returns back username from signed username."""

    if username_signed.count(".") != 1:
        return
    
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


@app.get("/", response_class=HTMLResponse)
async def index_page(
    request: Request, 
    username: Optional[str] = Cookie(default=None),
):
    if not username:
        return fetch_template(request)
    
    valid_username = extract_username_from_signed_string(username)
    if not valid_username:
        response = fetch_template(request)
        response.delete_cookie(key="username")
        return response
    
    return fetch_user_greetings(users[valid_username])


@app.post("/login")
async def process_login(username: str = Form(...), password: str = Form(...)):
    """"Processes login."""

    # check if username and passwords are correct
    user = users.get(username)
    if not (user := users.get(username)) or user["password"] != password:
        return Response("Я вас не знаю", media_type="text/html")

    response = fetch_user_greetings(user)
    
    # signing username cookie
    username_signed = (f"{base64.b64encode(username.encode()).decode()}."
                       f"{sign_data(username)}")
    response.set_cookie(key="username", value=username_signed)

    return response
