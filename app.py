from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector
import random
import os
import time
from contextlib import asynccontextmanager

templates = Jinja2Templates(directory="templates")
db = None
cursor = None
# MySQL connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, cursor

    for _ in range(30):
        try:
            db = mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "guessgame"),
                port=int(os.getenv("DB_PORT", "3306"))
            )
            cursor = db.cursor()
            with open("init.sql") as f:
                for statement in f.read().split(";"):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
            db.commit()
            break
        except mysql.connector.Error:
            time.sleep(1)
    else:
        raise RuntimeError("Could not connect to MySQL")

    try:
        yield
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None and db.is_connected():
            db.close()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
   

SECRET_NUMBER = random.randint(1, 100)
attempts = 0

def get_scores():
    cursor.execute(
        "SELECT username, attempts FROM scores ORDER BY attempts ASC LIMIT 10"
    )
    return cursor.fetchall()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scores": get_scores(),
            "message": "",
            "username": ""
        }
    )


@app.post("/guess", response_class=HTMLResponse)
def guess(request: Request, username: str = Form(...), number: int = Form(...)):
    global SECRET_NUMBER
    global attempts

    attempts += 1
    message = ""

    if number < SECRET_NUMBER:
        message = "Too low!"
    elif number > SECRET_NUMBER:
        message = "Too high!"
    else:
        cursor.execute(
            "INSERT INTO scores (username, attempts) VALUES (%s, %s)",
            (username, attempts)
        )
        db.commit()

        message = f"Correct! You guessed it in {attempts} attempts."

        SECRET_NUMBER = random.randint(1, 100)
        attempts = 0

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "scores": get_scores(),
            "message": message,
            "username": username
        }
    )