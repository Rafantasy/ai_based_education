import json
import ast

from utils.func_str import common_chars

import logging
logger = logging.getLogger("service_log")

# 计算TP得分
def cal_TP_score_old(tp_evi):
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


def cal_TP_score(tp_evi):
    print("overall tp evidence:",tp_evi)
    tp_tendency = {
        "A_S": 'balanced',
        "L_J": 'balanced',
        "I_P": 'balanced',
        "R_B": 'balanced'
    }    
    tp_tag = ''
    
    def find_key(target, key_list):
        for key in key_list:
            if target in key:
                return key
        
        return ''

    def cal_tp_score(tp_evi):
        score = {}
        for dim, evi in tp_evi:
            print('*****test dim*********', dim) 
            # evi = json.loads(evi.replace("```json",'').replace("```",'').strip())
            evi = ast.literal_eval(evi.replace("```json",'').replace("```",'').strip())
            evi_str = json.dumps(evi,indent=4,ensure_ascii=False)
            logger.info(f"*************evi is:{evi_str}")
            print("*************evi is:",evi_str)
            tendency_score = []
            key_list = list(evi.keys())

            # key = find_key('强', key_list)
            # tendency_score.extend([sum([int(str(v).replace('分','').strip())for item in evi.get(key, []) for k,v in item.items()])])
            # key = find_key('中', key_list)
            # tendency_score.extend([sum([int(str(v).replace('分','').strip())for item in evi.get(key, []) for k,v in item.items()])])
            # key = find_key('弱', key_list)
            # tendency_score.extend([sum([int(str(v).replace('分','').strip())for item in evi.get(key, []) for k,v in item.items()])])
            # if ((tendency_score[0] > tendency_score[1]) and (tendency_score[0] > tendency_score[2])):
            #     # 明显积极向的维度强
            #     score[dim] = int(100*tendency_score[0]/(tendency_score[0]+tendency_score[2]+0.0001))
            # else:
            #     score[dim] = int(100*tendency_score[0]/(tendency_score[0]+tendency_score[1]+tendency_score[2]+0.0001))
        
            key = find_key('强', key_list)
            tendency_score.append([int(str(v).replace('分','').strip()) for item in evi.get(key, []) for k,v in item.items()])
            key = find_key('中', key_list)
            tendency_score.append([int(str(v).replace('分','').strip()) for item in evi.get(key, []) for k,v in item.items()])
            key = find_key('弱', key_list)
            tendency_score.append([int(str(v).replace('分','').strip()) for item in evi.get(key, []) for k,v in item.items()])
            score_1 = (sum(tendency_score[0])+sum(tendency_score[1]))/(len(tendency_score[0])+len(tendency_score[1]))
            score_2 = sum(tendency_score[2])/len(tendency_score[2])
            score[dim] = int(100*score_1/(score_1+score_2))

        return score
    
    score = cal_tp_score(tp_evi) 
    tp_score = {
        "A_S": score.get("A_S"),
        "L_J": score.get("L_J"),
        "I_P": score.get("I_P"),
        "R_B": score.get("R_B")
    }
    
    def score_map(score, dim):
        tag_left = dim.split('_')[0]
        tag_right = dim.split('_')[1]
        if score <= 30:
            return 'strong-right', tag_right
        elif score <= 45:
            return 'mild-right', tag_right
        elif score <= 54:
            return 'balanced', tag_right
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

# 学业/学能表现多选题
def multi_select_score(qa,q_item):
    with open('./resource/q_score_multi_selection.json', 'r') as f:
        multi_select = json.load(f)

    for tmp_q in multi_select:
        if common_chars(qa['question'],tmp_q)/len(set(qa['question'])) > 0.9:
            # logger.info(f"test ans:{qa['answer'][0]}")
            # print(qa['question'],qa['answer'][0],elem['questions_options'])
            score_actual_mark = 0
            for tmp_a in qa['answer']:
                tmp_value = q_item['questions_options'][tmp_a.strip()]
                print(tmp_a, tmp_value)
                tmp_score = int(multi_select[tmp_q].get(tmp_value, 0))
                logger.info(f"**multi-select-question-{qa['question']}**option-{tmp_a}**score-{tmp_score}")
                print(qa['question'],tmp_a,tmp_score)
                score_actual_mark += tmp_score
            SCORE_LIMIT = multi_select[tmp_q].get('SCORE_LIMIT', 0)
            if SCORE_LIMIT > 0:
                score_actual_mark = min(score_actual_mark, SCORE_LIMIT)
            else:
                score_actual_mark = max(score_actual_mark, SCORE_LIMIT)
            
            print(qa['question'], score_actual_mark)
            return score_actual_mark
    
    return 0
    

def cal_learning_score(req):
    with open('./resource/q_score.json', 'r') as f:
        q_score = json.load(f)
    
    # 评测结果
    qa_list = req.get('eval_result', [])

    def cal_dim_score(dim):
        tmp_q_score = q_score[dim]
        score_actual_mark = 0
        full_mark = 0
        multi_qa = []

        for elem in tmp_q_score:
            # 暂时不计入英语能力部分 & 开放试题的分数
            if elem['sub_dimention'] == '英语能力':
                continue
            if elem['question_type'] == 2:
                continue
            
            tmp_q = elem['question']
            # if '老师常提醒' in tmp_q:
            # logger.info(f"cal_learning_score: raw question is {tmp_q}")
                 
            tmp_score_rule = elem['score_rule']
            for qa in qa_list:
                # if common_chars(qa['question'],tmp_q)/len(set(tmp_q)) > 0.9:
                # if '老师常提醒' in qa['question']:
                #     # logger.info(f"cal_learning_score: ratio is {common_chars(qa['question'],tmp_q)/len(set(qa['question']))}")
                #     print('test')
                if elem['question_type'] == 1:
                    if common_chars(qa['question'],tmp_q)/len(set(qa['question'])) > 0.9:
                        # logger.info(f"test ans:{qa['answer'][0]}")
                        # print(qa['question'],qa['answer'][0],elem['questions_options'])
                        tmp_value = elem['questions_options'][qa['answer'][0].strip()]
                        tmp_score = int(tmp_score_rule.get(tmp_value, 0))
                        logger.info(f"{dim}**question-{qa['question']}**score-{tmp_score}")
                        score_actual_mark += tmp_score
                        full_mark += 100
                else:
                    if common_chars(qa['question'],tmp_q)/len(set(qa['question'])) > 0.9:
                        # 多选题调整总分
                        score_actual_mark += multi_select_score(qa, elem)
                        logger.info(f"**multi-select-question-{qa['question']}**sum_score-{score_actual_mark}")

                
        return score_actual_mark,full_mark
    
    # 学业表现得分
    actual_mark_1,full_mark_1 = cal_dim_score('学业表现')
    # 学能表现得分
    actual_mark_2,full_mark_2 = cal_dim_score('学能表现')
    
    return int(100*actual_mark_1/(full_mark_1+0.0001)), int(100*actual_mark_2/(full_mark_2+0.0001))

# 计算学生测评分数，并进行分档
def rate_classify(req):
    # 英语分数和英语水平
    eng_final_score, eng_final_level = eng_level_classify(req)
    # 学能分数和学业分数
    learning_score_1, learning_score_2 = cal_learning_score(req)
 
    # 最终加权分 
    final_score = 0.35*learning_score_1 + 0.25*learning_score_2 + 0.4*eng_final_score

    logger.info(f"加权总分:{final_score}**学业表现分数:{learning_score_1},学能表现分数:{learning_score_2},英语分数:{eng_final_score}")    
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
    print('debug:eng_q_list', eng_q_list)
    eng_exam_q_list = [item for item in q_score if item['sub_dimention']=='英语能力' and item['question']==eng_exam_q]
    
    # 找到题目答案 & 计算分数
    eng_ans_list = ['' for x in eng_q_list]
    eng_score_list = [0 for x in eng_q_list]

    qa_list = req.get('eval_result', [])
    for i in range(len(eng_q_list)):
        for item in qa_list:
            # if common_chars(item['question'],eng_q_list[i]['question'])/len(set(eng_q_list[i]['question'])) > 0.9:
            # if common_chars(item['question'],eng_q_list[i]['question'])/len(set(item['question'])) > 0.9:
            if common_chars(item['question'],eng_q_list[i]['question'])/len(set(eng_q_list[i]['question'])) > 0.98:
                # if '在阅读理解英文时，通常能理解到什么' in item['question']:
                eng_ans_list[i] = item['answer'][0]
                tmp_value = eng_q_list[i]['questions_options'][item['answer'][0].strip()]
                # print('match:', i, item, eng_q_list[i])
                print(tmp_value, eng_q_list[i]['score_rule'])
                eng_score_list[i] = int(eng_q_list[i]['score_rule'].get(tmp_value, 0))
                break
    # 选择题均分
    print('debug:eng_score_list:',eng_score_list)
    eng_option_score = sum(eng_score_list)/len(eng_score_list)

    eng_exam_result = 0
    flag_not_pass = 0
    for item in qa_list:
        # if common_chars(item['question'],eng_exam_q)/len(set(eng_exam_q)) > 0.9:
        if common_chars(item['question'],eng_exam_q)/len(set(item['question'])) > 0.9:
            if '未通过' in item['answer'][0]:
                flag_not_pass = 1
            tmp_value = eng_exam_q_list[0]['questions_options'][item['answer'][0].strip()]
            print('exam value:', tmp_value, eng_exam_q_list[0])
            eng_exam_result = int(eng_exam_q_list[0]['score_rule'].get(tmp_value, 0))
            break
    
    print('debug:eng_option_score:',eng_option_score,'eng_exam_result:',eng_exam_result)
    eng_raw_score = (eng_option_score+eng_exam_result)/2
    if eng_option_score - eng_exam_result > 15:
        eng_raw_score -= 15

    if req['student_info']['school_type']=='公立':
        eng_raw_score = min(eng_raw_score,eng_exam_result+10)
    else:
        eng_raw_score = min(eng_raw_score,eng_exam_result+12)
    if flag_not_pass:
        eng_raw_score = min(eng_raw_score, 55)-5
    
    tmp_school_type = req['student_info']['school_type']
    tmp_grade = req['student_info']['current_grade']

    expect_info = eng_expect_score.get(req['student_info']['school_type']).get(req['student_info']['current_grade'])
    expect_score = expect_info['score']
    expect_level = expect_info['CEFR']

    score_delta = eng_raw_score-expect_score
    
    # 英语最终得分
    print('debug: eng_raw_score:',eng_raw_score,'expect_score:',expect_score)
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
    def get_eng_level(eng_raw_score):
        eng_score_rule_config = eng_expect_score.get(req['student_info']['school_type'])
        eng_score_rule = [v for k,v in eng_score_rule_config.items()]
        eng_score_rule.sort(key=lambda x:x['score'], reverse=True)
        
        for rule in eng_score_rule:
            if eng_raw_score >= rule['score']:
                return rule['CEFR']
        
        return 'Pre-A1（英语启蒙阶段）'

    # eng_final_level = ''
    # if eng_final_score >= 60:
    #     eng_final_level = expect_level
    # else:
    #     grade_num = int(req['student_info']['current_grade'].split('G')[1])
    #     print('grade_num:', grade_num)
    #     if grade_num > 1:
    #         eng_final_level = eng_expect_score.get(req['student_info']['school_type']).get("G"+str(grade_num-1)).get('CEFR','')
        
    # if '' == eng_final_level:
    #     eng_final_level = 'Pre-A1（英语启蒙阶段）'
    #     logger.info(f"use default english level because of low eng_eval_score")
    eng_final_level = get_eng_level(eng_raw_score)
        
    return eng_final_score, eng_final_level


if __name__ == '__main__':
    from data import proc
    # req = proc.main(3)

    req = {'student_info': {'name': '宋晓丹', 'gender': '女', 'school_type': '私立', 'current_grade': 'G2', 'city_location': '长春市', 'college_goal_path': ['中国大陆本科', '英联邦本科', '其他国际本科'], 'id': '22583d13-a8a4-11f0-978e-0242ac120003'}, 'eval_result': [{'question_section_name': '体育艺术', 'question_type': 1, 'question': '孩子是否喜欢体育运动？', 'answer': ['只有体育课才运动']}, {'question_section_name': '专注力', 'question_type': 1, 'question': '学习时，孩子的专注程度是？', 'answer': ['大多数能专注']}, {'question_section_name': '写作能力', 'question_type': 1, 'question': '写语文作文时，孩子的表现如何？', 'answer': ['老师常当范文，写得特别好']}, {'question_section_name': '数理思维', 'question_type': 1, 'question': '孩子数学成绩表现更常是？', 'answer': ['经常在 90% 以上（优秀）']}, {'question_section_name': '检查习惯', 'question_type': 1, 'question': '做题时，孩子是否会检查？', 'answer': ['经常检查']}, {'question_section_name': '时间管理', 'question_type': 1, 'question': '孩子的时间管理习惯是？', 'answer': ['能规划并执行']}, {'question_section_name': '协作力', 'question_type': 1, 'question': '孩子在和小伙伴相处时，更常见的表现是？', 'answer': ['带头小领导，喜欢组织大家']}, {'question_section_name': '公共表达', 'question_type': 1, 'question': '孩子在公众场合发言时，更像？', 'answer': ['在公共场合自信大方，全场焦点']}, {'question_section_name': '创造力', 'question_type': 1, 'question': '当遇到需要创新的作业时，孩子会？', 'answer': ['点子多，喜欢尝试不同方法']}, {'question_section_name': '解决问题能力', 'question_type': 1, 'question': '当面对复杂问题时，孩子更常？', 'answer': ['尝试一步步推理']}, {'question_section_name': '社会认知', 'question_type': 1, 'question': '孩子平时会不会关心新闻或身边发生的大事？', 'answer': ['很关心，经常主动和别人讨论']}, {'question_section_name': '探索力', 'question_type': 1, 'question': '孩子是否参加过学科类实践/社会公益活动？', 'answer': ['有过短暂尝试']}, {'question_section_name': '学术竞争力', 'question_type': 1, 'question': '孩子是否参加过学科类竞赛/学术探究活动？', 'answer': ['没有']}, {'question_section_name': '学习习惯', 'question_type': 1, 'question': '孩子是否会主动预习/复习？', 'answer': ['经常主动']}, {'question_section_name': '体育艺术', 'question_type': 1, 'question': '孩子是否有长期参与某项运动的专业训练？', 'answer': ['没有长期坚持']}, {'question_section_name': '体育艺术', 'question_type': 1, 'question': '孩子是否参加过体育比赛或获得奖项？', 'answer': ['没有参加过']}, {'question_section_name': '体育艺术', 'question_type': 1, 'question': '孩子在艺术（音乐/美术/舞蹈/表演等）方面的兴趣如何？', 'answer': ['偶尔参与']}, {'question_section_name': '体育艺术', 'question_type': 1, 'question': '孩子是否有长期学习/训练艺术类项目？', 'answer': ['没有系统学习']}, {'question_section_name': '体育艺术', 'question_type': 1, 'question': '孩子是否获得过艺术类（音乐/美术/舞蹈/戏剧等）奖项/证书？', 'answer': ['培训机构/兴趣班颁发']}, {'question_section_name': '家庭陪伴', 'question_type': 1, 'question': '父母是否经常陪伴孩子？', 'answer': ['偶尔陪伴']}, {'question_section_name': '亲子沟通', 'question_type': 1, 'question': '孩子与父母的沟通频率是？', 'answer': ['一个月聊几次']}, {'question_section_name': '孩子期望', 'question_type': 1, 'question': '孩子自己对未来最大的期待是？', 'answer': ['考入理想学校']}, {'question_section_name': '家长期望', 'question_type': 1, 'question': '父母对孩子未来的最大期望是？（最多选3项）', 'answer': ['学习成绩好，考上名校', '综合发展，德智体美全面', '健康快乐，心态阳光', '出国留学，开阔眼界', '有稳定工作（如公务员/教师/医生）']}, {'question_section_name': '孩子未来愿景', 'question_type': 2, 'question': '孩子有什么梦想吗？', 'answer': ['孩子梦想成为外交官，想去联合国工作']}, {'question_section_name': '潜力意向', 'question_type': 1, 'question': '如果给未来的孩子一个“魔法选择”，最希望拥有的能力是？', 'answer': ['说话有力量（能带动大家、很有影响力）']}, {'question_section_name': '学科兴趣', 'question_type': 1, 'question': '孩子最喜欢的学科是？', 'answer': ['英语/外语']}, {'question_section_name': '团队角色', 'question_type': 1, 'question': '孩子在和同伴合作时，更像是？', 'answer': ['主动组织者']}, {'question_section_name': '社交表达', 'question_type': 1, 'question': '在公众场合，孩子更可能？', 'answer': ['踊跃发言']}, {'question_section_name': '情绪调节', 'question_type': 1, 'question': '当孩子面对批评时，更可能？', 'answer': ['表面接受但心里别扭']}, {'question_section_name': '毅力', 'question_type': 1, 'question': '孩子是否容易坚持完成一件事？', 'answer': ['总是坚持到底']}, {'question_section_name': '适应力', 'question_type': 1, 'question': '在陌生环境，孩子的适应速度是？', 'answer': ['很快适应']}, {'question_section_name': '团队角色', 'question_type': 1, 'question': '孩子在团队中更像？', 'answer': ['领导型']}, {'question_section_name': '自律习惯', 'question_type': 1, 'question': '在生活习惯上，孩子更像？', 'answer': ['自律规律', '偶尔需要提醒']}, {'question_section_name': '自我认知（优势）', 'question_type': 1, 'question': '孩子最大的 3 个性格优点是？（请选择 3 个）', 'answer': ['乐观开朗', '自信勇敢', '有责任心']}, {'question_section_name': '自我认知（短板）', 'question_type': 1, 'question': '孩子最需要改的 3 个性格缺点是？（请选择 3 个）', 'answer': ['固执', '犟脾气', '爱生气']}, {'question_section_name': '成就动机', 'question_type': 2, 'question': '请分享一件让孩子最有成就感的事情。', 'answer': ['他在班级里担任班长']}, {'question_section_name': '学科水平', 'question_type': 1, 'question': '孩子平时成绩大致在哪个水平？', 'answer': ['班级前10%']}, {'question_section_name': '性格韧性', 'question_type': 1, 'question': '当孩子遇到困难时，更常见的反应是？', 'answer': ['主动想办法解决']}, {'question_section_name': '偏科情况', 'question_type': 1, 'question': '孩子是否存在“偏科”？', 'answer': ['文科强、数理弱']}, {'question_section_name': '学业稳定度', 'question_type': 1, 'question': '最近一次重要考试，孩子的表现是？', 'answer': ['正常发挥']}, {'question_section_name': '补习情况', 'question_type': 1, 'question': '孩子参加了多少学科补习班？', 'answer': ['2 个（学科补习班/家教）']}, {'question_section_name': '目标感', 'question_type': 1, 'question': '孩子对自己未来3–5年的学习目标有想法吗？', 'answer': ['很清楚，知道要做到什么（比如考好成绩、学会新本领）']}, {'question_section_name': '作业态度', 'question_type': 1, 'question': '完成作业时，孩子的态度是？', 'answer': ['主动完成，不用催']}, {'question_section_name': '老师评价（优点）', 'question_type': 1, 'question': '老师平时评价孩子的学习有哪些优点？（最多3个）', 'answer': ['上课专心', '作业认真', '乐于发言']}, {'question_section_name': '老师评价（短板）', 'question_type': 1, 'question': '老师常提醒孩子哪些方面需要改进？（最多3个）', 'answer': ['缺少耐心', '成绩不稳', '粗心大意']}, {'question_section_name': '英语能力', 'question_type': 1, 'question': '孩子在阅读理解英文时，通常能理解到什么程度？', 'answer': ['能读较长（600词），能推断和简单判断']}, {'question_section_name': '英语能力', 'question_type': 1, 'question': '孩子在日常英文交流中，一般能做到哪种程度？', 'answer': ['能描述经历和观点，听懂正常语速']}, {'question_section_name': '英语能力', 'question_type': 1, 'question': '孩子写英文时，能写到什么程度？', 'answer': ['能写120–180词的作文/邮件']}, {'question_section_name': '英语能力', 'question_type': 1, 'question': '孩子是否参加过以下英语考试？请选择最近一次且成绩最高的一项。', 'answer': ['剑桥英语二级（PET）及格（Pass）']}]}
    eng_score, eng_level = eng_level_classify(req)
    print(eng_score, eng_level)
