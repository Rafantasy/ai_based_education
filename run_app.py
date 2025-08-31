# -*- encoding:utf-8 -*-
from flask import Flask, request, Response
from collections import defaultdict
from importlib import import_module
import sys, time, os, json, re
import logging
from logging.handlers import TimedRotatingFileHandler
import numpy as np
import random
from main import (
    check_input,
    get_growth_advice_rules
)

from tools.load_resource import (
    load_growth_advice_rule
)

# global vars
DB_GROWTH_ADVICE_RULE = None

# init app
app = Flask(__name__)
sys.path.append(os.getcwd())
 
# route
@app.route('/open_question', methods=['POST'])
def produe_open_question_ans():
    res = defaultdict()
 
    if request.json:
        jsonstr = request.json
        # 输入内容校验
        print('input_check_result:',check_input(request.json,'open_question'))
    else:
        logger.error("please check format of request")
        return res 
    
    res = { 
    }   
    
    return Response(json.dumps(res))


@app.route('/instant_profile', methods=['POST'])
def produe_instant_profile():
    res = defaultdict()

    if request.json:
        jsonstr = request.json
        # 输入内容校验
        print('input_check_result:',check_input(request.json,'instant_profile'))
    else:
        logger.error("please check format of request")
        return res
    
    res = {
        "eval_dimension": {
        },
        "english_ablity": {
            "level": "A2",
            "rate": "A"
        },
	    "profile": {
            "profile_type": random.sample(['顶级竞赛科研型人才','社会公众影响型人才','人文艺术型人才','体育竞技型人才'],1)[0],
            "sub_profile_type": random.sample(['顶级竞赛科研型人才','社会公众影响型人才','人文艺术型人才','体育竞技型人才'],1)[0],
            "description": random.sample(['竞赛科研','公众影响','人文艺术','体育竞技'],1)[0]
        },
        "keyword": ['潜力股','有耐力'],
        "academic_direction": ['数学','自然科学'],
        "swot": {
            "strength": "盘同学展现出活跃而稳定的气质，社交适应良好且具备化解冲突的能力，成就导向与内在驱动力强。逻辑清晰、注重细节的思维风格，配合自律坚持的行为倾向，使他在面对挑战时能保持积极心态，抗挫力与乐观情绪为持续成长提供了坚实心理基础。",
            "weakness": "学习动力尚在发展，面对挑战时易显被动，自我驱动意识有待激发；在人际互动中表现较为内敛，主动表达与建立连接的意愿较弱，需更多支持来增强内在信心。",
            "opportunity": "学科基础扎实且成绩突出，具备冲击高阶竞赛与学术挑战的潜力。",
            "threat": "阅读与逻辑思维优势明显，但表达清晰度不足、自信心待增强，可能限制其观点输出与学术交流。"
        }
    }
    
    return Response(json.dumps(res))

 
@app.route('/growth_advice', methods=['POST'])
def produe_growth_advice():
    if request.json:
        # 输入内容校验
        print('input_check_result:',check_input(request.json,'instant_profile'))
    else:
        logger.error("please check format of request")
        return res
    
    ## 生成知识库召回规则
    rules = get_growth_advice_rules(request.json)
    print(json.dumps(rules,indent=4,ensure_ascii=False))

    ## 最终出格式示例 
    res = {
        "本科推荐院校": "美本top10",
        "G1": {
            "学年目标": "适应学校环境，打好语文数学基础",
            "推荐资源": "",
            "应完成的项目": "",
            "升学节点提示": "",
            "延续性建议": "",
            "英语进阶目标": "",
            "特别提醒": ""
        },
        "G12": {
            "学年目标": "积极备考",
            "推荐资源": "提前关注各学校招生简章",
            "应完成的项目": "",
            "升学节点提示": "",
            "延续性建议": "",
            "英语进阶目标": "",
            "特别提醒": ""
        }
    }
    
    return Response(json.dumps(res))


def setup_log(log_name):
    logger = logging.getLogger(log_name)
    log_path = os.path.join('./log/', log_name)
    logger.setLevel(logging.INFO)
    file_handler = TimedRotatingFileHandler(
        filename=log_path, when="MIDNIGHT", interval=1, backupCount=30
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    file_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(process)d] [%(levelname)s] - %(module)s.%(funcName)s (%(filename)s:%(lineno)d) - %(message)s"
        )
    )
    logger.addHandler(file_handler)
    return logger

# 规则库 & 知识库的加载放到这里
def init_resource():
    global DB_GROWTH_ADVICE_RULE
    DB_GROWTH_ADVICE_RULE = load_growth_advice_rule()

if __name__ == '__main__':

    logger = setup_log("test_log")
    
    init_resource()

    app.run('0.0.0.0',port=5001,debug=True)
