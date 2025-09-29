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
    get_open_question_summary,
    get_swot,
    get_profile
)

from tools.load_resource import (
    load_growth_advice_rule
)
# from gen_report import get_report
from gen_report_wo_db import get_report

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
    
    req = request.json
    logger.info(f"open question input req:{req}")
    
    model_res = get_open_question_summary(request.json)
    
    response_validity = 1 
    if len(model_res['潜力亮点']) == 0 and len(model_res['问题点']) == 0:
        response_validity = 0 
        
    return {'response_validity':response_validity, 'potential_highlights':model_res['潜力亮点'], 'defect':model_res['问题点']}
 
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
    req = request.json
    logger.info(f"instant_profile input req:{req}") 
    t_start = time.time()
    res = get_profile(req)
    time_consumed = time.time()-t_start
    id = request.json['student_info']['id']
    logger.info(f"{id}-instant profile generate time:{time_consumed}")
    
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
    
    req = request.json
    logger.info(f"swot-input req is{req}")

    t_start = time.time() 
    res = {
        "swot": get_swot(req)
    }   
    time_consumed = time.time()-t_start
    id = request.json['student_info']['id']
    logger.info(f"{id}-swot generate time:{time_consumed}")
    
    return Response(json.dumps(res))


@app.route('/growth_advice', methods=['POST'])
def produe_growth_advice():
    # if request.json:
    #     # 输入内容校验
    #     print('input_check_result:',check_input(request.json,'growth_advice'))
    # else:
    #     logger.error("please check format of request")
    #     return res
    
    # print('begin to generate rules!')
    # # step1: 生成知识库召回规则
    # t_start = time.time()
    # rules = get_growth_advice_rules(request.json)
    # tmp = json.dumps(rules,indent=4,ensure_ascii=False)
    # # logger.info(f"rules generated:{rules}")
    # time_consumed = time.time()-t_start
    # id = request.json['student_info']['id']
    # logger.info(f"{id}-rules generate time:{time_consumed}")
    # # step2: 知识召回

    # # step3: 内容生成
    # # 最终出格式示例
    # t_start = time.time()
    # res = get_report(rules)
    # time_consumed = time.time()-t_start
    # logger.info(f"{id}-report generate time:{time_consumed}")
    
    req = request.json
    logger.info(f"growth advice-input req is{req}")
    t_start = time.time()
    res = get_report(req)
    time_consumed = time.time()-t_start
    logger.info(f"{id}-report generate time:{time_consumed}")

    return Response(json.dumps(res)) 
    # 输出格式化
    # keys = sorted(list(res.keys()), key=lambda x:x)
    # res_formated = {}
    # for key in keys:
    #     tmp_v = res[key]
    #     if key != '本科推荐院校':
    #         tmp_v = eval(res[key])
    #     res_formated[key] = tmp_v

    # return Response(json.dumps(res_formated))


def setup_log(log_name):
    logger = logging.getLogger(log_name)
    log_path = os.path.join('./log/', log_name)
    logger.setLevel(logging.DEBUG)
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

    logger = setup_log("service_log")
    
    init_resource()

    app.run('0.0.0.0',port=5000,debug=True)
