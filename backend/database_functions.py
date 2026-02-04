import sqlite3
from config.logger import logger
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(THIS_DIR), 'ITest.db')

def database_fill(data):
    try:
        with sqlite3.connect(DB_PATH) as db:
            if data is not None:
                logger.info(f"Начало обработки {len(data)} заданий")
                cursor = db.execute("SELECT MAX(test_id) FROM TestQuestions")
                result = cursor.fetchone()
                if result and result[0] is not None:
                    test_id = result[0] + 1
                else:
                    test_id = 1
                
                for i, task in enumerate(data, 1):
                    logger.info(f"Обработка задания {i}/{len(data)}: {task.get('question', 'No question')}")
                    user_id = task.get("user_id")
                    module = task.get("module")
                    type_ = task.get("type")
                    question = task.get("question")
                    answers = task.get("answers")
                    right_answer = task.get("right_answer")
                    user_answer = task.get("user_answer", None)
                    file_answer_path = task.get("file_answer_path", None)
                    score = task.get("score", 10)
                    score_earned = task.get("score_earned", 0)

                    cursor = db.execute("SELECT user_id FROM Users WHERE user_id=?", (user_id,))
                    row = cursor.fetchone()
                    
                    if not row:
                        add_user()
                        logger.info(f"Добавлен новый пользователь: {user_id}")
                    
                    cursor.execute("INSERT INTO TestQuestions (test_id, user_id, module, type, question, answers, right_answer, user_answer, file_answer_path, score, score_earned) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (test_id, user_id, module, type_, question, answers, right_answer, user_answer, file_answer_path, score, score_earned))
                    logger.info(f"Добавлено задание {i} для теста #{test_id}")

                db.commit()
                logger.info(f"Тест #{test_id} успешно сохранен в БД ({len(data)} вопросов)")
                return True 
            else:
                logger.error("Объект data пустой")
                return False

    except Exception as e:
        logger.error(f"Ошибка добавления задания в TestQuestions: {e}")
        return False
        
          
def add_user(first_name=None, last_name=None, email=None, is_anonymous=True):
    try:
        with sqlite3.connect(DB_PATH) as db:
            if is_anonymous:
                first_name = "Аноним _"
            if email:
                cursor = db.execute("SELECT user_id FROM Users WHERE email=?", (email,))
                if cursor.fetchone():
                    logger.warning(f"Пользователь с email {email} уже существует!")
                    return False
            cursor = db.execute("INSERT INTO Users (first_name, last_name, email) VALUES (?, ?, ?)", (first_name, last_name, email))
            user_id = cursor.lastrowid

            if is_anonymous:
                cursor = db.execute("UPDATE Users SET last_name=? WHERE user_id=?", (str(user_id), user_id))
                last_name = str(user_id)
            db.commit()
            logger.info(f"Создан пользователь #{user_id}: {first_name} {last_name}")
            return True
        
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        return False
    

def update_user(user_id, first_name, last_name, email):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT email FROM Users WHERE user_id=?", (user_id,))
            result = cursor.fetchone()[0]
            if result and result != email:
                cursor = db.execute("SELECT user_id FROM Users WHERE email=?", (email,))
                if cursor.fetchone():
                    logger.warning("Пользователь с таким email уже существует!")
                    return False
            cursor = db.execute("UPDATE Users SET first_name=?, last_name=?, email=? WHERE user_id=?", (first_name, last_name, email, user_id,))
            db.commit()
            logger.info(f"Данные пользователя #{user_id} успешно изменены")
            return True
    
    except Exception as e:
        logger.error("Ошибка при редактировании информации о пользователе: {e}")
        return False
    

def delete_user(user_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT user_id FROM Users WHERE user_id=?", (user_id,))
            if not cursor.fetchone():
                logger.warning(f"Пользователя #{user_id} не существует")
                return False
            else:
                cursor = db.execute("DELETE FROM Users WHERE user_id=?", (user_id,))
                db.commit()
                logger.info(f"Пользователь #{user_id} успешно удалён")
                return True
    except Exception as e:
        logger.error(f"Ошибка удаления пользователя: {e}")
        return False
    

def update_user_answer(question_id, user_answer):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("UPDATE TestQuestions SET user_answer=? WHERE question_id=?", (user_answer, question_id,))
            db.commit()
            logger.info("Ответ пользователя успешно изменён")
            return True
    
    except Exception as e:
        logger.error(f"Ошибка редактирования ответа пользователя: {e}")
        return False
    

def update_file_answer(question_id, file_path):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("UPDATE TestQuestions SET file_answer_path=? WHERE question_id=?", (file_path, question_id,))
            db.commit()
            logger.info("Ответ пользователя успешно изменён")
            return True
    
    except Exception as e:
        logger.error(f"Ошибка замены file_path {e}")
        return False


def update_user_progress(user_id, test_id, report):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT test_id FROM UserProgress WHERE test_id=?", (test_id,))
            if cursor.fetchone():
                logger.error(f"Запись с тестом #{test_id} уже существует")
                return False
            
            cursor = db.execute("SELECT SUM(score) FROM TestQuestions WHERE test_id=?", (test_id,))
            max_score = cursor.fetchone()[0]

            cursor = db.execute("SELECT SUM(score_earned) FROM TestQuestions WHERE test_id=?", (test_id,))
            total_score = cursor.fetchone()[0]

            percentage = int((total_score / max_score)*100)
    
            cursor = db.execute("INSERT INTO UserProgress (user_id, test_id, total_score, max_score, percentage, report) VALUES(?, ?, ?, ?, ?, ?)", (user_id, test_id, total_score, max_score, percentage, report))
            db.commit()
            logger.info(f"Тест #{test_id} успешно добавлен в UserProgress")
            return True
    
    except Exception as e:
        logger.error(f"Ошибка при добавлении теста в UserProgress: {e}")
        return False