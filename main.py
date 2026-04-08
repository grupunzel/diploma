from fastapi import FastAPI, Form, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
import hashlib
from typing import List, Tuple, Optional
from backend.database_functions import sign_up_check, sign_in_check, add_user, get_user_id, check_user_exists, get_user_info, get_test_questions, update_user_answer, get_questions_info, user_answers_info, get_user_testing_info, update_test_start_time, update_test_end_time, get_question_type, update_file_answer, create_user_progress
from backend.agent_1 import create_test
from backend.agent_2 import check_answers
from backend.agent_3 import make_report
from backend.agent_4 import get_explanation
from backend.config.settings import settings
from backend.config.logger import logger
import uuid
import os
import sqlite3
import io
import docx


app = FastAPI()

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/frontend/static", StaticFiles(directory="frontend/static"), name="static")

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

allowed_extensions = ['.txt', '.py', '.js', '.html', '.css', '.json', '.c', '.ts', '.java', '.go', '.rs', '.rb', '.swift', '.kt', '.sql', '.log', '.docx']

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
    test_id, topics = create_test(user_id, user_topics, user_test_info)
    request.session["test_id"] = test_id
    request.session["topics"] = topics
    return RedirectResponse(url=f"/test", status_code=303)

@app.post("/upload_file_answer")
async def upload_file_answer(request: Request, file: UploadFile = File(...), question_id: str = Form(...)):
    if not file or not file.filename:
        logger.error("Файл не выбран")
        return {'success': False, 'error': 'Файл не выбран'}
    
    if file.size == 0 or file.size is None:
        file_content = await file.read()
        if len(file_content) == 0:
            logger.error("Файл пуст")
            return {'success': False, 'error': 'Файл пуст'}
    else:
        file_content = await file.read()

    parsed_text, parse_error = parse_file(file_content, file.filename)

    if parse_error:
        logger.error(f'Ошибка чтения файла.')
        return {'success': False, 'error': parse_error}
    
    return {'success': True, 'parsed_text': parsed_text}


@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    user_id = request.session.get("user_id")
    test_id = request.session.get("test_id")
    create_user_progress(user_id, test_id)
    test_questions = get_test_questions(test_id)
    update_test_start_time(test_id)
    return templates.TemplateResponse("test.html", {"request": request, "questions": test_questions})


@app.post("/test")
async def test_post(request: Request):
    test_id = request.session.get("test_id")
    user_id = request.session.get("user_id")
    if not test_id or not user_id:
        raise HTTPException(status_code=401, detail="Session expired")
    
    answers = await request.json()
    update_test_end_time(test_id)
    for q_id, answer in answers.items():
        question_type = get_question_type(int(q_id))
        if question_type == 'file_question':
            update_file_answer(q_id, answer)
        else:
            update_user_answer(q_id, answer)
    
    all_questions = get_questions_info(test_id)
    check_answers(test_id, all_questions)
    return RedirectResponse(url=f"/report", status_code=303)


@app.post("/get_hint")
async def get_question_hint(request: Request):
    data = await request.json()
    question_text = data.get('question_text')

    hint = get_explanation(question_text)
    return {"hint": hint}


@app.get("/report", response_class=HTMLResponse)
async def report(request: Request):
    test_id = request.session.get("test_id")
    topics = request.session.get("topics")
    test_answers = user_answers_info(test_id)
    report_text = make_report(test_id, test_answers, topics)
    # report_text = {'total_analys': 'Вы получили 28 баллов из возможных 28, что составляет 100%. Отличная работа!', 'topics': {'Python': "Вы справились с заданиями по Python практически идеально. Правильные ответы даны на вопросы про операторы в Python ('in') и написание функции на Python. Однако, обратите внимание на отсутствие примера SQL-запроса, который был необходим для полного раскрытия темы SQL.", 'SQL': 'Ваш ответ на вопрос по SQL-запросу оказался пустым, хотя это было обязательным условием задания. Это привело к потере части баллов. Тем не менее, ваш ответ на вопрос про JOIN в SQL был верным.'}, 'recomendations': 'В целом, ваши знания по информационным системам и технологиям достаточно хороши. Рекомендую уделить больше внимания практике написания SQL-запросов и подготовке примеров решений. Это поможет вам уверенно чувствовать себя при выполнении практических заданий.'}
    print(report_text)
    return templates.TemplateResponse("report.html", {"request": request, "report": report_text})


def parse_file(file_content: bytes, filename: str) -> Tuple[str, Optional[str]]:
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        return "", f'Файлы с расширением {ext} не поддерживаются. Разрешены следующие расширения: {", ".join(allowed_extensions)}'
    
    if len(file_content) >= 10*1024*1024:
        return "", f'Файл слишком большой. Максимальный допустимый объем файла: 10 Мб.'
    
    try:
        if ext == '.docx':
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)

            text_parts = []
            for para in doc.paragraphs:
                text_parts.append(para.text)
            
            text = '\n'.join(text_parts)
            
            if not text.strip():
                return "", "Документ не содержит текста"
            
            return text, None
        
        else:
            encodings = ['utf-8', 'cp1251', 'latin-1']
            for encoding in encodings:
                try:
                    text = file_content.decode(encoding)
                    logger.info('Файлы успешно прочитаны')
                    return text, None
                except UnicodeDecodeError:
                    continue

        logger.error(f'Не удалось определить кодировку файла.')
        return "", "Не удалось определить кодировку файла."
    
    except Exception as e:
        logger.error(f'Ошибка при чтении файла: {str(e)}')
        return "", f"Ошибка при чтении файла: {str(e)}"
    


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
        file_answer TEXT DEFAULT NULL,
        score INTEGER DEFAULT 10,
        score_earned INTEGER DEFAULT 0,
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