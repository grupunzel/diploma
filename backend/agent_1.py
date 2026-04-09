from backend.config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json, re
from backend.agent1_prompt import prompt_for_agent_1
from backend.database_functions import database_fill
from backend.agent_5 import process_user_input

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)

def create_test(user_id, topics, user_info):

    checked_topics = process_user_input(topics)

    prompt = prompt_for_agent_1.format(
                        topics=checked_topics,
                        user_id=user_id,
                        user_info=user_info)

    try:
        response = gigachat.invoke([SystemMessage(content=prompt)])
        content = response.content.strip()
        if content.startswith('```json') and content.endswith('```'):
            content = content[7:-3].strip()
        elif content.startswith('```') and content.endswith('```'):
            content = content[3:-3].strip()

        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)

        if content.startswith('[') and content.endswith(']'):
            result = json.loads(content)
        else:
            result = [json.loads(content)]
        test_id = database_fill(result)
        return [test_id, topics]
    except Exception as e:
        logger.error('Error: ', e)
        return False
