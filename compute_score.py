import json


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

# 计算学生英语水平，并进行分档
def rate_classify(req):
    # 读取题库
    with open('q_score.json', 'r') as f:
        q_score = json.load(f)['学业表现']
    
    # 英语测试问题列表
    eng_q_list = [
        '孩子在阅读英文材料时，通常能理解到什么程度？',
        '孩子在日常英文交流中，一般能做到哪种程度？',
        '孩子在英文写作和语法方面，通常能完成到什么水平？',
        # 开放式问题
        '孩子是否参加过以下英语考试？请选择最近一次且成绩最高的一项。'
    ]

    # 找到题目答案 & 计算分数
    eng_ans_list = ['' for x in eng_q_list]
    eng_score_list = [0 for x in eng_q_list]

    qa_list = req.get('eval_result', [])
    for i in range(len(eng_q_list)):
        for item in qa_list:
            if item['question'] == eng_q_list[i]:
                eng_ans_list[i] = item['answer']
        
        for item in q_score:
            if item['question'] == eng_q_list[i]:
                eng_score_list[i] = int(item['score_rule'].get(eng_ans_list[i], 0))

    # 计算英语水平
    eng_level = ''
    score = sum(eng_score_list[0:3])/3
    if 0 == eng_score_list[-1]:
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
    else:
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
    with open('eng.json', 'r') as f:
        eng_requriment = json.load(f)
    
    school_type = 'public_school' if req['school_type'] == '公立' else 'private_school'
    eng_requriment_rule = eng_requriment[school_type]
    for rule in eng_requriment_rule:
        if req['current_grade'] in rule['grade']:
            for tmp_level in rule['cefr_level'].split(','):
                if eng_level >= tmp_level:
                    rate = 'A'

    return eng_level, rate 