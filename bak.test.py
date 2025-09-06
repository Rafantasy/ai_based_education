# -*- encoding:utf-8 -*-
import requests
import json

if __name__ == '__main__':
    headers = {'content-type': 'application/json'}
    
    req = {}
    student_info = {}
    student_info['name'] = '李同学'
    student_info['gender'] = '男'
    student_info['school'] = ''
    student_info['city_location'] = 'SH'
    student_info['school_type'] = '公立'
    student_info['current_grade'] = 'G3'
    student_info['profile_type'] = '顶级竞赛科研型'
    student_info['english_level'] = 'A2'
    student_info['rate'] = 'A档'
    student_info['college_goal_path'] = ['美国本科']
    student_info['subject_interest'] = '数学'
    student_info['id'] = '12345'
    req['student_info'] = student_info
    req['eval_result'] = [
        {
            "question_section_name":"性格特征",
            "question_type":2,
            "question":"如果让你描述一下孩子的性格（优点和短板），你会怎样描述？",
            "answer":"我觉得自己挺开朗的，愿意帮助别人，但有时候太急躁。"
        }
    ]
    # # 开放问题小结
    # r = requests.post("http://127.0.0.1:5000/open_question", data=json.dumps(req), headers=headers)
    
    # # 人才画像
    # r = requests.post("http://127.0.0.1:5000/instant_profile", data=json.dumps(req), headers=headers)
    
    # # swot分析
    # r = requests.post("http://127.0.0.1:5000/swot", data=json.dumps(req), headers=headers)
    
    # # 成长建议
    # r = requests.post("http://127.0.0.1:5000/growth_advice", data=json.dumps(req), headers=headers)
    
    print(r.json())
