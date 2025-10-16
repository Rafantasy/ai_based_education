import pandas as pd
import json
import ast
import asyncio
from datetime import datetime

from call_llm_model import call_model
from profile_desc import get_profile_def

import logging
logger = logging.getLogger("service_log")

import time


prompt_summary = """# 角色
你是一个经验丰富的教育专家，对学生的各种评估维度都理解深刻，且十分擅长低龄升学建议。

# 任务
你的任务是根据学生基本信息，以及学生评测问答结果，生成一份给家长的升学建议。

# 升学建议包含：
*    **✍️ SHAI人才官评语**：一句话说明学生的现状，以及基于现状，怎么达到对应的人才画像要求。
*    **📊 资源与精力分配**：告诉家长为了达到目标，需要在哪方面投入精力，并且给出大致的精力分配占比。
*    **🏫 目标院校池**：根据学生的分档以及目标升学路径，给出5所建议的目标本科院校，并给出推荐理由。

# 生成规则
1. 生成的内容总字数不能超过150字。
2. 学生分档信息适用说明：
   - 如果是“A档”，则推荐符合**目标升学路径**的top类学校；
   - 如果是“B档”，则推荐符合**目标升学路径**的普通类学校；
3. 输出内容里绝对不能包含”A档“，”B档“这样的字眼。
4. 语言简洁，面向家长，避免专业术语。

# 输出格式
请以json格式输出你的分析结果，模板如下：
{
   "✍️ SHAI人才官评语": "xx"
   "📊 资源与精力分配": "xx"
   "🏫 目标院校池": "xx"
}

# 学生基本信息
%s

# 学生评测问答结果
%s

# 你的输出"""



prompt_report_v0 = """# 角色
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
2. 转轨说明：
    - 如果学生**当前学校类型**是公立，但是**升学路径**非中国大陆本科，那么在G6升G7、G8升G9或者G9升G10节点提示转轨国际学校，并推荐合适课程体系（AP/IB/AL，按学科优势匹配）。
    - 转轨的节点只选择一个即可。
3. 如果**人才画像升学规划**要求里要求参加科研类类竞赛，那么要求如下：
    - 若**升学路径**只有中国大陆本科，则优先推荐教育部认可的白名单赛事（如全国中学生学科竞赛五大联赛、**所在城市**对应的省市科技创新大赛）。
    - 若**升学路径**只有海外本科，则优先推荐国际认可赛事（如AMC、AIME、ISEF、NSDA、John Locke Essay）等。
    - 若*升学路径**目标是双轨（既有中国大陆本科，也有海外本科），则两类赛事都需给出：国内白名单作为保底，国际赛事作为亮点。
    - 禁止输出“市级比赛/省级比赛”，或者“参加国际会议”等等泛称，必须写中文全称+主办方。若根据你的知识无法确认，则应该做出提示：“需家长确认本地教育局/协会官网赛事公告”。
4. 需要特别注意：
    - 你生成的规划一定要**明确**，**可落地**，避免空洞的描述；如果有行业公认的评价指标，可以列出详细的目标值。
    - 即使是艺术或者体育类人才画像的学生，生成的规划也要包含学业目标（目标不要定的过高）。
    - 规划要结合学生基本信息里的**升学路径**信息，因此不同的升学路径（比如大陆本科，美国本科，英联邦本科）对学生的要求可能不一致。
    - 每一年级的目标一定要和对应年龄段学生的心智能力相匹配，不能制定不切实际的目标。
5. 输出的规划一定从当前年级开始，一直到12年级（G12）。
6. 语言风格：简洁、家长友好、鼓励性。

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
      "📌 学年定位&目标": "在公立体系保持成绩，同时启动国际学校入学备考（英文+数学），为G9转轨做准备。",
      "🛠️ 战略规划": "⭐核心任务：参加【AMC8 数学竞赛】（美国数学协会主办），检验国际数学基础；参与【深圳市青少年科技创新大赛】（教育局、科协主办，白名单赛事），完成小型科研项目。➕选做：PET英语考试或初阶托福，检测语言水平。",
      "⏰ 时间与家庭协同": "每周固定英文/数学专项训练，家长协助报名AMC8和青创赛。",
      "🏆 关键成果": "AMC8成绩单+深圳青创赛证书；年度标签＝“转轨备考年”。"
}

# 你的输出"""


prompt_report = """# 角色
你是一位十分有经验的教育专家，且专注于低龄升学规划。

# 任务
根据学生基本信息，以及学生当前所属人才画像的升学规划要求，生成一份从当前年级的下一年级开始一直到G12的升学规划。

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
2. 转轨说明：
    - 如果学生**当前学校类型**是公立，但是**升学路径**非中国大陆本科，那么在G8，G9和G10节点提示转轨国际学校。
    - 具体转轨要求：
      - G8：需要提示国际学校备考（英文和数学）；
      - G9：定义为国际学校衔接年，重点是适应，而不是做体系选择；
      - G10：根据成绩和方向推荐合适课程体系（美国=IB/AP，英国IB/AL，需要按学科优势匹配）。
3. 如果**人才画像升学规划**要求里要求参加科研类类竞赛，那么要求如下：
    - 若**升学路径**只有中国大陆本科，则优先推荐教育部认可的白名单赛事（如全国中学生学科竞赛五大联赛、**所在城市**对应的省市科技创新大赛）。
    - 若**升学路径**只有海外本科，则优先推荐国际认可赛事（如AMC、AIME、ISEF、NSDA、John Locke Essay）等。
    - 若**升学路径**目标是双轨（既有中国大陆本科，也有海外本科），则两类赛事都需给出：国内白名单作为保底，国际赛事作为亮点。
    - 禁止输出“市级比赛/省级比赛”，或者“参加国际会议”等不明确的表述，必须给出**具体**且**真实存在**的竞赛或者项目。若根据你的知识无法确认，则应该做出提示：“需家长确认本地教育局/协会官网赛事公告”。
4. 需要特别注意：
    - 你生成的规划一定要**明确**且**可落地**，避免空洞的描述；如果有行业公认的评价指标，可以列出详细的目标值。
    - 即使是艺术或者体育类人才画像的学生，生成的规划也要包含学业目标（目标不要定的过高）。
    - 规划要结合学生基本信息里的**升学路径**信息，因此不同的升学路径（比如大陆本科，美国本科，英联邦本科）对学生的要求可能不一致。
    - 每一年级的目标一定要和对应年龄段学生的心智能力相匹配，不能制定不切实际的目标。
5. 输出的规划一定从当前年级的下一年级开始，一直到12年级（G12）：
    - 比如：当前年级为G5，那么你的规划应该从G6开始，一直到G12。
6. 语言风格：简洁、家长友好、鼓励性。
7. 生成内容中的英文简写后必须加上中文注解，以便不了解相关知识的家长可以看懂。

# 输出要求
1. 只能输出逐年规划，不要输出其它任何无关内容。
2. 输出内容里绝对不能包含”A档“，”B档“这样的字眼。
3. 严格按照JSON格式输出；输出格式模板如下：
{
     "G9": {
          "📌 学年定位&目标":"xx",
          "🛠️ 战略规划":"xx(⭐ 核心任务和➕ 选做两部分内容要换行输出)",
          "⏰ 时间与家庭协同":"xx",
          "🏆 关键成果":"xx"
     },
     "G10": {...},
     "G11": {...},
     "G12": {...}
}

# 你的输出"""

prompt_report_current_grade = """# 角色
你是一位十分有经验的教育专家，且专注于低龄升学规划。

# 任务
根据学生基本信息，以及学生当前所属人才画像的升学规划要求，生成一份当前年级的升学规划。

# 学生基本信息
%s

# 人才画像升学规划要求
%s

# 升学规划生成规则
1. 当前年级的升学包含以下四个要点：
*    **📌 学年定位&目标**：当前学年的规划目标(<=60字)
*    **🛠️ 战略规划**：⭐ 核心任务（2条，最低目标+理想目标，必须可验证），➕ 选做（兴趣/运动/公益等）。(<=100字)
*    **⏰ 时间与家庭协同**：要落实到具体行动(<=70字)
*    **🏆 关键成果**：1–2个硬核证据 + 年度标签；并且要做到逐年级递进。(<=60字)
*    **🚨 近期迫切问题 & 解法**：一句话点出问题 + 2–3条可执行方法 + 时间周期/预期效果；该部分一定要让家长觉得准确，可落地。(<=100字)
*    **🎯 本年度重点目标落地**：目标拆解 + 行动路径 + 检查节点 + 一年后成果；；该部分一定要具有洞察力，让家长觉得有目标感，可落地。(<=120字)
2. 转轨说明：
    - 如果学生**当前学校类型**是公立，但是**升学路径**非中国大陆本科，那么在G6升G7、G8升G9或者G9升G10节点提示转轨国际学校，并推荐合适课程体系（AP/IB/AL，按学科优势匹配）。
    - 转轨的节点只选择一个即可。
3. 如果**人才画像升学规划**要求里要求参加科研类类竞赛，那么要求如下：
    - 若**升学路径**只有中国大陆本科，则优先推荐教育部认可的白名单赛事（如全国中学生学科竞赛五大联赛、**所在城市**对应的省市科技创新大赛）。
    - 若**升学路径**只有海外本科，则优先推荐国际认可赛事（如AMC、AIME、ISEF、NSDA、John Locke Essay）等。
    - 若**升学路径**目标是双轨（既有中国大陆本科，也有海外本科），则两类赛事都需给出：国内白名单作为保底，国际赛事作为亮点。
    - 禁止输出“市级比赛/省级比赛”，或者“参加国际会议”等不明确的表述，必须给出**具体**且**真实存在**的竞赛或者项目。若根据你的知识无法确认，则应该做出提示：“需家长确认本地教育局/协会官网赛事公告”。
4. 需要特别注意：
    - 你生成的规划一定要**明确**且**可落地**，避免空洞的描述；如果有行业公认的评价指标，可以列出详细的目标值。
    - 即使是艺术或者体育类人才画像的学生，生成的规划也要包含学业目标（目标不要定的过高）。
    - 规划要结合学生基本信息里的**升学路径**信息，因此不同的升学路径（比如大陆本科，美国本科，英联邦本科）对学生的要求可能不一致。
    - 年级目标一定要和对应年龄段学生的心智能力相匹配，不能制定不切实际的目标。
6. 语言风格：简洁、家长友好、鼓励性。
7. 生成内容中的英文简写后必须加上中文注解，以便不了解相关知识的家长可以看懂。

# 输出要求
1. 只能输出当前年级规划，不要输出其它任何无关内容。
2. 总字数控制在550字左右。
3. 输出内容里绝对不能包含”A档“，”B档“这样的字眼。
4. 严格按照JSON格式输出；输出格式模板如下：
{
    "📌 学年定位&目标":"xx",
    "🛠️ 战略规划":"xx(⭐ 核心任务和➕ 选做两部分内容要换行输出)",
    "⏰ 时间与家庭协同":"xx",
    "🏆 关键成果":"xx",
    "🚨 近期迫切问题 & 解法":"xx",
    "🎯 本年度重点目标落地":"xx"
}

# 你的输出"""


async def get_instant_report(req):
    loop = asyncio.get_running_loop()
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
    
    model_prompt = prompt_summary % (basic_info, qa_list)
    logger.info(f"instant report prompt is:{model_prompt}")
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": model_prompt},
    ]
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型开始时间{start_time}")

    # result = call_model(messages)
    result = await loop.run_in_executor(None, call_model, messages)

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型结束时间{end_time}")
    
    result = ast.literal_eval(result.replace("```json",'').replace("```",'').strip())
    # print(json.dumps(result,indent=4,ensure_ascii=False))
    return result

async def get_detail_report(req):
    loop = asyncio.get_running_loop()
    with open('./resource/TP_planning.json', 'r') as f:
        TP_PLANNING = json.load(f)
    basic_info = {}
    basic_info['姓名'] = req['student_info']['name']
    basic_info['所在城市'] = req['student_info']['city_location']
    basic_info['当前学校类型'] = req['student_info']['school_type']
    basic_info['当前年级'] = req['student_info']['current_grade']
    basic_info['人才画像类型'] = req['student_info']['profile_type']

    basic_info['分档'] = req['student_info']['rate']
    basic_info['升学路径'] = ','.join(req['student_info']['college_goal_path'])
    basic_info['兴趣学科'] = req['student_info']['subject_interest']
    
     
    logger.info(f"人才画像类型:{basic_info['人才画像类型']}")
    target_plan = [item for item in TP_PLANNING if item['画像代码'] in basic_info['人才画像类型']][0]
    test_keys = list(target_plan.keys())
    logger.info(f"target plan keys:{test_keys}")
    # print('target plan keys:',test_keys)
    # print('test_keys:',test_keys)
    if 'A' in req['student_info']['rate']:
        print('1')
        target_plan.pop('B档升学主线')
    else:
        print('2')
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
 
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型开始时间{start_time}")

    # result = call_model(messages)
    result = await loop.run_in_executor(None, call_model, messages)

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型结束时间{end_time}")
    
    result = ast.literal_eval(result.replace("```json",'').replace("```",'').strip())
    return result


async def get_detail_report_current_grade(req):
    loop = asyncio.get_running_loop()
    with open('./resource/TP_planning.json', 'r') as f:
        TP_PLANNING = json.load(f)
    basic_info = {}
    basic_info['姓名'] = req['student_info']['name']
    basic_info['所在城市'] = req['student_info']['city_location']
    basic_info['当前学校类型'] = req['student_info']['school_type']
    basic_info['当前年级'] = req['student_info']['current_grade']
    basic_info['人才画像类型'] = req['student_info']['profile_type']

    basic_info['分档'] = req['student_info']['rate']
    basic_info['升学路径'] = ','.join(req['student_info']['college_goal_path'])
    basic_info['兴趣学科'] = req['student_info']['subject_interest']
    
     
    logger.info(f"人才画像类型:{basic_info['人才画像类型']}")
    target_plan = [item for item in TP_PLANNING if item['画像代码'] in basic_info['人才画像类型']][0]
    test_keys = list(target_plan.keys())
    logger.info(f"target plan keys:{test_keys}")
    # print('target plan keys:',test_keys)
    # print('test_keys:',test_keys)
    if 'A' in req['student_info']['rate']:
        print('1')
        target_plan.pop('B档升学主线')
    else:
        print('2')
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
    
    model_prompt = prompt_report_current_grade % (basic_info, target_plan)
    logger.info(f"growth advice prompt is:{model_prompt}")
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": model_prompt},
    ]
 
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型开始时间{start_time}")

    # result = call_model(messages)
    result = await loop.run_in_executor(None, call_model, messages)

    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型结束时间{end_time}")
    
    result = ast.literal_eval(result.replace("```json",'').replace("```",'').strip())
    
    res = {
        req['student_info']['current_grade']: result
    }

    return res

async def run_aync_tasks(req): 
    # 初始化任务
    tasks = [get_instant_report(req),get_detail_report_current_grade(req)]
    if req['student_info']['current_grade'] != 'G12':
        tasks.extend([get_detail_report(req)])

    # 执行任务
    results = await asyncio.gather(*tasks)

    return results

def get_report(req):
    model_res = asyncio.run(run_aync_tasks(req))
    
    result = {}
    # result['家长10s通'] = ast.literal_eval(model_res[0].replace("```json",'').replace("```",'').strip())
    # result['升学建议'] = ast.literal_eval(model_res[1].replace("```json",'').replace("```",'').strip())
    
    result['家长10s通'] = model_res[0]
    advices = model_res[1]
    if len(model_res) > 2:
        advices.update(model_res[2])
    result['升学建议'] = advices
    
    return result
    


if __name__ == '__main__':
    from data import proc
    req = {'student_info':{'name': '汤同学', 'gender': '', 'school_type': '公立', 'current_grade': 'G5', 'city_location': '深圳', 'college_goal_path': ['中国大陆本科'], 'id': 904, 'english_level': 'A2', 'rate': 'A', 'subject_interest': '艺术,体育', 'profile_type': 'AJPB｜体育明星 Sports Star 🏅⚽🏌️t'}}
    res = get_report(req)
    print(json.dumps(res,indent=4,ensure_ascii=False))


