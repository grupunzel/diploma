from backend.config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json, re
from backend.agent3_prompt import prompt_for_agent_3
from backend.database_functions import update_user_progress

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)


def make_report(test_id, content, topics):
    prompt = prompt_for_agent_3.format(
                        content=content,
                        topics=topics)

    try:
        response = gigachat.invoke([SystemMessage(content=prompt)])
        content = response.content.strip()
        # content = re.sub(r'<[^>]+>', '', content)
        # content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        # content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        # content = re.sub(r'__(.*?)__', r'\1', content)
        # content = re.sub(r'\*(.*?)\*', r'\1', content)
        # content = re.sub(r'_(.*?)_', r'\1', content)
        # content = re.sub(r'^[-*_]{3,}\s*$', '', content, flags=re.MULTILINE)

        if content.startswith('```json') and content.endswith('```'):
            content = content[7:-3].strip()
        elif content.startswith('```') and content.endswith('```'):
            content = content[3:-3].strip()

        report_dict = json.loads(content)
        update_user_progress(test_id, json.dumps(report_dict, ensure_ascii=False))
        return report_dict
    except Exception as e:
        logger.error('Error: ', e)
        return