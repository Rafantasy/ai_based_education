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
    
# 计算TP得分
def cal_TP_score(tp_evi):
    tp_tendency = {
        "A_S": 'balanced',
        "L_J": 'balanced',
        "I_P": 'balanced',
        "R_B": 'balanced'
    }    
    tp_tag = ''

    tp_score = {
        "A_S": int(100*tp_evi.get('Athletic',0)/(tp_evi.get('Athletic',0)+tp_evi.get('Sedentary',0)+0.0001)),
        "L_J": int(100*tp_evi.get('Leader',0)/(tp_evi.get('Leader',0)+tp_evi.get('Joiner',0)+0.0001)),
        "I_P": int(100*tp_evi.get('Intuitive',0)/(tp_evi.get('Intuitive',0)+tp_evi.get('Practical',0)+0.0001)),
        "R_B": int(100*tp_evi.get('Research',0)/(tp_evi.get('Research',0)+tp_evi.get('Balanced',0)+0.0001))
    }
    
    def score_map(score, dim):
        tag_left = dim.split('_')[0]
        tag_right = dim.split('_')[1]
        if score <= 30:
            return 'strong-right', tag_right
        elif score <= 45:
            return 'mild-right', tag_right
        elif score <= 54:
            return 'balanced', tag_left
        elif score <= 70:
            return 'mild-left', tag_left
        else:
            return 'strong-left', tag_left
    
    # A_S
    tendency,tag = score_map(tp_score['A_S'], 'A_S')
    tp_tendency['A_S'] = tendency
    tp_tag += tag
    # L_J
    tendency,tag = score_map(tp_score['L_J'], 'L_J')
    tp_tendency['L_J'] = tendency
    tp_tag += tag
    # I_P
    tendency,tag = score_map(tp_score['I_P'], 'I_P')
    tp_tendency['I_P'] = tendency
    tp_tag += tag
    # R_B
    tendency,tag = score_map(tp_score['R_B'], 'R_B')
    tp_tendency['R_B'] = tendency
    tp_tag += tag

    return tp_tendency, tp_score, tp_tag

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

def cal_learning_score(req):
    with open('./resource/q_score.json', 'r') as f:
        q_score = json.load(f)
    
    # 评测结果
    qa_list = req.get('eval_result', [])

    def cal_dim_score(dim):
        tmp_q_score = q_score[dim]
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
        return score_actual_mark
    
    # 学业表现得分
    actual_mark_1 = cal_dim_score('学业表现')
    # 学能表现得分
    actual_mark_2 = cal_dim_score('学能表现')
    
    return actual_mark_1, actual_mark_2

# 计算学生测评分数，并进行分档
def rate_classify(req):
    # 英语分数和英语水平
    eng_final_score, eng_final_level = eng_level_classify(req)
    # 学能分数和学业分数
    learning_score_1, learning_score_2 = cal_learning_score(req)
    
    # 最终加权分 
    final_score = 0.35*learning_score_1 + 0.25*learning_score_2 + 0.4*eng_final_score
    
    rate = 'B'
    if final_score >= 60 and learning_score_1 >= 45 and learning_score_2 >= 45 and eng_final_score >=45:
        rate = 'A'
    
    return eng_final_level, rate
    
def eng_level_classify(req):
    # 读取题库
    with open('./resource/q_score.json', 'r') as f:
        q_score = json.load(f)['学业表现']
    with open('./resource/eng_expect_score.json', 'r') as f:
        eng_expect_score = json.load(f)
    
    """
    英语部分得分
    """
    # 英语测试问题列表
    eng_exam_q = '是否参加过以下英语考试？请选择最近一次且成绩最高的一项。'
    eng_q_list = [item for item in q_score if item['sub_dimention']=='英语能力' and item['question']!=eng_exam_q]
    eng_exam_q_list = [item for item in q_score if item['sub_dimention']=='英语能力' and item['question']==eng_exam_q]
    
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
    # 选择题均分
    eng_option_score = sum(eng_score_list)/len(eng_score_list)

    eng_exam_result = 0
    flag_not_pass = 0
    for item in qa_list:
        if common_chars(item['question'],eng_exam_q)/len(set(eng_exam_q)) > 0.9:
            if '未通过' in item['answer'][0]:
                flag_not_pass = 1
            tmp_value = eng_exam_q_list[0]['questions_options'][item['answer'][0]]
            eng_exam_result = int(eng_exam_q_list[0]['score_rule'].get(tmp_value, 0))
            break
    
    eng_raw_score = (eng_option_score+eng_exam_result)/2
    if eng_option_score - eng_exam_result > 15:
        eng_raw_score -= 15

    if req['student_info']['school_type']=='公立':
        eng_raw_score = min(eng_raw_score,eng_exam_result+10)
    else:
        eng_raw_score = min(eng_raw_score,eng_exam_result+12)
    if flag_not_pass:
        eng_raw_score = min(eng_raw_score, 55)-5
    
    expect_info = eng_expect_score.get(req['student_info']['school_type']).get(req['student_info']['current_grade'])
    expect_score = expect_info['score']
    expect_level = expect_info['CEFR']

    score_delta = eng_raw_score-expect_score
    
    # 英语最终得分
    eng_final_score = 0
    if score_delta >= 10:
        eng_final_score = 100
    elif score_delta >= 5:
        eng_final_score = 90
    elif score_delta >= 0:
        eng_final_score = 80
    elif score_delta >= -5:
        eng_final_score = 70
    elif score_delta >= -10:
        eng_final_score = 60
    else:
        eng_final_score = 50
            
    # 英语水平
    eng_final_level = ''
    if eng_final_score >= 60:
        eng_final_level = expect_level
    else:
        grade_num = int(req['student_info']['current_grade'].split('G')[1])
        if grade_num > 1:
            eng_final_level = eng_expect_score.get(req['student_info']['school_type']).get("G"+str(grade_num-1))

    return eng_final_score, eng_final_level
