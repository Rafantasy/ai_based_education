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
    get_growth_advice_rules,
    get_open_question_summary
)

from tools.load_resource import (
    load_growth_advice_rule
)
from gen_report import get_report

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
    
    logger.info('input req:', request.json)
    logger.info('input req type:', type(request.json))
    
    logger.info('begin call model')
    res = get_open_question_summary(request.json)
    
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
	"profile": {
            "name": random.sample(['LRDE 倡导者 📚'],1)[0],
            "english_name": "Orator",
            "definition": "以科研推动社会进步的学术先锋。",
            "description": "逻辑推理强，具备科研热情与长远视野，常参加数理/科研竞赛。",
            "major": "商科,理科",
            "college": "美本USNews前20",
            "hof":[
		{
			"name_education":"杨振宁（清华大学物理学 → 芝加哥大学博士）",
			"major_event":"国内顶尖+国际科研深造路径，诺贝尔奖得主。"
		},
		{
			"name_education":"屠呦呦（北京医学院 → 中医药研究院）",
			"major_event":"国内科研体系代表，国际影响力。"
		},
		{
			"name_education":"埃隆·马斯克（宾夕法尼亚大学物理+沃顿商学院）",
			"major_event":"跨学科科研冲顶型典范，AI/新能源/跨界探索者。"
		}
	    ]
        },
        "enrollment": {
            "L": 100,
            "S": 0,
            "A": 50,
            "R": 50,
            "D": 60,
            "G": 40,
            "E": 0,
            "B": 100,
	    "explanation":"孩子在公众表达与组织中表现较突出(L65%),同时在科研理性方向有明显优势(R 80%),路径选择为国际(G70%)，倾向冲顶型(E65%)"
        },
        "english_level": "A1",
        "rate": "A",
	"subject_interest": "数学"
    }
    
    return Response(json.dumps(res))

 
@app.route('/swot', methods=['POST'])
def produe_swot():
    res = defaultdict()
 
    if request.json:
        jsonstr = request.json
        # 输入内容校验
        # print('input_check_result:',check_input(request.json,'swot'))
    else:
        logger.error("please check format of request")
        return res 
    
    res = {
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
        print('input_check_result:',check_input(request.json,'growth_advice'))
    else:
        logger.error("please check format of request")
        return res
    
    ## step1: 生成知识库召回规则
    # rules = get_growth_advice_rules(request.json)
    # tmp = json.dumps(rules,indent=4,ensure_ascii=False)
    # print(f"tmp is: \n{rules['name']}")
    
    ## step2: 知识召回

    ## step3: 内容生成
    ## 最终出格式示例 
    # res = get_report(rules)
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

    app.run('0.0.0.0',port=5000,debug=True)
