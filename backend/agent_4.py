from config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json, os, sqlite3
from agent4_prompt import prompt_for_agent_4

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(THIS_DIR), 'ITest.db')

with sqlite3.connect(DB_PATH) as db:
    cursor = db.execute("SELECT question FROM TestQuestions WHERE question_id=?", (2,))
    question = cursor.fetchone()[0]
    cursor = db.execute("SELECT answers FROM TestQuestions WHERE question_id=?", (2,))
    answers = cursor.fetchone()[0]
    cursor = db.execute("SELECT right_answer FROM TestQuestions WHERE question_id=?", (2,))
    right_answer = cursor.fetchone()[0]

prompt = prompt_for_agent_4.format(
                    question=question,
                    answers=answers,
                    right_answer=right_answer)

try:
    response = gigachat.invoke([SystemMessage(content=prompt)])
    content = response.content.strip()
    print(content)
except Exception as e:
    logger.error('Error: ', e)