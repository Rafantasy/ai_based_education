import pandas as pd
import json
import sys
from input_parse import parse
# from score_compute import (
#     compute_sub_dim_score,
#     compute_profile_score,
#     get_profile,
#     compute_sub_dim_tag
# )
from generate_swot import gen_swot, gen_proposal
from tools.info_check import (
    input_valid_instant_profile,
    input_valid_growth_advice 
)

from tools.load_resource import (
    load_growth_advice_rule
)

def check_input(req, name):
    """输入参数校验"""
    if not isinstance(req, dict):
        return False
    if 'instant_profile' == name:
        return input_valid_instant_profile(req)
    elif 'growth_advice' == name:
        return input_valid_growth_advice(req)
    
    return False

def get_growth_advice_rules(req):
    """生成成长规划生成规则"""

    # 加载原始规则库
    raw_rules = load_growth_advice_rule()
    print(type(raw_rules.iloc[4]['适用年级']))

    res = {}
    res['name'] = req['name']
    res['school_type'] = req['school_type']
    res['current_grade'] = req['current_grade']
    res['profile_type'] = req['profile_type']
    res['rate'] = req['rate']
    res['college_goal_path'] = req['college_goal_path']
    res['subject_interest'] = req['subject_interest']
    res['recall_rules'] = {}
    # 根据年级/画像筛选用于知识库召回的规则
    # 1. 本科推荐学校(每个学生只生成一次)
    res['recall_rules']['university_recommendation'] = {
        'db_name': 'db_A档&B档升学路径对标本科要求知识库',
        'requirement': raw_rules[(raw_rules['人才画像']==res['profile_type']) & (raw_rules['输出子模块（可以大模型自行判断）']=='本科推荐学校列表')].iloc[0]['标准内容/条目（输出）'], 
        'module_name': '本科推荐学校列表' 
    }

    # 2. 其他知识库规则：按年级粒度进行聚合
    db_rules = raw_rules[raw_rules['人才画像']==res['profile_type']]
    grade_num = int(req['current_grade'].split('G')[1])
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
    req = {}
    req['name'] = '李同学'
    req['school_type'] = '公立'
    req['current_grade'] = 'G3'
    req['profile_type'] = '顶级竞赛科研型'
    req['rate'] = 'A档'
    req['college_goal_path'] = '美国本科'
    req['subject_interest'] = '数学'
    
    res = get_growth_advice_rules(req)
    print(json.dumps(res,indent=4,ensure_ascii=False))