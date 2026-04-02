from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
import hashlib
from typing import List
from backend.database_functions import sign_up_check, sign_in_check, add_user, get_user_id, check_user_exists, get_user_info, get_test_questions, update_user_answer, get_questions_info, show_user_answers, get_user_testing_info
from backend.agent_1 import create_test
from backend.agent_2 import check_answers
from backend.config.settings import settings
from backend.config.logger import logger
import uuid
import os
import sqlite3

app = FastAPI()

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/frontend/static", StaticFiles(directory="frontend/static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/sign_in", response_class=HTMLResponse)
async def profile_redirect(request: Request):
    return RedirectResponse(url="/register", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})


@app.post("/register")
async def register_user(request: Request, first_name: str=Form(...), last_name: str=Form(...), email: str=Form(...), password: str=Form(...)):
    real_password = hashlib.sha256(password.encode()).hexdigest()
    if_new_user = sign_up_check(email)
    if if_new_user:
        user_id = add_user(first_name=first_name, last_name=last_name, email=email, password=real_password, is_anonymous=False)
        request.session["user_id"] = user_id
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
        user_id = get_user_id(email)
        request.session["user_id"] = user_id
        return RedirectResponse(url=f"/profile", status_code=303)
    else:
        return templates.TemplateResponse(
            "sign_in.html",
            {"request": request, "error": "Неверный email или пароль"}
        )
    

@app.get("/profile", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = request.session.get("user_id")
    if_user_exists = check_user_exists(user_id)
    if if_user_exists:
        user_info, test_info = get_user_info(user_id)
        tests = ""
        for test in test_info:
            tests += test
        return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user_id": user_id, "user_info": user_info, "tests": tests}
    )
    else:
        return RedirectResponse(url="/register", status_code=303)


@app.get("/pick_topics", response_class=HTMLResponse)
async def pick_topics(request: Request):
    return templates.TemplateResponse("pick_topics.html", {"request": request})


@app.post("/pick_topics")
async def submitting_topics(request: Request, user_topics: str=Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        user_id = add_user(is_anonymous=True)
        request.session["user_id"] = user_id
    user_test_info = get_user_testing_info(user_id)
    test_id = create_test(user_id, user_topics, user_test_info)
    request.session["test_id"] = test_id
    return RedirectResponse(url=f"/test", status_code=303)


@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    test_id = request.session.get("test_id")
    test_questions = get_test_questions(test_id)
    return templates.TemplateResponse("test.html", {"request": request, "questions": test_questions})

@app.post("/test")
async def test_post(request: Request, answers: List[str] = Form(...), question_ids: List[str] = Form(...)):
    test_id = request.session.get("test_id")
    user_id = request.session.get("user_id")
    if not test_id or not user_id:
        raise HTTPException(status_code=401, detail="Session expired")
    
    for q_id, answer in zip(question_ids, answers):
        update_user_answer(q_id, answer)
    
    all_questions = get_questions_info(test_id)
    check_answers(test_id, all_questions)
    return RedirectResponse(url=f"/report", status_code=303)

@app.get("/report", response_class=HTMLResponse)
async def report(request: Request):
    test_id = request.session.get("test_id")
    test_report = show_user_answers(test_id)
    return templates.TemplateResponse("report.html", {"request": request, "report": test_report})


def init_db():
    if os.path.exists('ITest.db'):
        logger.info("Database already exists")
        return
    
    with sqlite3.connect('ITest.db') as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
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
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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