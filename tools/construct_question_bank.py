import json
import math

eng_exam_score = {
    "其他/为参加": 0,
    "其他/未参加": 0,
    "未参加": 0,
    "剑桥英语一级（KET）未通过": 0,
    "剑桥英语一级（KET）及格（Pass）": 60,
    "剑桥英语一级（KET）良好（Merit）": 70,
    "剑桥英语一级（KET）优秀（Distinction）": 80,
    "剑桥英语二级（PET）未通过": 0,
    "剑桥英语二级（PET）及格（Pass）": 75,
    "剑桥英语二级（PET）良好（Merit）": 85,
    "剑桥英语二级（PET）优秀（Distinction）": 90,
    "剑桥英语三级（FCE）C等级（Grade C）": 65,
    "剑桥英语三级（FCE）B等级（Grade B）": 75,
    "剑桥英语三级（FCE）A等级（Grade A）": 85,
    "雅思成绩 < 5.5（IELTS < 5.5）": 70,
    "雅思成绩 5.5–6.0（IELTS 5.5–6.0）": 75,
    "雅思成绩 6.5–7.0（IELTS 6.5–7.0）": 80,
    "雅思成绩≥7.5（IELTS≥7.5）": 90,
    "托福成绩<60（TOEFL iBT<60）": 60,
    "托福成绩60-79（TOEFL iBT 60–79）": 70,
    "托福成绩80-99（TOEFL iBT 80-99）": 80,
    "托福成绩≥100（TOEFL iBT ≥100）": 90
}
    
def eng_exam_score_mapping(ans):
    return eng_exam_score.get(ans.strip(), 0)
   
    
def parse_q_bank(data):
    result = {}

    input = data.get('questions_sections', [])
    for item in input:
        test_dim = item.get('test_questions_section_name', '')
        test_q_list = []
        for q in item.get('questions', []):
            tmp_q = {}
            tmp_q['question'] = q['question_content'].replace("{{appellation}}",'')
            tmp_q['sub_dimention'] = q.get('test_questions_section_name', '')
            # tmp_q['question_type'] = 1 if q['question_type'] == 'A' else 2
            if q['question_type'] == 'A':
                tmp_q['question_type'] = 1
            elif q['question_type'] == 'B':
                tmp_q['question_type'] = 2
            if q['question_type'] == 'C':
                tmp_q['question_type'] = 3
            tmp_q['questions_options'] = {}
            score_rule = {}
            questions_options = q.get('questions_options', [])
            questions_options.sort(key=lambda x : x['value'])
            
            score_interval = 100/(len(questions_options)-1)
            for i in range(len(questions_options)):
                tmp_q['questions_options'][questions_options[i]['label']] = questions_options[i]['value']   
                if tmp_q['question_type'] == 1:
                    if tmp_q['sub_dimention'] == '英语能力':
                        # score_rule[questions_options[i]['value']] = i + 1
                        if '参加过以下英语考试' not in tmp_q['question']:
                            score_rule[questions_options[i]['value']] = math.ceil(i*score_interval)
                        else:
                            score_rule[questions_options[i]['value']] = eng_exam_score_mapping(questions_options[i]['label'])
                    else:
                        score_rule[questions_options[i]['value']] = math.ceil(i*score_interval)

            if tmp_q['question_type'] == 1 and tmp_q['sub_dimention'] != '英语能力':
                tmp_max_score = max([v for k,v in score_rule.items()])
                for key in score_rule:
                    score_rule[key] = tmp_max_score - score_rule[key] 
            
            tmp_q['score_rule'] = score_rule 
            
            test_q_list.extend([tmp_q])
        
        result[test_dim] = test_q_list

    # print(json.dumps(result, indent=4, ensure_ascii=False)) 
    with open('../resource/q_score.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False)

if __name__ == '__main__':
    with open('../resource/试题.json','r') as f:
        data = json.load(f)
    
    parse_q_bank(data)
