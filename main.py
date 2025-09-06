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

from prompt_template import (
    prompt_open_question_summary,
    prompt_lars,
    prompt_subject_interest,
    prompt_swot
)

from profile_desc import (
    get_profile_desc,
    get_profile_def
)

from call_llm_model import (
    call_model
)

from compute_score import (
    cal_lars_score,
    cal_dg_score,
    rate_classify
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

def get_open_question_summary(req):
    eval_result = req.get('eval_result',[])
    print('eval_result', eval_result)
    if len(eval_result) != 1:
        return {'response_validity':0, 'summary': ''}
    
    dim = eval_result[0]['question_section_name']
    qa_pair = '问题：' + eval_result[0]['question'] + '\n' + '回答：' + eval_result[0]['answer']
    
    prompt = prompt_open_question_summary % (dim, qa_pair)

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]   
    result = call_model(messages)
    response_validity = 1
    if '无效' not in result:
        response_validity = 0
    
    return {'response_validity':response_validity, 'summary': result}


def get_LARS_evidence(req):
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = item['answer']
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    qa_list = """[题目]:请回忆最近一次和同学/朋友发生不愉快的事情，描述一下经过。
[答案]:上次和同学争论某某事情时我有点生气，但后来主动沟通，最后和好了。
[题目]:如果让你描述一下孩子的性格（优点和短板），你会怎样描述？
[答案]:我觉得自己挺开朗的，愿意帮助别人，但有时候太急躁。
[题目]:如果老师（或培训班）布置了一周后到期的作业/项目，孩子通常会怎么安排？
[答案]:尽快开始并按计划完成
[题目]:当孩子在考试、比赛或测评中表现不理想时，通常会怎么做？
[答案]:复盘问题后再开始
[题目]:孩子最喜欢的学科是哪一个？为什么喜欢？有参加过学科竞赛吗？是什么竞赛？有拿到奖项吗？
[答案]:我特别喜欢数学，经常能提前学会新的知识点。
[题目]:孩子最近一次的学习成绩怎么样？（月考/期中/期末）
[答案]:几乎全A（90分以上/满分100）
[题目]:孩子平时会主动预习和复习吗？
[答案]:偶尔会主动
[题目]:孩子在阅读英文材料时，通常能理解到什么程度？
[答案]:能读250–400词文章，查少量生词也能明白大意，并读懂时间表/海报。
[题目]:孩子在日常英文交流中，一般能做到哪种程度？
[答案]:能连贯地描述经历/观点，参与简单辩论，大体听懂常速英语。
[题目]:孩子在英文写作和语法方面，通常能完成到什么水平？
[答案]:写200–250词带论证的短文，基本正确使用从句/被动/让步等结构。
[题目]:孩子有多少个学科补习班？补习的内容是校内相关还是额外拓展？有明显效果吗？/对孩子有帮助吗？
[答案]:我现在上了 2 个补习班，一个是数学，每周两次，主要是复习校内内容；另一个是英语口语，算是额外拓展，我觉得英语课挺有趣的。
[题目]:在没有作业要求时，孩子平时会不会主动去读课外书？通常会选择哪些类型的书？
[答案]:会主动读，但多是自己喜欢的书
[题目]:孩子在写作文或写作任务时，通常会不会注意到词汇表达和细节描写？
[答案]:会注意用一些新词，写一些细节
[题目]:孩子在玩推理游戏或遇到复杂问题时，会不会主动一步步分析并寻找解决办法？
[答案]:偶尔会尝试，但多半依赖别人
[题目]:在课堂或和别人交流时，孩子会不会主动表达自己的看法？别人能不能听懂？
[答案]:比较害羞，说得不清楚
[题目]:当遇到不懂的问题时，孩子会怎么找答案？找到后会不会整理学习资料？
[答案]:会用网络或 AI 工具查找，并简单整理
[题目]:孩子在学习新知识后，通常能记住多久？记得牢不牢？
[答案]:记住一部分，但容易忘
[题目]:孩子在做数学题时，计算是否准确？学过的知识是否能灵活应用到生活里？
[答案]:基本不出错，还能用到生活中的问题
[题目]:孩子在每天学习和专注方面情况如何？时间管理和专注力表现怎样？会有厌学和沉迷游戏/短视频的情况吗？
[答案]:有计划，专注稳定，不受干扰
[题目]:孩子平时最喜欢的活动或学科是什么？为什么喜欢？
[答案]:我最喜欢画画，因为能表达自己的想法。
[题目]:如果有一个机会，可以让孩子带领同学完成一件事，孩子会选择什么？会怎么做？
[答案]:我会选择带领大家做班级布置，我会先分工，然后自己带头完成。
[题目]:平时更愿意花时间在：
[答案]:不太清楚（0）
[题目]:在班级里，孩子更像：
[答案]:跟随别人完成任务（中性 +1）
[题目]:如果有一场比赛，孩子更想：
[答案]:不参加（0）
[题目]:孩子遇到问题时，更常见的做法是：
[答案]:找人商量，带大家一起解决（公众影响型 +3）
[题目]:孩子对哪类内容更感兴趣？
[答案]:没特别兴趣（0）
[题目]:假如让孩子当“小老师”，最想讲的内容是：
[答案]:讲故事、组织同学做活动（公众影响型 +3）
[题目]:请描述一下孩子自己最近一次在体育或艺术方面坚持练习或创作的经历？是什么让你坚持下去的？
[答案]:我每天都练习钢琴，准备比赛时虽然累，但觉得有收获。
[题目]:孩子在空闲时间最喜欢的体育运动或艺术活动是什么？为什么？
[答案]:我喜欢画漫画，因为能讲故事。
[题目]:孩子是否长期坚持某项体育运动，并有专业教练指导？
[答案]:偶尔
[题目]:孩子是否经常参加体育比赛或训练营？
[答案]:经常
[题目]:孩子是否在艺术创作（绘画/音乐/写作等）中有长期投入？
[答案]:经常
[题目]:孩子是否经常参加艺术类展示或比赛？
[答案]:经常
[题目]:孩子是否更喜欢体育竞技的挑战感，而不是安静的艺术创作？
[答案]:非常喜欢体育
[题目]:孩子是否喜欢通过文学/艺术/表演等方式表达思想或情感？
[答案]:不喜欢"""

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_lars % qa_list},
    ]
    result = call_model(messages)
    
    return result

def get_subject_interest(req):
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = item['answer']
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    qa_list = """[题目]:请回忆最近一次和同学/朋友发生不愉快的事情，描述一下经过。
[答案]:上次和同学争论某某事情时我有点生气，但后来主动沟通，最后和好了。
[题目]:如果让你描述一下孩子的性格（优点和短板），你会怎样描述？
[答案]:我觉得自己挺开朗的，愿意帮助别人，但有时候太急躁。
[题目]:如果老师（或培训班）布置了一周后到期的作业/项目，孩子通常会怎么安排？
[答案]:尽快开始并按计划完成
[题目]:当孩子在考试、比赛或测评中表现不理想时，通常会怎么做？
[答案]:复盘问题后再开始
[题目]:孩子最喜欢的学科是哪一个？为什么喜欢？有参加过学科竞赛吗？是什么竞赛？有拿到奖项吗？
[答案]:我特别喜欢数学，经常能提前学会新的知识点。
[题目]:孩子最近一次的学习成绩怎么样？（月考/期中/期末）
[答案]:几乎全A（90分以上/满分100）
[题目]:孩子平时会主动预习和复习吗？
[答案]:偶尔会主动
[题目]:孩子在阅读英文材料时，通常能理解到什么程度？
[答案]:能读250–400词文章，查少量生词也能明白大意，并读懂时间表/海报。
[题目]:孩子在日常英文交流中，一般能做到哪种程度？
[答案]:能连贯地描述经历/观点，参与简单辩论，大体听懂常速英语。
[题目]:孩子在英文写作和语法方面，通常能完成到什么水平？
[答案]:写200–250词带论证的短文，基本正确使用从句/被动/让步等结构。
[题目]:孩子有多少个学科补习班？补习的内容是校内相关还是额外拓展？有明显效果吗？/对孩子有帮助吗？
[答案]:我现在上了 2 个补习班，一个是数学，每周两次，主要是复习校内内容；另一个是英语口语，算是额外拓展，我觉得英语课挺有趣的。
[题目]:在没有作业要求时，孩子平时会不会主动去读课外书？通常会选择哪些类型的书？
[答案]:会主动读，但多是自己喜欢的书
[题目]:孩子在写作文或写作任务时，通常会不会注意到词汇表达和细节描写？
[答案]:会注意用一些新词，写一些细节
[题目]:孩子在玩推理游戏或遇到复杂问题时，会不会主动一步步分析并寻找解决办法？
[答案]:偶尔会尝试，但多半依赖别人
[题目]:在课堂或和别人交流时，孩子会不会主动表达自己的看法？别人能不能听懂？
[答案]:比较害羞，说得不清楚
[题目]:当遇到不懂的问题时，孩子会怎么找答案？找到后会不会整理学习资料？
[答案]:会用网络或 AI 工具查找，并简单整理
[题目]:孩子在学习新知识后，通常能记住多久？记得牢不牢？
[答案]:记住一部分，但容易忘
[题目]:孩子在做数学题时，计算是否准确？学过的知识是否能灵活应用到生活里？
[答案]:基本不出错，还能用到生活中的问题
[题目]:孩子在每天学习和专注方面情况如何？时间管理和专注力表现怎样？会有厌学和沉迷游戏/短视频的情况吗？
[答案]:有计划，专注稳定，不受干扰
[题目]:孩子平时最喜欢的活动或学科是什么？为什么喜欢？
[答案]:我最喜欢画画，因为能表达自己的想法。
[题目]:如果有一个机会，可以让孩子带领同学完成一件事，孩子会选择什么？会怎么做？
[答案]:我会选择带领大家做班级布置，我会先分工，然后自己带头完成。
[题目]:平时更愿意花时间在：
[答案]:不太清楚（0）
[题目]:在班级里，孩子更像：
[答案]:跟随别人完成任务（中性 +1）
[题目]:如果有一场比赛，孩子更想：
[答案]:不参加（0）
[题目]:孩子遇到问题时，更常见的做法是：
[答案]:找人商量，带大家一起解决（公众影响型 +3）
[题目]:孩子对哪类内容更感兴趣？
[答案]:没特别兴趣（0）
[题目]:假如让孩子当“小老师”，最想讲的内容是：
[答案]:讲故事、组织同学做活动（公众影响型 +3）
[题目]:请描述一下孩子自己最近一次在体育或艺术方面坚持练习或创作的经历？是什么让你坚持下去的？
[答案]:我每天都练习钢琴，准备比赛时虽然累，但觉得有收获。
[题目]:孩子在空闲时间最喜欢的体育运动或艺术活动是什么？为什么？
[答案]:我喜欢画漫画，因为能讲故事。
[题目]:孩子是否长期坚持某项体育运动，并有专业教练指导？
[答案]:偶尔
[题目]:孩子是否经常参加体育比赛或训练营？
[答案]:经常
[题目]:孩子是否在艺术创作（绘画/音乐/写作等）中有长期投入？
[答案]:经常
[题目]:孩子是否经常参加艺术类展示或比赛？
[答案]:经常
[题目]:孩子是否更喜欢体育竞技的挑战感，而不是安静的艺术创作？
[答案]:非常喜欢体育
[题目]:孩子是否喜欢通过文学/艺术/表演等方式表达思想或情感？
[答案]:不喜欢"""

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_subject_interest % qa_list},
    ]
    result = call_model(messages)
    
    return result

def get_profile(req, eng_level, rate):
    # 初始化
    enrollment = {
        "L": 0,
        "S": 0,
        "A": 0,
        "R": 0,
        "D": 0,
        "G": 0,
        "E": 0,
        "B": 0,
        "explanation": ""
    }
    
    # LARS评价抽取证据
    lars_evidence = get_LARS_evidence(req)
    lars_evidence = json.loads(lars_evidence.replace("```json",'').replace("```",'').strip())
    lars_score = {}
    for key in lars_evidence:
        tmp_score = sum(v for k,v in lars_evidence[key].items())
        lars_score[key] = tmp_score
    
    # 计算LARS得分
    cal_lars_score(lars_score, enrollment)

    # 计算DG得分
    college_goal_path = req.get('college_goal_path', [])
    cal_dg_score(college_goal_path, enrollment)

    # 得到每个画像的一句话描述
    explain_LS, explain_AR, explain_DG, explain_EB, lars_tag = get_profile_desc(enrollment)
    enrollment['explanation'] = '孩子' + explain_LS + '，同时' + explain_AR + '；' + explain_DG + '，倾向' + explain_EB 
    
    # 学生感兴趣学科
    subject_interest = get_subject_interest(req)

    # 学生英语水平及分档
    eng_level, rate = rate_classify(req)

    # 获取人才画像所有属性信息
    profile_def = get_profile_def(lars_tag)

    # 拼接输出结果
    profile = {
        "profile": profile_def,
        "enrollment": enrollment,
        "english_level": eng_level,
        "rate": rate,
		"subject_interest": subject_interest
    }

    return profile


def get_swot(req):
    # 生成学生背景信息
    basic_info = '\n'.join(
        [
            '性别:' + req.get('gender',''),
            '学校类型:' + req.get('school_type',''),
            '当前年级:' + req.get('current_grade',''),
            '所在城市:' + req.get('city_location',''),
            '目标升学路径:' + ','.join(req.get('college_goal_path',[])),
            '兴趣学科:' + req.get('subject_interest',''),
            '人才画像:' + req.get('profile_type',''),
            '画像描述:' + get_profile_def(req.get('profile_type','')),
            '英语水平:' + req.get('english_level','')
        ]
    )

    # 构造评测结果
    eval_result = req.get('eval_result', [])
    qa_list = []
    for item in eval_result:
        q = item['question']
        ans = item['answer']
        qa_list.extend(['[题目]:'+q+'\n[答案]:'+ans])
    qa_list = '\n'.join(qa_list)

    qa_list = """[题目]:请回忆最近一次和同学/朋友发生不愉快的事情，描述一下经过。
[答案]:上次和同学争论某某事情时我有点生气，但后来主动沟通，最后和好了。
[题目]:如果让你描述一下孩子的性格（优点和短板），你会怎样描述？
[答案]:我觉得自己挺开朗的，愿意帮助别人，但有时候太急躁。
[题目]:如果老师（或培训班）布置了一周后到期的作业/项目，孩子通常会怎么安排？
[答案]:尽快开始并按计划完成
[题目]:当孩子在考试、比赛或测评中表现不理想时，通常会怎么做？
[答案]:复盘问题后再开始
[题目]:孩子最喜欢的学科是哪一个？为什么喜欢？有参加过学科竞赛吗？是什么竞赛？有拿到奖项吗？
[答案]:我特别喜欢数学，经常能提前学会新的知识点。
[题目]:孩子最近一次的学习成绩怎么样？（月考/期中/期末）
[答案]:几乎全A（90分以上/满分100）
[题目]:孩子平时会主动预习和复习吗？
[答案]:偶尔会主动
[题目]:孩子在阅读英文材料时，通常能理解到什么程度？
[答案]:能读250–400词文章，查少量生词也能明白大意，并读懂时间表/海报。
[题目]:孩子在日常英文交流中，一般能做到哪种程度？
[答案]:能连贯地描述经历/观点，参与简单辩论，大体听懂常速英语。
[题目]:孩子在英文写作和语法方面，通常能完成到什么水平？
[答案]:写200–250词带论证的短文，基本正确使用从句/被动/让步等结构。
[题目]:孩子有多少个学科补习班？补习的内容是校内相关还是额外拓展？有明显效果吗？/对孩子有帮助吗？
[答案]:我现在上了 2 个补习班，一个是数学，每周两次，主要是复习校内内容；另一个是英语口语，算是额外拓展，我觉得英语课挺有趣的。
[题目]:在没有作业要求时，孩子平时会不会主动去读课外书？通常会选择哪些类型的书？
[答案]:会主动读，但多是自己喜欢的书
[题目]:孩子在写作文或写作任务时，通常会不会注意到词汇表达和细节描写？
[答案]:会注意用一些新词，写一些细节
[题目]:孩子在玩推理游戏或遇到复杂问题时，会不会主动一步步分析并寻找解决办法？
[答案]:偶尔会尝试，但多半依赖别人
[题目]:在课堂或和别人交流时，孩子会不会主动表达自己的看法？别人能不能听懂？
[答案]:比较害羞，说得不清楚
[题目]:当遇到不懂的问题时，孩子会怎么找答案？找到后会不会整理学习资料？
[答案]:会用网络或 AI 工具查找，并简单整理
[题目]:孩子在学习新知识后，通常能记住多久？记得牢不牢？
[答案]:记住一部分，但容易忘
[题目]:孩子在做数学题时，计算是否准确？学过的知识是否能灵活应用到生活里？
[答案]:基本不出错，还能用到生活中的问题
[题目]:孩子在每天学习和专注方面情况如何？时间管理和专注力表现怎样？会有厌学和沉迷游戏/短视频的情况吗？
[答案]:有计划，专注稳定，不受干扰
[题目]:孩子平时最喜欢的活动或学科是什么？为什么喜欢？
[答案]:我最喜欢画画，因为能表达自己的想法。
[题目]:如果有一个机会，可以让孩子带领同学完成一件事，孩子会选择什么？会怎么做？
[答案]:我会选择带领大家做班级布置，我会先分工，然后自己带头完成。
[题目]:平时更愿意花时间在：
[答案]:不太清楚（0）
[题目]:在班级里，孩子更像：
[答案]:跟随别人完成任务（中性 +1）
[题目]:如果有一场比赛，孩子更想：
[答案]:不参加（0）
[题目]:孩子遇到问题时，更常见的做法是：
[答案]:找人商量，带大家一起解决（公众影响型 +3）
[题目]:孩子对哪类内容更感兴趣？
[答案]:没特别兴趣（0）
[题目]:假如让孩子当“小老师”，最想讲的内容是：
[答案]:讲故事、组织同学做活动（公众影响型 +3）
[题目]:请描述一下孩子自己最近一次在体育或艺术方面坚持练习或创作的经历？是什么让你坚持下去的？
[答案]:我每天都练习钢琴，准备比赛时虽然累，但觉得有收获。
[题目]:孩子在空闲时间最喜欢的体育运动或艺术活动是什么？为什么？
[答案]:我喜欢画漫画，因为能讲故事。
[题目]:孩子是否长期坚持某项体育运动，并有专业教练指导？
[答案]:偶尔
[题目]:孩子是否经常参加体育比赛或训练营？
[答案]:经常
[题目]:孩子是否在艺术创作（绘画/音乐/写作等）中有长期投入？
[答案]:经常
[题目]:孩子是否经常参加艺术类展示或比赛？
[答案]:经常
[题目]:孩子是否更喜欢体育竞技的挑战感，而不是安静的艺术创作？
[答案]:非常喜欢体育
[题目]:孩子是否喜欢通过文学/艺术/表演等方式表达思想或情感？
[答案]:不喜欢"""

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt_swot % (basic_info, qa_list)},
    ]
    result = call_model(messages)
    
    return result


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
    # req = {}
    # req['name'] = '李同学'
    # req['school_type'] = '公立'
    # req['current_grade'] = 'G3'
    # req['profile_type'] = '顶级竞赛科研型'
    # req['rate'] = 'A档'
    # req['college_goal_path'] = '美国本科'
    # req['subject_interest'] = '数学'
    # 
    # res = get_growth_advice_rules(req)
    # print(json.dumps(res,indent=4,ensure_ascii=False))

    req = {}
    pred_data = {}
    pred_data['name'] = '李同学'
    pred_data['gender'] = '男'
    pred_data['city_location'] = 'SH'
    pred_data['school_type'] = '公立'
    pred_data['current_grade'] = 'G3'
    pred_data['profile_type'] = '顶级竞赛科研型'
    pred_data['english_level'] = 'A2'
    pred_data['rate'] = 'A档'
    pred_data['college_goal_path'] = ['美国本科']
    pred_data['subject_interest'] = '数学'
    pred_data['id'] = '12345'
    req['student_info'] = pred_data
    req['eval_result'] = [ 
        {   
            "question_section_name":"性格特征",
            "question_type":2,
            "question":"如果让你描述一下孩子的性格（优点和短板），你会怎样描述？",
            "answer":"我觉得自己挺开朗的，愿意帮助别人，但有时候太急躁。"
        }   
    ]
    
    # res = get_open_question_summary(req.json)
    # print(res)
    import json
    with open('./resource/LARS_definition.json', 'r') as f:
        data = json.load(f)
    print(len(data))
