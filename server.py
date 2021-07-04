import base64
import json
import hashlib
import hmac
import io
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


load_dotenv()
SALT = os.getenv("SALT")
SECRET_KEY = os.getenv("SECRET_KEY")
DATA_FILENAME = os.getenv("DATA_FILENAME", "data.json")

try:
    with open(DATA_FILENAME, "r") as f:
        users = json.load(f)
except io.UnsupportedOperation:
    users = {}


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


def is_password_correct(username: str, password: str) -> bool:
    password_hash = hashlib.sha256(
        f"{password}{SALT}".encode()
    ).hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash


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
    
    user = users[valid_username]
    return Response(
        f"Привет, {user['name']}. Баланс: {user['balance']}", 
        media_type="text/html",
    )


@app.post("/login")
async def process_login(username: str = Form(...), password: str = Form(...)):
    """"Processes login."""

    # check if username and passwords are correct
    if (not (user := users.get(username)) or 
        not is_password_correct(username, password)):
        return Response(
            json.dumps({
                "success": False,
                "message": "Я вас не знаю",
            }), 
            media_type="application/json",
        )

    response = Response(
        json.dumps({
            "success": True,
            "message": f"Привет, {user['name']}. Баланс: {user['balance']}", 
        }),
        media_type="application/json",
    )
    
    # signing username cookie
    username_signed = (f"{base64.b64encode(username.encode()).decode()}."
                       f"{sign_data(username)}")
    response.set_cookie(key="username", value=username_signed)

    return response


@app.get("/logout")
async def process_logout(request: Request):
    response = Response(
        "Вы разлогинились",
        media_type="text/html", 
    )
    response.delete_cookie(key="username")
    return response
