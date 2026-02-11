from config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json
from agent3_prompt import prompt_for_agent_3
from agent_2 import check_answers
from agent_1 import topics
from database_functions import update_user_progress

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)

content, user_id, test_id = check_answers()

prompt = prompt_for_agent_3.format(
                    content=content,
                    topics=topics)

try:
    response = gigachat.invoke([SystemMessage(content=prompt)])
    content = response.content.strip()
    update_user_progress(user_id, test_id, content)
except Exception as e:
    logger.error('Error: ', e)