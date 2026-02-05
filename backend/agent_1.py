from config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json
from agent1_prompt import prompt_for_agent_1
from database_functions import database_fill

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)

topics = ['Python']

def create_test():
    prompt = prompt_for_agent_1.format(
                        topics=topics)

    try:
        response = gigachat.invoke([SystemMessage(content=prompt)])
        content = response.content.strip()
        if content.startswith('```json') and content.endswith('```'):
            content = content[7:-3].strip()
        elif content.startswith('```') and content.endswith('```'):
            content = content[3:-3].strip()
        if content.startswith('[') and content.endswith(']'):
            result = json.loads(content)
        else:
            result = [json.loads(content)]
        test_id = database_fill(result)
        return [test_id, result]
    except Exception as e:
        logger.error('Error: ', e)