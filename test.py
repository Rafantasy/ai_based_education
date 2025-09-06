# -*- encoding:utf-8 -*-
import requests
import json

if __name__ == '__main__':
    headers = {'content-type': 'application/json'}
    
    req = {}
    # # 开放问题小结
    # r = requests.post("http://127.0.0.1:5000/open_question", data=json.dumps(req), headers=headers)
    
    # # 人才画像
    r = requests.post("http://127.0.0.1:5000/instant_profile", data=json.dumps(req), headers=headers)
    
    # # swot分析
    # r = requests.post("http://127.0.0.1:5000/swot", data=json.dumps(req), headers=headers)
    
    # # 成长建议
    # r = requests.post("http://127.0.0.1:5000/growth_advice", data=json.dumps(req), headers=headers)
    
    print(r.json())
