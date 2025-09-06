from call_llm_model import call_model
from main import get_growth_advice_rules

import pandas as pd
import json

get_target_university_recommendation_prompt = '''
请结合以下学生信息和相关信息，生成一份目标大学的推荐列表，最多不超过5所：
### 要求如下
- 只给出学校的列表即可

### 学生信息
{background}

### 相关信息
{related_info}
'''

get_current_grade_plan_prompt = '''
请结合以下学生信息和相关信息，生成一份符合当前年级的规划json：
### 要求如下
- 一定要选取仅符合「当前规划年级」的活动来给出建议
- 最终建议的结构应包含以下各项，每项一段话，不能给出列表
如：
```json{{
  "学年目标": "本学年目标是帮助学生在科学素养方面打下更扎实基础，初步建立生物学方向的学科兴趣，同时提升科研意识与问题思维能力。",
  "推荐资源": "推荐学生使用《DK自然科学图解百科》(青少年生物探秘课程)，并参与MOOC平台上的生物启蒙课程；使用“科学探究小实验”工具箱进行家庭实验项目。",
  "应完成的项目": "鼓励学生参加“全国青少年科技创新大赛(初阶)”或“生物小课题研究营”，开展一个小型植物观察记录项目，初步训练数据记录与假设思维，贴合未来STEM方向申请逻辑。",
  "升学节点提示": "本阶段建议家长与学生共同了解国际课程体系(如IB/AP/A-Level)，并考虑在7年级起申请过渡至国际课程体系的初中项目；同时开始规划初中阶段竞赛路径。",
  "延续性建议": "上一学年的英文绘本阅读和自然拼读基础可在本年延伸为自然科学类分级读物阅读；建议记录本年完成的生物观察项目成果，为G7阶段科研项目打基础。",
  "英语进阶目标": "在英语方面，建议词汇量达到2500，语言能力提升至CEFR B1，为未来的TOEFL考试打好语言基础。",
  "特别提醒": "若该升学路径存在时间关键点(如国际体系转换节点、课程体系切换、标化考试规划时间等)，请列出提醒事项；可适配家长建议，强调系统性准备。"
}}```
- 在当前{current_grade0}年级的规划中，不要出现其他年级的规划内容

### 学生信息
{background}

### 目标学校
{target_universsity}

### 之前的规划
{former_plan}

### 参考知识库
{reference_data}

### 建议规划内容
{reference_plan}

### 当前规划年级
{current_grade}
'''


class RagDatabase():
    def __init__(self):
        self.university_recommendation = pd.read_json('/root/data/新版知识库&规则库/db_all_v0/db_【画像知识库】.json')

        self.summer_school = pd.read_json('/root/data/新版知识库&规则库/db_all_v0/db_【美国大学夏校知识库】.json')
        self.research_activity = pd.read_json('/root/data/新版知识库&规则库/db_all_v0/db_科研知识库.json')
        self.english_ability = json.load(open('/root/data/新版知识库&规则库/db_all_v0/db_英语能力知识库.json', 'r'))
        self.competition_activity = pd.read_json('/root/data/新版知识库&规则库/db_all_v0/db_竞赛_活动知识库.json')
        self.requirement_base = pd.read_json('/root/data/新版知识库&规则库/db_all_v0/db_A档&B档升学路径对标本科要求知识库.json')


    def get_university_recommendation(self, profile_type):
        for key in self.university_recommendation.keys():
            if profile_type in key:
                return self.university_recommendation[key]
        return self.university_recommendation['顶级竞赛科研型（STEM方向）']
    
    def get_current_databse(self, db_name_list):
        db_map = {
            'db_【画像知识库】':self.university_recommendation,
            'db_【美国大学夏校知识库】':self.summer_school,
            'db_科研知识库':self.research_activity,
            'db_英语能力知识库':self.english_ability,
            'db_竞赛_活动知识库':self.competition_activity,
            'db_A档&B档升学路径对标本科要求知识库':self.requirement_base
        }
        parts = []
        for name in db_name_list:
            value = db_map.get(name)
            if value is None:
                # Skip unknown database names to avoid KeyError
                continue
            if isinstance(value, pd.DataFrame):
                try:
                    value_str = value.to_json(orient='records', force_ascii=False)
                except Exception:
                    value_str = value.to_string()
            else:
                try:
                    value_str = json.dumps(value, ensure_ascii=False)
                except Exception:
                    value_str = str(value)
            parts.append(f"{name}\n{value_str}")
        return "\n".join(parts)

    
    # def get_

def get_background(res):
    background = {
        "name": res['name'],
        "school_type": res['school_type'],
        "current_grade": res['current_grade'],
        "profile_type": res['profile_type'],
        "rate": res['rate'],
        "college_goal_path": res['college_goal_path'],
        "subject_interest": res['subject_interest'],
    }
    return background

def request_model(prompt_input):
    messages = [
        {
            "role": "user",
            "content": f"{prompt_input}"
        }
    ]
    response = call_model(messages)
    return response
import re
import json

def format_flag(text):
    try:
        pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            # final_res = json.loads(matches[0])
            final_res = matches[0]
            return False  # Valid JSON found
        else:
            return True   # No JSON found
    except (json.JSONDecodeError, IndexError):
        return True       # Invalid JSON or no matches

def get_final_res(get_plan_prompt):
    res = ''
    while format_flag(res):
        res = request_model(get_plan_prompt)
        # print(res)
    
    # Process the valid response
    pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(pattern, res, re.DOTALL)  # Use 'res' instead of 'text'
    # final_res = json.loads(matches[0])
    final_res = matches[0]
    return final_res

def get_report(res):
    background = get_background(res)
    db = RagDatabase()
    related_info = db.get_university_recommendation(res['profile_type'])
    university_recommend = request_model(get_target_university_recommendation_prompt.format(background=background, related_info=related_info))

    grade_list = res['recall_rules']['grade_list'].keys()

    db_name_full_list = [
        'db_【画像知识库】',
        'db_【美国大学夏校知识库】',
        'db_科研知识库',
        'db_英语能力知识库',
        'db_竞赛_活动知识库',
        'db_A档&B档升学路径对标本科要求知识库'
    ]

    former_plan = {"本科推荐院校":university_recommend}

    for current_grade in grade_list:
        reference_plan = res['recall_rules']['grade_list'][current_grade]
        db_name_list = ','.join([x['db_name'] for x in reference_plan])
        current_db_list = []
        for item in db_name_full_list:
            if item in db_name_list:
                current_db_list.append(item)

        reference_data = db.get_current_databse(current_db_list)

        get_plan_prompt = get_current_grade_plan_prompt.format(current_grade0=current_grade, background=background, target_universsity=university_recommend, former_plan=former_plan, reference_data=reference_data, reference_plan=reference_plan, current_grade=current_grade)
        current_plan = get_final_res(get_plan_prompt)
        former_plan[current_grade] = current_plan
        # print(f"{current_grade} plan is {json.dumps(former_plan,indent=4,ensure_ascii=False)}")
        print(f"{current_grade} plan is {current_plan}")
    
    return former_plan


if __name__ == '__main__':
    req = {}
    req['name'] = '李同学'
    req['school_type'] = '公立'
    req['current_grade'] = 'G3'
    req['profile_type'] = '顶级竞赛科研型'
    req['rate'] = 'A档'
    req['college_goal_path'] = '美国本科'
    req['subject_interest'] = '数学'
    
    res = get_growth_advice_rules(req)

    get_report(res)

