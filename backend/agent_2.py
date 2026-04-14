from backend.config.settings import logger, Settings
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage
import json
from backend.agent2_prompt import prompt_for_agent_2
from backend.agent_1 import create_test
from backend.database_functions import check_user_answer, user_answers_info

gigachat = GigaChat(temperature=0,
                    top_p=0.1,
                    credentials=Settings.GIGA_CREDENTIALS,
                    model="GigaChat-2",
                    verify_ssl_certs=False)

def check_answers(user_id, test_id, content):
    
    for item in content:
        question_type = item.get('question_type')
        user_answer = item.get('user_answer')
        file_answer = item.get('file_answer')
        
        if question_type in ['multiple_choice', 'open_question']:
            if not user_answer or str(user_answer).strip() == '' or str(user_answer) == 'None':
                item['user_answer'] = 'NO_ANSWER'
            else:
                item['user_answer'] = str(user_answer).strip()
            item['file_answer'] = 'IGNORE_FIELD'
            
        elif question_type == 'file_question':
            if not file_answer or str(file_answer).strip() == '' or str(file_answer) == 'None':
                item['file_answer'] = 'NO_ANSWER'
            else:
                item['file_answer'] = str(file_answer).strip()
            item['user_answer'] = 'IGNORE_FIELD'
    

    prompt = prompt_for_agent_2.format(
                        user_id=user_id,
                        content=content,
                        test_id=test_id)

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
        check_user_answer(result)
        return True
    except Exception as e:
        logger.error('Error: ', e)
        return False