from config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json
from agent3_prompt import prompt_for_agent_3
from agent_2 import check_answers
from agent_1 import topics

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2-Lite",
                    verify_ssl_certs=False)

content = check_answers()

prompt = prompt_for_agent_3.format(
                    content=content,
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
    print('Отчет: ', result)
except Exception as e:
    print('Error: ', e)