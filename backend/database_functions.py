import sqlite3
from backend.config.logger import logger
import os, json
from datetime import datetime

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(THIS_DIR), 'ITest.db')

def database_fill(data: list):
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

                user_id = data[0].get("user_id")
                cursor = db.execute("SELECT user_id FROM Users WHERE user_id=?", (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    new_user_id = add_user()
                    logger.info(f"Добавлен новый пользователь: {new_user_id}")
                else:
                    new_user_id = user_id
                
                for i, task in enumerate(data, 1):
                    logger.info(f"Обработка задания {i}/{len(data)}: {task.get('question', 'No question')}")
                    module = task.get("module")
                    type_ = task.get("type")
                    question = task.get("question")
                    answers = task.get("answers")
                    right_answer = task.get("right_answer")
                    score = task.get("score", 10)

                    cursor.execute("INSERT INTO TestQuestions (test_id, user_id, module, type, question, answers, right_answer, score) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (test_id, new_user_id, module, type_, question, answers, right_answer, score))
                    logger.info(f"Добавлено задание {i} для теста #{test_id}")

                db.commit()
                logger.info(f"Тест #{test_id} успешно сохранен в БД ({len(data)} вопросов)")
                return test_id
            else:
                logger.error("Объект data пустой")
                return False

    except Exception as e:
        logger.error(f"Ошибка добавления задания в TestQuestions: {e}")
        return False
        
          
def add_user(role="user", first_name=None, last_name=None, email=None, password=None, is_anonymous=True):
    try:
        with sqlite3.connect(DB_PATH) as db:
            if is_anonymous:
                first_name = "Аноним _"
            if email:
                cursor = db.execute("SELECT user_id FROM Users WHERE email=?", (email,))
                if cursor.fetchone():
                    logger.warning(f"Пользователь с email {email} уже существует!")
                    return False
            cursor = db.execute("INSERT INTO Users (role, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)", (role, first_name, last_name, email, password))
            user_id = cursor.lastrowid

            if is_anonymous:
                cursor = db.execute("UPDATE Users SET last_name=? WHERE user_id=?", (str(user_id), user_id))
                last_name = str(user_id)
            db.commit()
            logger.info(f"Создан пользователь #{user_id}: {first_name} {last_name}")
            return user_id
        
    except Exception as e:
        logger.error(f"Ошибка создания пользователя: {e}")
        return False
    

def update_user(user_id, first_name, last_name, email, password):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT email FROM Users WHERE user_id=?", (user_id,))
            result = cursor.fetchone()[0]
            if result and result != email:
                cursor = db.execute("SELECT user_id FROM Users WHERE email=?", (email,))
                if cursor.fetchone():
                    logger.warning("Пользователь с таким email уже существует!")
                    return False
            cursor = db.execute("UPDATE Users SET first_name=?, last_name=?, email=?, password=? WHERE user_id=?", (first_name, last_name, email, password, user_id))
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
    

def update_file_answer(question_id, file_answer):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("UPDATE TestQuestions SET file_answer=? WHERE question_id=?", (file_answer, question_id,))
            db.commit()
            logger.info("Ответ пользователя успешно изменён")
            return True
    
    except Exception as e:
        logger.error(f"Ошибка замены file_answer {e}")
        return False


def create_user_progress(user_id, test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute('INSERT INTO UserProgress (user_id, test_id, total_score, max_score, percentage, report) VALUES (?, ?, ?, ?, ?, ?)', (user_id, test_id, 0, 0, 0, '{}'))
            db.commit()
            logger.info(f'Добавили запись о тесте #{test_id} в UserProgress')
            return True
    
    except Exception as e:
        logger.error(f'Ошибка создания записи о тесте #{test_id} в UserProgress: {e}')
        return False


def update_user_progress(test_id, report):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT user_id FROM TestQuestions WHERE test_id=? LIMIT 1", (test_id,))
            user_result = cursor.fetchone()
            user_id = user_result[0] if user_result else None
            
            if user_id is None:
                logger.error(f"Не удалось найти user_id для test_id {test_id}")
                return False
            
            cursor = db.execute("SELECT SUM(score) FROM TestQuestions WHERE test_id=?", (test_id,))
            max_score = cursor.fetchone()[0]

            cursor = db.execute("SELECT SUM(score_earned) FROM TestQuestions WHERE test_id=?", (test_id,))
            total_score = cursor.fetchone()[0]

            percentage = int((total_score / max_score)*100)

            report_json = json.dumps(report, ensure_ascii=False)
    
            cursor = db.execute("UPDATE UserProgress SET total_score=?, max_score=?, percentage=?, report=? WHERE test_id=?", (total_score, max_score, percentage, report_json, test_id))
            db.commit()
            logger.info(f"Тест #{test_id} успешно добавлен в UserProgress")
            return True
    
    except Exception as e:
        logger.error(f"Ошибка при добавлении теста в UserProgress: {e}")
        return False
    

def check_user_answer(data: list):
    try:
        with sqlite3.connect(DB_PATH) as db:
            if data is not None:
                logger.info(f"Начало проверки заданий для теста #{data[0].get('test_id')}")

                for i, task in enumerate(data, 1):
                    logger.info(f"Проверка задания {i}/{len(data)}: {task.get('question', 'No question')}")
                    user_id = task.get("user_id")
                    test_id = task.get("test_id")
                    question = task.get("question")
                    score_earned = task.get("score_earned")

                    logger.info(f"Типы: user_id={type(user_id)}, test_id={type(test_id)}, question={type(question)}")

                    cursor = db.execute("SELECT question_id FROM TestQuestions WHERE test_id=? AND question=?", (test_id, question,))
                    question_id = cursor.fetchone()
                    if not question_id:
                        logger.error(f"Вопрос не найден в БД! user_id={user_id}, test_id={test_id}")
                    else:
                        question_id = question_id[0]

                    cursor = db.execute("UPDATE TestQuestions SET score_earned=? WHERE question_id=?", (score_earned, question_id,))
                    logger.info(f"Задание {i}/{len(data)} успешно проверено")

                db.commit()
                logger.info(f"Тест #{data[0].get("test_id")} успешно проверен")
                return user_id
            else:
                logger.error("Объект data пустой")
                return False
            
    except Exception as e:
        logger.error(f"Ошибка проверки заданий: {e}")
        return False
    

def sign_in_check(email, password):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT email FROM Users WHERE email=?", (email,))
            if not cursor.fetchone():
                logger.error("Неправильная почта")
                return False
            
            cursor = db.execute("SELECT password FROM Users WHERE email=?", (email,))
            real_password = cursor.fetchone()[0]

            if password == real_password:
                logger.info("Пароль правильный")
                return True
            else:
                logger.info("Пароль не правильный")
                return False
            
    except Exception as e:
        logger.error(f"Ошибка сравнения паролей: {e}")
        return None


def sign_up_check(email):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT email FROM Users WHERE email=?", (email,))
            if cursor.fetchone():
                logger.error("Пользователь с такой почтой уже существует")
                return False
            return True
    except Exception as e:
        logger.error(f"Ошибка регистрации пользователя: {e}")
        return None
    

def get_user_id(email):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT user_id FROM Users WHERE email=?", (email,))
            user_id = cursor.fetchone()[0]
            if user_id:
                logger.info("Успешно получили id пользователя")
                return user_id
            else:
                logger.error("Не удалось получить user_id")
                return False
    
    except Exception as e:
        logger.error(f"Ошибка получения id пользователя: {e}")
        return False
    

def check_user_exists(user_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT user_id FROM Users WHERE user_id=?", (user_id,))
            if cursor.fetchone:
                logger.info("Пользователь существует")
                return True
            else:
                logger.error("Такого пользователя не существует")
                return False
    
    except Exception as e:
        logger.error(f"Ошибка проверки существования пользователя: {e}")
        return None
    

def get_user_info(user_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT first_name, last_name, email FROM Users WHERE user_id=?", (user_id,))
            result = cursor.fetchone()
            first_name, last_name, email = result

            user_info = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }

            cursor = db.execute("SELECT test_id, total_score, max_score, percentage, report FROM UserProgress WHERE user_id=?", (user_id,))
            result = cursor.fetchall()

            tests_info = {}
            for test in result:
                test_id, total_score, max_score, percentage, report = test
                
                tests_info[test_id] = {
                    'total_score': total_score,
                    'max_score': max_score,
                    'percentage': percentage,
                    'report': report
                }

            logger.info("Успешно вывели информацию о пользователе")
            return user_info, tests_info
    
    except Exception as e:
        logger.error(f"Ошибка вывода информации о пользователе: {e}")
        return None, {}


def get_test_questions(test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT question_id, module, type, question, answers, score FROM TestQuestions WHERE test_id=?", (test_id,))
            result = cursor.fetchall()

            questions = {}
            for question in result:
                question_id, module, type, question_text, answers, score = question

                if answers:
                    question_answers = answers.split('; ')
                    answers_info = []
                    for i in range(len(question_answers)):
                        answers_info.append(f"{question_answers[i]}")
                else:
                    answers_info = None

                questions[question_id] = {
                    'module': module,
                    'type': type,
                    'question_text': question_text,
                    'answers': answers_info,
                    'score': score,
                }
            
            logger.info(f"Успешно вывели вопросы из теста №{test_id}")
            return questions
    
    except Exception as e:
        logger.error(f'Ошибка при выводе вопросов из теста №{test_id}: {e}')
        return False
    
def get_questions_info(test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT question_id, type, question, answers, right_answer, user_answer, file_answer, score FROM TestQuestions WHERE test_id=?", (test_id,))
            result = cursor.fetchall()
            all_questions = []
            for question in result:
                question_id, question_type, question_text, answers, right_answer, user_answer, file_answer, score = question

                all_questions.append({
                    'question_id': question_id,
                    'question_type': question_type,
                    'question_text': question_text,
                    'answers': answers,
                    'right_answer': right_answer,
                    'user_answer': user_answer,
                    'file_answer': file_answer,
                    'score': score
                })
            logger.info(f"Успешно получили информацию о заданиях теста №{test_id}")
            return all_questions
    
    except Exception as e:
        logger.error(f'Ошибка получения информации о заданиях теста №{test_id}: {e}')
        return []
    

def get_user_testing_info(user_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT test_id, total_score, max_score, report FROM UserProgress WHERE user_id=?", (user_id,))
            result = cursor.fetchall()

            test_info = {}
            for test in result:
                test_id, total_score, max_score, report = test
                test_info[test_id] = {
                    'total_score': total_score,
                    'max_score': max_score,
                    'report': report,
                }
            
            logger.info(f'Успешно вывели историю прошлах тестирований пользователя №{user_id}')
            return test_info
    
    except Exception as e:
        logger.error(f'Ошибка вывод истории тестирований: {e}')
        return False
    

def user_answers_info(test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT question, type, answers, right_answer, user_answer, file_answer, score, score_earned FROM TestQuestions WHERE test_id=?", (test_id,))
            result = cursor.fetchall()

            info = []
            total_score_earned = 0
            total_score_max = 0
            question_id = 1
            for question in result:
                question_text, question_type, answers, right_answer, user_answer, file_answer, score, score_earned = question

                total_score_earned += score_earned if score_earned else 0
                total_score_max += score if score else 0

                info.append({
                    'question_id': question_id,
                    'question_text': question_text,
                    'question_type': question_type,
                    'question_answers': answers,
                    'right_answer': right_answer,
                    'user_answer': user_answer,
                    'file_answer': file_answer,
                    'score': score,
                    'score_earned': score_earned
                })
                question_id += 1

            percentage = int((total_score_earned / total_score_max) * 100) if total_score_max > 0 else 0
            
            logger.info(f'Успешно получили информацию об ответах пользователя на тест #{test_id}')
            return {
                'questions': info,
                'total_score_earned': total_score_earned,
                'total_score_max': total_score_max,
                'percentage': percentage
            }
        
    except Exception as e:
        logger.error(f"Ошибка получения информации об ответах пользователя: {e}")
        return False
    

def update_test_start_time(test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute('UPDATE UserProgress SET start_time=? WHERE test_id=?', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), test_id,))
            db.commit()
            logger.info(f'Успешно занесли время начала тестирования #{test_id} в UserProgress.')
            return True
    
    except Exception as e:
        logger.error(f'Ошибка занесения времени начала тестирования: {e}')
        return False
    

def update_test_end_time(test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute('UPDATE UserProgress SET end_time=? WHERE test_id=?', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), test_id,))
            db.commit()
            logger.info(f'Успешно занесли время окончания тестирования #{test_id} в UserProgress.')
            return True
    
    except Exception as e:
        logger.error(f'Ошибка занесения времени окончания тестирования: {e}')
        return False
    

def get_question_type(question_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute('SELECT type FROM TestQuestions WHERE question_id=?', (question_id,))
            result = cursor.fetchone()[0]
            return result
    
    except Exception as e:
        logger.error(f'Ошибка определения типа вопроса: {e}')
        return False
    

def is_user_anonym(user_id): 
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT first_name FROM Users WHERE user_id=?", (user_id,))
            result = cursor.fetchone()[0]
            if result == "Аноним _":
                return True
            else:
                return False
            
    except Exception as e:
        logger.error(f'Ошибка определения анонимности пользователя: {e}')
        return None
    
def if_user_progress_exists(test_id):
    try:
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.execute("SELECT test_id FROM UserProgress WHERE test_id=?", (test_id,))
            result = cursor.fetchone()

            if result:
                return True
            else:
                return False
    
    except Exception as e:
        logger.error(f'Ошибка проверки наличия записи в UserProgress: {e}')
        return None