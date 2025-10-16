# -*- encoding:utf-8 -*-

import pandas as pd
import json
import sys
import asyncio
from input_parse import parse

from generate_swot import gen_swot, gen_proposal
from tools.info_check import (
    input_valid_instant_profile,
    input_valid_growth_advice 
)

from tools.load_resource import (
    load_growth_advice_rule
)

from tools.load_talent_evidence import load_evidence
 
from prompt_template import (
    prompt_open_question_summary,
    prompt_subject_interest,
    prompt_swot,
    prompt_instant_report,
    prompt_tp
)

from profile_desc import (
    get_profile_desc,
    get_profile_def,
    get_enrollment_data
)

from call_llm_model import (
    call_model,
    async_call_model,
    run_async_tasks
)

from compute_score import (
    cal_TP_score,
    cal_dg_score,
    cal_learning_score,
    rate_classify
)
import time
import logging
logger = logging.getLogger("service_log")

def handle_grade(req):
    if ('K' in req['student_info']['current_grade']) or ('k' in req['student_info']['current_grade']):
        req['student_info']['current_grade'] = 'G1'
    
    return req

def check_input(req, name):
    """输入参数校验"""
    if not isinstance(req, dict):
        return False
    if 'instant_profile' == name:
        return input_valid_instant_profile(req)
    elif 'growth_advice' == name:
        return input_valid_growth_advice(req)
    
    return False

def get_open_question_summary(req):
    eval_result = req.get('eval_result',[])
    print('eval_result', eval_result)
    if len(eval_result) != 1:
        return {'response_validity':0, 'summary': ''}
    
    dim = eval_result[0]['question_section_name']
    # qa_pair = '问题：' + eval_result[0]['question'] + '\n' + '回答：' + ','.join(eval_result[0]['answer'])
    qa_pair = '问题：' + eval_result[0]['question'] + '\n' + '回答：' + eval_result[0]['answer']
    
    prompt = prompt_open_question_summary % (dim, qa_pair)
    print('open question:', prompt)
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]   
    result = call_model(messages)
    result = json.loads(result.replace("```json",'').replace("```",'').strip())
    
    return result


def test_summary(req):
    req = handle_grade(req)
    logger.info(f"open question input req:{req}")
    model_res = get_open_question_summary(req)
    print(model_res)
    
    response_validity = 1 
    if len(model_res['潜力亮点']) == 0 and len(model_res['问题点']) == 0:
        response_validity = 0 
    
    return {'response_validity':response_validity, 'potential_highlights':model_res['潜力亮点'], 'defect':model_res['问题点']}
 
def get_TP_evidence(req):
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = ','.join(item['answer'])
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    t_start = time.time()
    
    talent_dim_list = ['A_S', 'L_J', 'I_P', 'R_B']
    talent_msg_list = []
    for dim in talent_dim_list:
        print('input dim:', dim, ' Grade', req.get('student_info',{}).get('current_grade',''))
        res_def, res_score = load_evidence(dim, req.get('student_info',{}).get('current_grade',''))

        print('input prompt:', prompt_tp % (res_def, res_score, qa_list))
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_tp % (res_def, res_score, qa_list)},
        ]
        talent_msg_list.extend([(dim, messages)])
    
    # result = async_call_model(talent_msg_list)
    result = asyncio.run(run_async_tasks(talent_msg_list))
    
    t_consumed = time.time() - t_start
    logger.info(f"tp_evidence extract:{t_consumed}")

    return result

def get_subject_interest(req):
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = ','.join(item['answer'])
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_subject_interest % qa_list},
    ]
    result = call_model(messages)
    
    return result


def get_profile(req):
    # TP 评价抽取证据
    tp_evidence = get_TP_evidence(req)
    # tp_evidence = json.loads(tp_evidence.replace("```json",'').replace("```",'').strip())
    # print('tp_evidence:', tp_evidence)
    # tp_score = {}
    # for key in tp_evidence:
    #     tmp_score = sum(v for k,v in tp_evidence[key].items())
    #     tp_score[key] = tmp_score
    
    # 计算TP(Talent Potential)得分和标签
    tp_tendency, tp_score, tp_tag = cal_TP_score(tp_evidence)
    
    # 得到人才倾向分数和描述
    enrollment = get_enrollment_data(tp_tendency, tp_score)

    # 获取人才画像所有属性信息
    profile_def = get_profile_def(tp_tag)

    # 学生感兴趣学科
    subject_interest = get_subject_interest(req)

    # 学生英语水平及分档
    eng_level, rate = rate_classify(req)
    
    # 过渡页内容生成
    instant_report = prod_instant_report(req,subject_interest,profile_def['name'],eng_level)

    # 拼接输出结果
    profile = {
        "profile": profile_def,
        "enrollment": enrollment,
        "english_level": eng_level,
        "rate": rate,
	"subject_interest": subject_interest,
        "instant_report": instant_report
    }

    return profile


def get_swot(req):
    # 生成学生背景信息
    student_info = req.get('student_info',{})
    basic_info = '\n'.join(
        [
            '性别:' + student_info.get('gender',''),
            '学校类型:' + student_info.get('school_type',''),
            '当前年级:' + student_info.get('current_grade',''),
            '所在城市:' + student_info.get('city_location',''),
            '目标升学路径:' + ','.join(student_info.get('college_goal_path',[])),
            '兴趣学科:' + student_info.get('subject_interest',''),
            '人才画像:' + student_info.get('profile_type',''),
            '画像描述:' + get_profile_def(student_info.get('profile_type','')).get('description',''),
            '英语水平:' + student_info.get('english_level','')
        ]
    )

    # 构造评测结果
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = ','.join(item['answer'])
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_swot % (basic_info, qa_list)},
    ]
    result = call_model(messages)
    
    result = json.loads(result.replace("```json",'').replace("```",'').strip())
    
    res = {
        "strength": result['strength'],
        "weakness": result['weakness'],
        "opportunity": result['opportunity'],
        "threat": result['threat']
    }
    return res



def prod_instant_report(req,subject_interest,profile_type,english_level):
    # 生成学生背景信息
    student_info = req.get('student_info',{})
    basic_info = '\n'.join(
        [
            '性别:' + student_info.get('gender',''),
            '学校类型:' + student_info.get('school_type',''),
            '当前年级:' + student_info.get('current_grade',''),
            '所在城市:' + student_info.get('city_location',''),
            '目标升学路径:' + ','.join(student_info.get('college_goal_path',[])),
            '兴趣学科:' + subject_interest,
            '人才画像:' + profile_type,
            '画像描述:' + get_profile_def(profile_type).get('description',''),
            '英语水平:' + english_level
        ]
    )

    # 构造评测结果
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = ','.join(item['answer'])
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_instant_report % (basic_info, qa_list)},
    ]
    result = call_model(messages)
    
    return result

    
def get_instant_report(req):
    # 生成学生背景信息
    student_info = req.get('student_info',{})
    basic_info = '\n'.join(
        [
            '性别:' + student_info.get('gender',''),
            '学校类型:' + student_info.get('school_type',''),
            '当前年级:' + student_info.get('current_grade',''),
            '所在城市:' + student_info.get('city_location',''),
            '目标升学路径:' + ','.join(student_info.get('college_goal_path',[])),
            '兴趣学科:' + student_info.get('subject_interest',''),
            '人才画像:' + student_info.get('profile_type',''),
            '画像描述:' + get_profile_def(student_info.get('profile_type','')).get('description',''),
            '英语水平:' + student_info.get('english_level','')
        ]
    )

    # 构造评测结果
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = ','.join(item['answer'])
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_instant_report % (basic_info, qa_list)},
    ]
    result = call_model(messages)
    
    return result

def get_growth_advice_rules(req):
    """生成成长规划生成规则"""

    # 加载原始规则库
    raw_rules = load_growth_advice_rule()
    print(type(raw_rules.iloc[4]['适用年级']))

    res = {}
    res['name'] = req['student_info']['name']
    res['school_type'] = req['student_info']['school_type']
    res['current_grade'] = req['student_info']['current_grade']
    
    profile_name = ''
    if 'JP' in req['student_info']['profile_type']:
        profile_name = '顶级竞赛科研型'
    elif 'LI' in req['student_info']['profile_type']:
        profile_name = '社会公众影响型'
    elif 'LP' in req['student_info']['profile_type']:
        profile_name = '体育竞技型'
    elif 'JI' in req['student_info']['profile_type']:
        profile_name = '人文艺术型'

    res['profile_type'] = profile_name
    res['rate'] = req['student_info']['rate']
    res['college_goal_path'] = req['student_info']['college_goal_path']
    res['subject_interest'] = req['student_info']['subject_interest']
    res['recall_rules'] = {}
    # 根据年级/画像筛选用于知识库召回的规则
    # 1. 本科推荐学校(每个学生只生成一次)
    print('res_profile_type',res['profile_type'])
    print(raw_rules)
    res['recall_rules']['university_recommendation'] = {
        'db_name': 'db_A档&B档升学路径对标本科要求知识库',
        'requirement': raw_rules[(raw_rules['人才画像'].str.contains(res['profile_type'])) & (raw_rules['输出子模块（可以大模型自行判断）'].str.contains('本科推荐学校列表'))].iloc[0]['标准内容/条目（输出）'], 
        'module_name': '本科推荐学校列表' 
    }

    # 2. 其他知识库规则：按年级粒度进行聚合
    db_rules = raw_rules[raw_rules['人才画像']==res['profile_type']]
    grade_num = int(req['student_info']['current_grade'].split('G')[1])
    db_rules = db_rules[db_rules['适用年级']>=grade_num]

    grade_list = [grade_num + i for i in range(12-grade_num+1)]
    res['recall_rules']['grade_list'] = {}
    for grade in grade_list:
        tmp_rules = db_rules[db_rules['适用年级'] == grade]
        tmp_res = []
        for i in range(len(tmp_rules)):
            tmp_res.extend([
                {
                    'db_name': tmp_rules.iloc[i]['知识库'],
                    'requirement': tmp_rules.iloc[i]['标准内容/条目（输出）'],
                    'module_name': tmp_rules.iloc[i]['输出子模块（可以大模型自行判断）']
                }
            ])
        
        res['recall_rules']['grade_list']['G'+str(grade)] = tmp_res 

    return res

if __name__ == '__main__':
    # profile = get_profile(req)
    # print(json.dumps(profile,indent=4,ensure_ascii=False))
    req = {'student_info': {'name': '小周', 'gender': '女', 'school_type': '私立', 'current_grade': 'G10', 'city_location': '北屯市', 'college_goal_path': ['英联邦本科'], 'id': 'cebc85a5-9ddb-11f0-86aa-0242ac120003'}, 'eval_result': [{'question_section_name': '成就动机', 'question_type': 2, 'question': '请分享一件让孩子最有成就感的事情。', 'answer': '英语'}]}
    test_summary(req)
    # print('begin to generate rules!')
    # # step1: 生成知识库召回规则
    # rules = get_growth_advice_rules(req)
    # tmp = json.dumps(rules,indent=4,ensure_ascii=False)
    
    # step2: 知识召回

    # step3: 内容生成
    # 最终出格式示例 
    # res = get_report(rules)
    # print(json.loads(res))
