import pandas as pd
import json
import sys
from input_parse import parse
from score_compute import (
    compute_sub_dim_score,
    compute_profile_score,
    get_profile,
    compute_sub_dim_tag
)
from generate_swot import gen_swot, gen_proposal

# read student info and Q&A data
student_list, eval_qa_list = parse('/Users/rafantasy/Documents/低龄规划项目/5个学生的Mock样本.xlsx')

def main(student_no):
    student_info = student_list[int(student_no)]
    print('***************学生基本信息*****************')
    print(student_info)
    
    qa_data = eval_qa_list[int(student_no)]
    print(qa_data)

    return
    # 计算子维度分数
    sub_dim_score = compute_sub_dim_score(qa_data)
    # print(sub_dim_score)

    # 计算四大画像得分
    profile_score = compute_profile_score(sub_dim_score)
    # print(profile_score)

    # 确定维度标签
    sub_dim_tag = compute_sub_dim_tag(qa_data, sub_dim_score)
    print(json.dumps(sub_dim_tag,indent=4,ensure_ascii=False))

    # 确定画像
    profile = get_profile(profile_score)
    print('\n***************学生画像*****************')
    print(profile)

    # 生成SWOT分析
    gen_swot(student_info, sub_dim_tag, profile)

    # 生成成长建议
    edu_proposal = gen_proposal(student_info, sub_dim_tag, profile)
    print('\n**************成长建议*******************')
    print(edu_proposal)

if __name__ == '__main__':
    main(sys.argv[1])