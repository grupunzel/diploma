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
        json_str = response.content.strip()
        if json_str.startswith('```json') and json_str.endswith('```'):
            json_str = json_str[7:-3].strip()
        elif json_str.startswith('```') and json_str.endswith('```'):
            json_str = json_str[3:-3].strip()

        # quotes_map = {
        #     '“': '"', '”': '"',
        #     '„': '"', '‟': '"',
        #     '«': '"', '»': '"',
        #     '‹': '"', '›': '"',
        #     '‘': "'", '’': "'",
        #     '‛': "'",
        # }
        # for wrong, correct in quotes_map.items():
        #     json_str = json_str.replace(wrong, correct)
        # json_str = re.sub(r'\*\*([^*]+)\*\*', r'\1', json_str)
        # json_str = re.sub(r'\*([^*]+)\*', r'\1', json_str)
        # json_str = re.sub(r'__([^_]+)__', r'\1', json_str)
        # json_str = re.sub(r'_([^_]+)_', r'\1', json_str)
        # json_str = re.sub(r'<[^>]+>', '', json_str)
        # json_str = re.sub(r'[#`>]', '', json_str)
        # json_str = re.sub(r'//.*?($|\n)', '', json_str, flags=re.MULTILINE)
        # json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        # json_str = re.sub(r',\s*}', '}', json_str)
        # json_str = re.sub(r',\s*]', ']', json_str)
        # json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        # open_braces = json_str.count('{')
        # close_braces = json_str.count('}')
        # open_brackets = json_str.count('[')
        # close_brackets = json_str.count(']')
        # if open_braces > close_braces:
        #     json_str += '}' * (open_braces - close_braces)
        # if open_brackets > close_brackets:
        #     json_str += ']' * (open_brackets - close_brackets)
        # json_str = json_str.lstrip('\ufeff')
        # json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        report_dict = json.loads(json_str)
        update_user_progress(test_id, json.dumps(report_dict, ensure_ascii=False))
        return report_dict
    except Exception as e:
        logger.error('Error: ', e)
        return