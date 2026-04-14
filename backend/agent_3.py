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


def make_report(lang, test_id, content, topics, is_anonym):

    questions_data = content.get('questions', {})
    total_score_earned = content.get('total_score_earned', 0)
    total_score_max = content.get('total_score_max', 0)
    percentage = content.get('percentage', 0)

    prompt = prompt_for_agent_3.format(
                        lang=lang,
                        total_score_earned=total_score_earned,
                        total_score_max=total_score_max,
                        percentage=percentage,
                        questions_data=questions_data,
                        topics=topics)

    try:
        response = gigachat.invoke([SystemMessage(content=prompt)])
        json_str = response.content.strip()
        if json_str.startswith('```json') and json_str.endswith('```'):
            json_str = json_str[7:-3].strip()
        elif json_str.startswith('```') and json_str.endswith('```'):
            json_str = json_str[3:-3].strip()

        report_dict = json.loads(json_str)
        topics_dict = {}
        if 'topics_list' in report_dict and 'topics_report' in report_dict:
            for topic, analysis in zip(report_dict['topics_list'], report_dict['topics_report']):
                topics_dict[topic] = analysis

        result = {
            "total_analys": report_dict.get('total_analys', ''),
            "topics": topics_dict,
            "recomendations": report_dict.get('recomendations', '')
        }
        if not is_anonym:
            update_user_progress(test_id, result)
        return result
    except Exception as e:
        logger.error('Error: ', e)
        return