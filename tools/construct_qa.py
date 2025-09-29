import json
import math
import random

    
def construct_qa(data):
    result = []

    input = data.get('questions_sections', [])
    for item in input:
        for q in item.get('questions', []):
            tmp_q = {}
            tmp_q['question'] = q['question_content'].replace("{{appellation}}",'')
            tmp_q['question_section_name'] = q.get('test_questions_section_name', '')
            tmp_q['question_type'] = 1 if q['question_type'] == 'A' else 2
            questions_options = q.get('questions_options', [])
            questions_options.sort(key=lambda x : x['value'])
            
            options = []
            for i in range(len(questions_options)):
                options.extend([questions_options[i]['label']])

            tmp_q['answer'] = random.sample(options, 1)
            result.extend([tmp_q])
    print(result)

if __name__ == '__main__':
    with open('../resource/试题.json','r') as f:
        data = json.load(f)

    construct_qa(data)
