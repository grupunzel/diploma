from backend.config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json, os, sqlite3
from backend.agent5_prompt import prompt_for_agent5

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(THIS_DIR), 'ITest.db')


def process_user_input(user_input):

    prompt = prompt_for_agent5.format(
                        user_input=user_input)

    try:
        response = gigachat.invoke([SystemMessage(content=prompt)])
        content = response.content.strip()
        return content
    except Exception as e:
        logger.error('Error: ', e)
        return