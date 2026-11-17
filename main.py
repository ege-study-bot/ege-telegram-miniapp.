
import os
import json
import hmac
import hashlib
import sqlite3
from urllib.parse import parse_qsl

import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
ADMIN_SECRET = os.environ["ADMIN_SECRET"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ege-study-bot.github.io"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def db():
    con = sqlite3.connect("access.db")
    con.row_factory = sqlite3.Row
    return con

with db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)

def verify_init_data(init_data):
    data = dict(parse_qsl(init_data))
    received_hash = data.pop("hash", None)

    if not received_hash:
        return None

    secret = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    calculated = hmac.new(
        secret,
        check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated, received_hash):
        return None

    try:
        return json.loads(data["user"])
    except Exception:
        return None

async def telegram_message(chat_id, message):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )

class AccessRequest(BaseModel):
    init_data: str

class Decision(BaseModel):
    user_id: int
    status: str

@app.get("/")
def home():
    return {"status": "server is running"}

@app.post("/access")
async def access(request: AccessRequest):
    user = verify_init_data(request.init_data)

    if not user:
        raise HTTPException(401, "Invalid Telegram session")

    user_id = int(user["id"])
    username = user.get("username", "без username")

    with db() as con:
        row = con.execute(
            "SELECT status FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()

        if row:
            status = row["status"]
        else:
            status = "pending"
            con.execute(
                "INSERT INTO users (user_id, username, status) VALUES (?, ?, ?)",
                (user_id, username, status)
            )

            await telegram_message(
                ADMIN_ID,
                f"Новая заявка в ЕГЭ-приложение\n"
                f"Ученик: @{username}\n"
                f"Telegram ID: {user_id}\n"
                f"Одобрить или отклонить можно в панели администратора."
            )

    return {"status": status}

def check_admin(secret):
    if not secret or not hmac.compare_digest(secret, ADMIN_SECRET):
        raise HTTPException(403, "Access denied")

@app.get("/admin/requests")
def requests_list(x_admin_secret: str = Header(None)):
    check_admin(x_admin_secret)

    with db() as con:
        rows = con.execute(
            "SELECT user_id, username, status FROM users ORDER BY user_id DESC"
        ).fetchall()

    return [dict(row) for row in rows]

@app.post("/admin/decision")
async def decision(
    data: Decision,
    x_admin_secret: str = Header(None)
):
    check_admin(x_admin_secret)

    if data.status not in ("approved", "rejected", "blocked"):
        raise HTTPException(400, "Invalid status")

    with db() as con:
        con.execute(
            "UPDATE users SET status=? WHERE user_id=?",
            (data.status, data.user_id)
        )

    messages = {
        "approved": "Твоя заявка одобрена! Добро пожаловать!",
        "rejected": "К сожалению, заявка отклонена.",
        "blocked": "Твой доступ к приложению закрыт."
    }

    await telegram_message(data.user_id, messages[data.status])

    return {"success": True}

@app.get("/check/{user_id}")
def check_access(user_id: int):
    with db() as con:
        row = con.execute(
            "SELECT status FROM users WHERE user_id=?",
            (user_id,)
        ).fetchone()

    return {"status": row["status"] if row else "not_found"}
