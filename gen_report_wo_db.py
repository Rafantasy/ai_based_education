import pandas as pd
import json
from call_llm_model import call_model

import logging
logger = logging.getLogger("service_log")

import time

with open('./resource/TP_planning.json', 'r') as f:
    TP_PLANNING = json.load(f)

prompt_report = """# 角色
你是一位十分有经验的教育专家，且专注于低龄升学规划。

# 任务
根据学生基本信息，以及学生当前所属人才画像的升学规划要求，生成一份从当前年级一直到G12的升学规划。

# 学生基本信息
%s

# 人才画像升学规划要求
%s

# 升学规划生成规则
1. 每一年级的升学包含以下四个要点：
*    **📌 学年定位&目标**：每一学年的规划目标
*    **🛠️ 战略规划**：⭐ 核心任务（2条，最低目标+理想目标，必须可验证），➕ 选做（兴趣/运动/公益等）。
*    **⏰ 时间与家庭协同**：要落实到具体行动
*    **🏆 关键成果**：1–2个硬核证据 + 年度标签；并且要做到逐年级递进。
2. 需要特别注意：
    - 你生成的规划一定要**明确**，**可落地**，避免空洞的描述；如果有行业公认的评价指标，可以列出详细的目标值。
    - 即使是艺术或者体育类人才画像的学生，生成的规划也要包含学业目标（目标不要定的过高）。
    - 规划要结合学生基本信息里的**升学路径**信息，因此不同的升学路径（比如大陆本科，美国本科，英联邦本科）对学生的要求可能不一致。
3. 每一年级的目标一定要和对应年龄段学生的心智能力相匹配，不能制定不切实际的目标。
4. 输出的规划一定从当前年级开始，一直到12年级（G12）。
5. 语言风格：简洁、家长友好、鼓励性。

# 输出要求
1. 只能输出逐年规划，不要输出其它任何无关内容。
2. 严格按照JSON格式输出；输出格式模板如下：
{
     "G9": {
           "📌 学年定位&目标":xx,
          "🛠️ 战略规划":xx,
          "⏰ 时间与家庭协同":xx,
          "🏆 关键成果"
     },
     "G10": {...},
     "G11": {...},
     "G12": {...}
}

# 输出示例
下面是某一个年级的输出示例：
{
      "📌 学年定位&目标": "提升英语表达，开始累积国际项目。",
      "🛠️ 战略规划": "⭐核心任务：雅思首测5.5（最低）/6.0（理想）；参加一次国际夏令营（最低结业证书，理想发表展示作品）。
 ➕选做：加入编程/设计社团，完成小型游戏作品。",
      "⏰ 时间与家庭协同": "父母需安排海外夏校预算。",
      "🏆 关键成果": "英语成绩+夏校证明；年度标签＝“国际起步年”。"
}

# 你的输出"""


def get_report(req):
    basic_info = {}
    basic_info['姓名'] = req['student_info']['name']
    # basic_info['school_type'] = req['student_info']['school_type']
    basic_info['当前年级'] = req['student_info']['current_grade']
    basic_info['人才画像类型'] = req['student_info']['profile_type']

    basic_info['分档'] = req['student_info']['rate']
    basic_info['升学路径'] = ','.join(req['student_info']['college_goal_path'])
    basic_info['兴趣学科'] = req['student_info']['subject_interest']
    
     
    logger.info(f"人才画像类型:{basic_info['人才画像类型']}")
    target_plan = [item for item in TP_PLANNING if item['画像代码'] in basic_info['人才画像类型']][0]
    if 'A' in req['student_info']['rate']:
        target_plan.pop('B档升学主线')
    else:
        target_plan.pop('A档升学主线')
    
    raw_path_points = target_plan['升学路径适配要点'] 
    target_plan['升学路径适配要点'] = {}
    for x in req['student_info']['college_goal_path']:
        logger.info(f"college_goal_path:{x}")
        target_plan['升学路径适配要点'][x] = [v for k,v in raw_path_points.items() if x in k][0]

    basic_info = json.dumps(basic_info,indent=4,ensure_ascii=False)
    # print(basic_info)

    target_plan = json.dumps(target_plan,indent=4,ensure_ascii=False)
    # print(target_plan)
    
    model_prompt = prompt_report % (basic_info, target_plan)
    logger.info(f"growth advice prompt is:{model_prompt}")
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": model_prompt},
    ]
 
    result = call_model(messages)
    
    result = json.loads(result.replace("```json",'').replace("```",'').strip())
    return result


if __name__ == '__main__':
    req = {'student_info': {'name': '拜访拜访你', 'gender': '男', 'school_type': '公立', 'current_grade': 'G12', 'city_location': '乌海>市', 'college_goal_path': ['中国大陆本科'], 'id': 'e3c7fc82-9abd-11f0-86aa-0242ac120003', 'english_level': 'B2', 'rate': 'A', 'subject_interest': '艺术/体育类', 'profile_type': 'SJIB｜文艺家Humanist & Artist 🎨📚🎶'}} 
    # print(req)
    get_report(req)
