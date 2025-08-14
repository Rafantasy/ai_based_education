import json
import copy
from call_llm_model import call_model
from prompt_template import (
    prompt_strength,
    prompt_weakness,
    prompt_opptunity,
    prompt_threat,
    prompt_edu_proposal
)

PROFILE_DEFINITION = {
    "顶级竞赛科研型人才": {
        "定义": "具有卓越的逻辑推理能力、数据处理能力与系统性思维，乐于深入研究并持续探索复杂问题，适合在数理、编程、工程、科研等领域深耕。该类学生具备扎实的学科基础、强烈的问题意识和自驱的探索欲，常在数理竞赛、科研项目、奥赛体系中脱颖而出。",
        "代表发展方向": "STEM（科学、技术、工程、数学）专业、数理竞赛（如AMC、IMO、IOI）、科研计划（如ISEF、英才计划）、顶尖大学工程/计算机/自然科学专业。"
    },
    "社会公众影响型人才": {
        "定义": "具备敏锐的社会观察力与优秀的沟通表达能力，能够整合资源、影响他人并组织群体协作。此类学生逻辑清晰，情境判断力强，善于演讲、辩论、策划与公共表达，富有责任意识和公众精神，具备未来领导潜质。",
        "代表发展方向": "经济、政治、社会学、商科、传媒等学科方向；参加模联、辩论、演讲、公益/社会创新项目；可发展为未来的企业家、政策制定者、公众影响者等。"
    },
    "人文艺术型人才": {
        "定义": "在文学、艺术、哲学、语言等方面展现出敏感性与表达力，拥有良好的审美能力与创作欲望，适合在文字、表演、设计、艺术创作等领域深入发展。此类学生感知细腻、富有想象力，常在写作、绘画、音乐、戏剧等方面持续投入。",
        "代表发展方向": "艺术类专业（美术、音乐、戏剧、电影）、文史哲相关学科、创意写作、设计类课程，适合参加艺术赛事、作品集提升、参加艺术高中或国际艺术升学路径。"
    },
    "体育竞技型人才": {
        "定义": "身体素质突出、训练投入度高，拥有明确的体育项目方向与竞技精神，具备长期坚持、抗压与突破自我的意志品质。此类学生常在专业教练指导下进行系统训练，在赛事中取得成绩，并有意向通过体育特长路径升学。",
        "代表发展方向": "田径、球类、武术、游泳等专项训练路径，国内体育特长生升学通道，或以体育为优势路径申请国际高中、NCAA大学体育奖学金。"
    }
}

def tag_selection(sub_dim_tag, condition):
    ### 筛选所有维度下符合条件的tag，比如：积极 | 消极
    sub_dim_tag_cp = copy.deepcopy(sub_dim_tag)
    for p_key in sub_dim_tag_cp:
        for s_key in sub_dim_tag_cp[p_key]:
            if '英语能力' == s_key:
                continue
            assert isinstance(sub_dim_tag_cp[p_key][s_key],list)
            s_items = []
            for item in sub_dim_tag_cp[p_key][s_key]:
                if condition in item:
                    s_items.extend([item.split('-')[0]])
            sub_dim_tag_cp[p_key][s_key] = s_items
    
    return sub_dim_tag_cp 

def gen_s(student_info, sub_dim_tag):
    sub_dim_tag_cp = tag_selection(sub_dim_tag, '积极') 
    prompt = prompt_strength % (student_info, json.dumps(sub_dim_tag_cp,indent=4,ensure_ascii=False))

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    result = call_model(messages)
    
    return result

def gen_w(student_info, sub_dim_tag):
    sub_dim_tag_cp = tag_selection(sub_dim_tag, '消极') 
    prompt = prompt_weakness % (student_info, json.dumps(sub_dim_tag_cp,indent=4,ensure_ascii=False))

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    result = call_model(messages)
    
    return result

def gen_o(student_info, sub_dim_tag, profile):
    prompt = prompt_opptunity % (
        student_info, 
        json.dumps(sub_dim_tag,indent=4,ensure_ascii=False),
        json.dumps(PROFILE_DEFINITION[profile],indent=4,ensure_ascii=False)
    )

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    
    result = call_model(messages)
    
    return result

def gen_t(student_info, sub_dim_tag, profile):
    prompt = prompt_threat % (
        student_info, 
        json.dumps(sub_dim_tag,indent=4,ensure_ascii=False),
        json.dumps(PROFILE_DEFINITION[profile],indent=4,ensure_ascii=False)
    )

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]

    result = call_model(messages)
    
    return result

def gen_swot(student_info, sub_dim_tag, profile):
    res_s = gen_s(student_info,sub_dim_tag)
    print('\n**************Strength*******************')
    print(res_s)

    res_w = gen_w(student_info,sub_dim_tag)
    print('\n**************Weakness*******************')
    print(res_w)

    res_o = gen_o(student_info,sub_dim_tag,profile)
    print('\n**************Opportunity*******************')
    print(res_o)

    res_t = gen_t(student_info,sub_dim_tag,profile)
    print('\n**************Threats*******************')
    print(res_t)


def gen_proposal(student_info, sub_dim_tag, profile):
    prompt = prompt_edu_proposal % (
        student_info, 
        json.dumps(sub_dim_tag,indent=4,ensure_ascii=False),
        json.dumps(PROFILE_DEFINITION[profile],indent=4,ensure_ascii=False)
    )

    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]

    result = call_model(messages)
    
    return result