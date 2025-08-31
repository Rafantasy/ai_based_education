# -*- encoding:utf-8 -*-
import requests
import json

if __name__ == '__main__':
    headers = {'content-type': 'application/json'}
    pred_data = {}
    pred_data['name'] = '李同学'
    pred_data['gender'] = '男'
    pred_data['school'] = ''
    pred_data['city_location'] = 'SH'
    pred_data['school_type'] = '公立'
    pred_data['current_grade'] = 'G3'
    pred_data['profile_type'] = '顶级竞赛科研型'
    pred_data['sub_profile_type'] = ''
    pred_data['english_level'] = 'A2'
    pred_data['rate'] = 'A档'
    pred_data['college_goal_path'] = '美国本科'
    pred_data['subject_interest'] = '数学'
    pred_data['open_questions_response'] = ''
    pred_data['id'] = '12345'

    r = requests.post("http://127.0.0.1:5000/instant_profile", data=json.dumps(pred_data), headers=headers)
    # r = requests.post("http://127.0.0.1:5000/growth_advice", data=json.dumps(pred_data), headers=headers)
    print(r.json())
