from config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json
from agent2_prompt import prompt_for_agent_2
from agent_1 import create_test

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2-Lite",
                    verify_ssl_certs=False)

def check_answers():

    content = create_test()

    prompt = prompt_for_agent_2.format(
                        content=content)

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
        return result
    except Exception as e:
        print('Error: ', e)