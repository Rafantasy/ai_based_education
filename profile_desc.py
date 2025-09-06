import json

# 加载LARS人才画像定义
with open('./resource/LARS_definition.json', 'r') as f:
    LARS_DEF_DATA = json.load(f)

class ProfileDesc:
    # L vs S
    desc_L = "善于组织与表达"
    desc_S = "擅长运动竞技"
    desc_LS = "在领导力与体育上均衡发展"

    # A vs R
    desc_A = "在艺术创作上表现突出"
    desc_R = "对科研探索充满热情"
    desc_AR = "在艺术创作与科研理性上也展现出均衡的天赋"

def get_profile_desc(enrollment):
    lars_tag = ''

    explain_LS = ''
    explain_AR = ''
    if enrollment['L'] > enrollment['S']:
        explain_LS = f"{ProfileDesc.desc_L}（L {enrollment['L']}）"
        lars_tag += 'L'
    elif enrollment['L'] < enrollment['S']:
        explain_LS = f"{ProfileDesc.desc_S}（S {enrollment['S']}）"
        lars_tag += 'S'
    else:
        explain_LS = ProfileDesc.desc_LS
        # TODO: 更新L=S时的取值逻辑
        lars_tag += 'L'

    if enrollment['A'] > enrollment['R']:
        explain_AR = f"{ProfileDesc.desc_A}（A {enrollment['A']}）"
        lars_tag += 'A'
    elif enrollment['A'] < enrollment['R']:
        explain_AR = f"{ProfileDesc.desc_R}（R {enrollment['R']}）"
        lars_tag += 'R'
    else:
        explain_AR = ProfileDesc.desc_AR
        # TODO: 更新A=R时的取值逻辑
        lars_tag += 'R'
    
    explain_DG = ''
    if enrollment['D'] == 100:
        explain_DG = '路径选择为国内'
        lars_tag += 'D'
    elif enrollment['G'] == 100:
        explain_DG = '路径选择为国际'
        lars_tag += 'G'
    else:
        explain_DG = '路径选择为国内国际双规'
        lars_tag += 'G'
    explain_EB = '冲顶型' if enrollment['E'] > enrollment['B'] else '稳进型'

    return explain_LS, explain_AR, explain_DG, explain_EB, lars_tag

def get_profile_def(lars_tag):
    for item in LARS_DEF_DATA:
        if lars_tag in item['name']:
            return item
    
    return {}
