from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import hashlib
from backend.database_functions import sign_up_check, sign_in_check, add_user, get_user_id, check_user_exists, get_user_info
from backend.config.settings import settings
from backend.config.logger import logger
import os
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/frontend/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_redirect(request: Request):
    return RedirectResponse(url="/register", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})


@app.post("/register")
async def register_user(request: Request, email: str=Form(...), password: str=Form(...)):
    real_password = hashlib.sha256(password.encode()).hexdigest()
    if_new_user = sign_up_check(email)
    if if_new_user:
        add_user(first_name=None, last_name=None, email=email, password=real_password, is_anonymous=True)
        return RedirectResponse(url="/login?registered=1", status_code=303)
    else:
        return templates.TemplateResponse(
            "sign_up.html",
            {"request": request, "error": "Email уже используется"}
        )
    

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registered: int = 0):
    message = "You signed in successfully!" if registered == 1 else ""
    return templates.TemplateResponse(
        "sign_in.html", 
        {"request": request, "message": message}
    )


@app.post("/login")
async def login_user(request: Request, email: str=Form(...), password: str=Form(...)):
    real_password = hashlib.sha256(password.encode()).hexdigest()
    check = sign_in_check(email, real_password)
    if check:
        print("check = True")
        user_id = get_user_id(email)
        return RedirectResponse(url=f"/dashboard/{user_id}", status_code=303)
    else:
        return templates.TemplateResponse(
            "sign_in.html",
            {"request": request, "error": "Неверный email или пароль"}
        )
    

@app.get("/dashboard/{user_id}", response_class=HTMLResponse)
async def dashboard(request: Request, user_id: int):
    if_user_exists = check_user_exists(user_id + 1)
    if if_user_exists:
        user_info, test_info = get_user_info(user_id + 1)
        tests = ""
        for test in test_info:
            tests += test
        return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user_id, "user": user_info, "tests": tests}
    )
    else:
        return RedirectResponse(url="/register", status_code=303)


@app.get("/pick_topics", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("pick_topics.html", {"request": request})


def init_db():
    if os.path.exists('ITest.db'):
        logger.info("Database already exists")
        return
    
    with sqlite3.connect('ITest.db') as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        password TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
                         )
        
        db.execute("""
        CREATE TABLE IF NOT EXISTS TestQuestions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        module TEXT,
        type TEXT,
        question TEXT,
        answers TEXT DEFAULT NULL,
        right_answer TEXT DEFAULT NULL,
        user_answer TEXT DEFAULT NULL,
        file_answer_path TEXT DEFAULT NULL,
        score INTEGER DEFAULT 10,
        score_earned INTEGER DEFAULT 0,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        )
        """
                         )
        
        db.execute("""
        CREATE TABLE IF NOT EXISTS UserProgress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        test_id INTEGER,
        total_score INTEGER,
        max_score INTEGER,
        percentage INTEGER,
        report TEXT,
        FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(test_id) REFERENCES TestQuestions(test_id) ON DELETE CASCADE
        )
        """
                         )
        
        db.commit()


def main():
    init_db()


if __name__ == "__main__":
    main()