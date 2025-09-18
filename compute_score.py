import json
from utils.func_str import common_chars

# 计算LARS得分
def cal_lars_score(lars_evi, enrollment):
    # LS
    if enrollment['L'] == 0 and enrollment['S'] == 0:
       enrollment['L'] = 50
       enrollment['S'] = 50
    else: 
        enrollment['L'] = int(100*lars_evi['L']/(lars_evi['L']+lars_evi['S']))
        enrollment['S'] = 100 - enrollment['L']

    # AR
    if enrollment['A'] == 0 and enrollment['R'] == 0:
       enrollment['A'] = 50
       enrollment['R'] = 50
    else:
        enrollment['A'] = int(100*lars_evi['A']/(lars_evi['A']+lars_evi['R']))
        enrollment['R'] = 100 - enrollment['A']
    
    
def cal_dg_score(college_goal_path, enrollment):
    if ['中国大陆本科'] == college_goal_path:
        enrollment['D'] = 100 
        enrollment['G'] = 0
    elif '中国大陆本科' not in college_goal_path:
        enrollment['D'] = 0 
        enrollment['G'] = 100
    else:
        enrollment['D'] = 30 
        enrollment['G'] = 7

def cal_learning_score(req, rate, enrollment):
    with open('./resource/q_score.json', 'r') as f:
        q_score = json.load(f)
    
    # 评测结果
    qa_list = req.get('eval_result', [])

    def cal_dim_score(dim):
        tmp_q_score = q_score[dim]
        score_full_mark = 0
        score_actual_mark = 0
        for elem in tmp_q_score:
            # 暂时不计入英语能力部分 & 开放试题的分数
            if elem['sub_dimention'] == '英语能力':
                continue
            if elem['question_type'] == 2:
                continue

            tmp_q = elem['question']
            tmp_score_rule = elem['score_rule']
            for qa in qa_list:
                if common_chars(qa['question'],tmp_q)/len(set(tmp_q)) > 0.9:
                    tmp_value = elem['questions_options'][qa['answer'][0]]
                    score_actual_mark += int(tmp_score_rule.get(tmp_value, 0))
            tmp_max_score = 0
            for k,v in tmp_score_rule.items():
                if int(v) > tmp_max_score:
                    tmp_max_score = int(v)
            score_full_mark += tmp_max_score
        
        return score_full_mark, score_actual_mark
    
    # 学业表现得分
    full_mark_1, actual_mark_1 = cal_dim_score('学业表现')
    # 学能表现得分
    full_mark_2, actual_mark_2 = cal_dim_score('学能表现')
    
    elite_score = (actual_mark_1+actual_mark_2)/(full_mark_1+full_mark_2+0.00001)
    if rate == 'A':
        if elite_score >= 0.8:
            enrollment['E'] = 80
            enrollment['B'] = 20
        elif elite_score >= 0.65:
            enrollment['E'] = 65
            enrollment['B'] = 35
        elif elite_score >= 0.5:
            enrollment['E'] = 55
            enrollment['B'] = 45
        else:
            enrollment['E'] = 50
            enrollment['B'] = 50
    elif rate == 'B':
        if elite_score >= 0.8:
            enrollment['E'] = 50
            enrollment['B'] = 50
        elif elite_score >= 0.65:
            enrollment['E'] = 45
            enrollment['B'] = 55
        elif elite_score >= 0.5:
            enrollment['E'] = 35
            enrollment['B'] = 65
        else:
            enrollment['E'] = 20
            enrollment['B'] = 80


# 计算学生测评分数，并进行分档
def rate_classify(req):
    # 读取题库
    with open('./resource/q_score.json', 'r') as f:
        q_score = json.load(f)['学业表现']
    
    # 英语测试问题列表
    eng_exam_q = '是否参加过以下英语考试？请选择最近一次且成绩最高的一项。'
    eng_q_list = [item for item in q_score if item['sub_dimention']=='英语能力' and item['question']!=eng_exam_q]
    
    # 找到题目答案 & 计算分数
    eng_ans_list = ['' for x in eng_q_list]
    eng_score_list = [0 for x in eng_q_list]

    qa_list = req.get('eval_result', [])
    for i in range(len(eng_q_list)):
        for item in qa_list:
            if common_chars(item['question'],eng_q_list[i]['question'])/len(set(eng_q_list[i]['question'])) > 0.9:
                eng_ans_list[i] = item['answer'][0]
                tmp_value = eng_q_list[i]['questions_options'][item['answer'][0]]
                eng_score_list[i] = int(eng_q_list[i]['score_rule'].get(tmp_value, 0))
    
    eng_exam_result = ''
    for item in qa_list:
        if common_chars(item['question'],eng_exam_q)/len(set(eng_exam_q)) > 0.9:
            exam_flag = 1
            tm_ans_list = item['answer']
            for ans in tm_ans_list:
                if '其他/为参加' in ans:
                    exam_flag = 0
                    break
            if exam_flag:
                eng_exam_result = ','.join(tm_ans_list)
            break
                
            
    # 计算英语水平
    eng_level = ''
    score = sum(eng_score_list)/len(eng_score_list)
    # TODO:更新英文水平
    # if '' == eng_exam_result:
    #     if score < 1.5:
    #         eng_level = 'A1'
    #     elif score < 2.5:
    #         eng_level = 'A2'
    #     elif score <3.5:
    #         eng_level = 'B1'
    #     elif score < 4.5:
    #         eng_level = 'B2'
    #     else:
    #         eng_level = 'C1'
    
    if score < 1.5:
        eng_level = 'A1'
    elif score < 2.5:
        eng_level = 'A2'
    elif score <3.5:
        eng_level = 'B1'
    elif score < 4.5:
        eng_level = 'B2'
    else:
        eng_level = 'C1'
    # 根据英语水平进行分档
    rate = 'B'
    with open('./resource/eng.json', 'r') as f:
        eng_requriment = json.load(f)
    
    student_info = req.get('student_info', {}) 
    school_type = 'public_school' if student_info['school_type'] == '公立' else 'private_school'
    eng_requriment_rule = eng_requriment[school_type]
    for rule in eng_requriment_rule:
        if student_info['current_grade'] in rule['grade']:
            for tmp_level in rule['cefr_level'].split(','):
                if eng_level >= tmp_level:
                    rate = 'A'

    return eng_level, rate 
