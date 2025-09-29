import pandas as pd
import random
import json
import sys

sys.path.append('/root/code/ai_based_education')
from utils.func_str import common_chars

with open('/root/code/ai_based_education/resource/q_score.json','r') as f:
    Q_BANK = json.load(f)

MOCK_LIST = [
    'Mock1-汤同学,G5,公立,中国大陆本科,教育预算10万',
    'Mock2-戴同学,G8,国际,英联邦本科,教育预算30万以上',
    'Mock3-李同学,G5,公立,中国大陆本科,教育预算20万',
    'Mock4-邓同学,G6,国际,英联邦本科,教育预算30万以上',
    'Mock5-李同学,G9,公立,中国大陆本科/美国本科,教育预算20万',
    'Mock6-彭同学,G6,国际,美国本科,教育预算30万以上',
    'Mock7-吴同学,G8,公立,英联邦本科/美国本科,教育预算30万以上',
    'Mock8-李同学,G6,国际,美国本科/港澳台本科/英联邦本科,教育预算30万以上'
]
def eval_result(idx):
    # df = pd.read_excel('/root/code/ai_based_education/data/Mock1_2.xlsx',sheet_name=None)['Mock1'].fillna('')
    # df = pd.read_excel('/root/code/ai_based_education/data/0916_Mock.xlsx',sheet_name=None)['AnswerMockTemplate'].fillna('')
    df = pd.read_excel('/root/code/ai_based_education/data/0928Mock.xlsx',sheet_name=None)['_________'].fillna('')
    # print(df.keys())
    
    def ans_col(idx):
        for item in MOCK_LIST:
            if 'Mock'+str(idx) in item:
                return item
        return ''

    def student_info(idx):
        student_info = {}
        item = ans_col(idx)
        info = item.strip().split('-')[1].strip().split(',')
        student_info["name"] = info[0]
        student_info["gender"] = ''
        student_info["school_type"] = info[2]
        student_info["current_grade"] = info[1]
        student_info["city_location"] = "深圳"
        student_info["college_goal_path"] = info[3].strip().split('/')
        student_info["id"] = random.randint(888,999)
        return student_info
                
    res = {}
    res['student_info'] = student_info(idx)

    def get_ans_content(dim, q, q_option):
        tmp_q_score = Q_BANK[dim]
        ans_list = []
        tmp_q = q.replace("{{appellation}}",'').strip()
        for elem in tmp_q_score:
            # if common_chars(q,elem['question'])/len(set(elem['question'])) > 0.9:
            if tmp_q.strip() == elem['question'].strip():
                options = elem['questions_options'] 
                tmp_ans = q_option.strip().split(',')
                for k,v in options.items():
                    if v in tmp_ans:
                        ans_list.extend([k])
        return ans_list

    def find_dim(q_content):
        tmp_q = q_content.replace("{{appellation}}",'').strip()
        for key in Q_BANK:
            q_list = Q_BANK[key]
            for item in q_list:
                if tmp_q.strip() == item['question'].strip():
                    return key
        return ''

    eval_result = [] 
    for i in range(len(df)):
        item = df.iloc[i]
        question_section_name = find_dim(item['题目'])
        question_type = 1 if item['question_type'] == 'A' else 2
        question = item['题目'].replace("{{appellation}}",'').strip()
        ans = item[ans_col(idx)].strip()
        if 1 == question_type:
            # print(i)
            ans = get_ans_content(question_section_name, question, ans)
        eval_result.extend([
            {
            'question_section_name': question_section_name,
            'question_type': question_type,
            'question': question,
            # 'answer': [ans]
            'answer': ans
            }
        ])
    res['eval_result'] = eval_result

    return res

def main(idx):
    req = eval_result(idx)

    import json 
    # print(json.dumps(req,indent=4,ensure_ascii=False))
    
    return req

if __name__ == '__main__':
    import sys
    idx = sys.argv[1]
    main(idx)
