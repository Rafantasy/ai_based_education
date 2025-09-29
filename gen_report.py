from call_llm_model import call_model
from main import get_growth_advice_rules

import pandas as pd
import json

import logging
logger = logging.getLogger("service_log")

import time

get_target_university_recommendation_prompt = '''
请结合以下学生信息和相关信息，生成一份目标大学的推荐列表，最多不超过5所：
### 要求如下
- 【目标院校】：依据升学目标与学生画像推荐5所目标高校，A档或B档建议区别展示
- 给出目标院校列表，A档或B档建议区别展示

### 学生信息
{background}

### 相关信息
{related_info}
'''

get_current_grade_plan_prompt = '''你现在是一名资深的低龄升学规划专家，熟悉全球本科升学路径（中国大陆本科、港澳台本科、美本、英联邦本科、双轨）和低龄教育规律。你的任务是为家长提供一份“可以直接施工”的规划方案。

⚠️ 输出必须像顾问和家长沟通，有温度、有逻辑、能执行。禁止复述抽象逻辑，禁止空泛表达（如“你可以了解 IB/AL/AP”），必须根据学生情况和升学路径选择直接给出明确的择校体系推荐（如“建议选择 IB 国际学校”），并说明理由和行动路径。

【输入来源】
- 学生信息
- 目标学校
- 之前的规划
- 下一年参考知识库
- 建议规划内容

请严格遵循以下输出要求：

1. **角色定位**
- 以“专家顾问”的身份直接对家长说话，语气专业、有温度、可执行。
- 避免使用过多专业术语或AI/模型逻辑解释。

2. **规划逻辑**
- 以终为始：从孩子未来本科目标倒推，结合当前年级/年龄特性分解路径。
- 从兴趣起点（一本书、一个社团、一次尝试）逐步延展到夏校、竞赛、科研、实习。
- 最终形成孩子的独特 **signature**（影响力、利他性、个人故事）。

3. 执行逻辑
- 必须按照既定的“升学路径规则库”自动推导 → 输出明确的择校体系选择（如 IB / A-Level / AP / 公立重点高中），并说明理由。
- 成长建议必须结合 SWOT 分析：  
   - **优势**：写出如何放大  
   - **劣势**：写出如何补强  
   - **机会**：写出如何利用  
   - **威胁**：必须转化为 1–2 条具体应对方法（如“心理韧性低 → 情绪日记法 + 体育释放活动”）  
   ⚠️ 禁止只写“心理需要调试”。
4. 所有考试/竞赛/夏校/科研推荐必须包含：  
   - 年级适合度  
   - 最低目标 vs 理想目标  
   - 达成路径（如“每周 2 次训练 → 校级选拔 → 区级/国家级”）
5. 升学与择校建议必须包含时间节点提示（如秋季看校、寒假夏校、G11 文书准备等）。
6. 输出内容必须符合孩子的年级和年龄特性，确保落地可执行。

--------------------------------------------------
【表达风格】
- 专业 × 通俗 × 有温度。
- 建议要像顾问跟家长说话，而不是写学术报告。
- 每条建议要有画面感和执行感，让家长看完能立刻行动。

--------------------------------------------------
【输出目标】
为家长提供一份 **结构清晰、路径明确、结合孩子个性化特征、落地可行、「当前规划年级」可执行的升学与成长路径指南**。
--------------------------------------------------
【输出格式】
必须包含以下各个部分，”每项一段话，不能给出列表“，输出json格式，如：
```json{{
  "学年目标": "本学年目标是帮助学生在科学素养方面打下更扎实基础……",
  "推荐资源": "推荐学生使用《DK自然科学图解百科》……",
  "应完成的项目": "鼓励学生参加“全国青少年科技创新大赛(初阶)”或“生物小课题研究营”，……",
  "升学节点提示": "本阶段建议家长与学生共同了解国际课程体系(如IB/AP/A-Level)，……",
  "延续性建议": "上一学年的英文绘本阅读和自然拼读基础可在本年延伸为自然科学类分级读物阅……",
  "英语进阶目标": "在英语方面，建议词汇量达到2500，语言能力提升……",
  "特别提醒": "若该升学路径存在时间关键……"
}}```


请记住：你的目标是帮助家长获得一份 **结构清晰、落地可行、「当前规划年级」可执行的升学与成长路径指南**，而不是写抽象的规划逻辑。

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
{current_grade}'''

# get_current_grade_plan_prompt = '''
# 请结合以下学生信息和相关信息，生成一份符合当前年级的规划json：
# ### 要求如下
# - 一定要选取仅符合「当前规划年级」的活动来给出建议,「只针对当前：{current_grade0}年级」，结合学生信息和目标院校给出**接下来一年**的学年规划。
# - 最终建议的结构应包含以下各项，每项一段话，不能给出列表
# 如：
# ```json{{
#   "学年目标": "本学年目标是帮助学生在科学素养方面打下更扎实基础，初步建立生物学方向的学科兴趣，同时提升科研意识与问题思维能力。",
#   "推荐资源": "推荐学生使用《DK自然科学图解百科》(青少年生物探秘课程)，并参与MOOC平台上的生物启蒙课程；使用“科学探究小实验”工具箱进行家庭实验项目。",
#   "应完成的项目": "鼓励学生参加“全国青少年科技创新大赛(初阶)”或“生物小课题研究营”，开展一个小型植物观察记录项目，初步训练数据记录与假设思维，贴合未来STEM方向申请逻辑。",
#   "升学节点提示": "本阶段建议家长与学生共同了解国际课程体系(如IB/AP/A-Level)，并考虑在7年级起申请过渡至国际课程体系的初中项目；同时开始规划初中阶段竞赛路径。",
#   "延续性建议": "上一学年的英文绘本阅读和自然拼读基础可在本年延伸为自然科学类分级读物阅读；建议记录本年完成的生物观察项目成果，为G7阶段科研项目打基础。",
#   "英语进阶目标": "在英语方面，建议词汇量达到2500，语言能力提升至CEFR B1，为未来的TOEFL考试打好语言基础。",
#   "特别提醒": "若该升学路径存在时间关键点(如国际体系转换节点、课程体系切换、标化考试规划时间等)，请列出提醒事项；可适配家长建议，强调系统性准备。"
# }}```
# - 和之前年级的规划内容要「具体」、「可执行」、有「延续性」，但是「不要重复」
# - 建议和措施要具体，


# ### 学生信息
# {background}

# ### 目标学校
# {target_universsity}

# ### 之前的规划
# {former_plan}

# ### 参考知识库
# {reference_data}

# ### 建议规划内容
# {reference_plan}

# ### 当前规划年级
# {current_grade}
# '''


class RagDatabase():
    def __init__(self):
        self.university_recommendation = pd.read_json('/root/data/新版知识库&规则库/db_all_v1/db_【画像知识库】.json')
        self.summer_school = pd.read_json('/root/data/新版知识库&规则库/db_all_v1/db_【美国大学夏校知识库】.json')
        self.research_activity = pd.read_json('/root/data/新版知识库&规则库/db_all_v1/db_科研知识库.json')
        self.english_ability = json.load(open('/root/data/新版知识库&规则库/db_all_v1/db_英语能力知识库.json', 'r'))
        self.competition_activity = pd.read_json('/root/data/新版知识库&规则库/db_all_v1/db_竞赛_活动知识库.json')
        self.requirement_base = pd.read_json('/root/data/新版知识库&规则库/db_all_v1/db_A档&B档升学路径对标本科要求知识库.json')


    def get_university_recommendation(self, profile_type):
        for key in self.university_recommendation.keys():
            if profile_type in key:
                return self.university_recommendation[key]
        return self.university_recommendation['顶级竞赛科研型（STEM方向）']
    
    def filter_by_grade(self, english_ability, grade):
        """
        筛选english_ability中包含指定年级的数据
        
        参数:
        english_ability: 英语能力数据，可以是字典或列表
        grade: 年级，如 'G8', 'G9', 'G10' 等
        
        返回:
        筛选后的数据，保持原始数据结构
        """
        if isinstance(english_ability, dict):
            # 如果是字典，筛选包含指定年级的条目
            filtered_entries = {k: v for k, v in english_ability.items() if grade in str(v)}
            return filtered_entries
        elif isinstance(english_ability, list):
            # 如果是列表，筛选包含指定年级的条目
            filtered_entries = [item for item in english_ability if grade in str(item)]
            return filtered_entries
        else:
            print(f"警告: 不支持的数据类型 {type(english_ability)}")
            return None
    
    def get_current_databse(self, db_name_list, current_grade):
        db_map = {
            'db_【画像知识库】':self.university_recommendation,
            'db_【美国大学夏校知识库】':self.summer_school[self.summer_school['eligibility'].astype(str).str.contains(current_grade, na=False)],
            'db_科研知识库':self.research_activity[self.research_activity['科研活动库'].astype(str).str.contains(current_grade, na=False)],
            'db_英语能力知识库':self.filter_by_grade(self.english_ability, current_grade),
            'db_竞赛_活动知识库':self.competition_activity[self.competition_activity['要求年级'].astype(str).str.contains(current_grade, na=False)],
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

def get_prev_plan(former_plan,current_grade,grade_list):
    """获取前一年级的升学规划"""
    prev_plan = {
        "本科推荐院校": former_plan.get("本科推荐院校", '')
    }
    
    cur_idx = grade_list.index(current_grade)
    if cur_idx > 0:
        prev_grade = grade_list[cur_idx-1]
        prev_plan[prev_grade] = former_plan.get(prev_grade, '')
    
    return prev_plan

def get_report(res):
    background = get_background(res)
    db = RagDatabase()
    related_info = db.get_university_recommendation(res['profile_type'])
    university_recommend = request_model(get_target_university_recommendation_prompt.format(background=background, related_info=related_info))

    grade_list = list(res['recall_rules']['grade_list'].keys())
    grade_list.sort(key=lambda x:int(x.split('G')[1]))

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

        reference_data = db.get_current_databse(current_db_list, current_grade)

        # get_plan_prompt = get_current_grade_plan_prompt.format(current_grade0=current_grade, background=background, target_universsity=university_recommend, former_plan=former_plan, reference_data=reference_data, reference_plan=reference_plan, current_grade=current_grade)
    
        # 20250923: former_plan修改为只用前一个年级(by 拉凡)
        start_time = time.time()
        
        prev_plan = get_prev_plan(former_plan,current_grade,grade_list)
        get_plan_prompt = get_current_grade_plan_prompt.format(current_grade0=current_grade, background=background, target_universsity=university_recommend, former_plan=prev_plan, reference_data=reference_data, reference_plan=reference_plan, current_grade=current_grade)
        # logger.info(f"****plan_prompt****\n{get_plan_prompt}")
        current_plan = get_final_res(get_plan_prompt)
        
        # former_plan[current_grade] = current_plan
        former_plan[current_grade] = eval(current_plan)
        
        # print(f"{current_grade} plan is {json.dumps(former_plan,indent=4,ensure_ascii=False)}")
        print(f"{current_grade} plan is {current_plan}")

        gen_time = time.time() - start_time
        logger.info(f"plan generate time:{gen_time}s")
    
    return former_plan


if __name__ == '__main__':
    req = {
        "student_info": {
            "name": "大头儿子",
            "gender": "男",
            "school_type": "国际",
            "current_grade": "G10",
            "city_location": "北屯市",
            "college_goal_path": [
                "中国大陆本科"
            ],
            "id": "141de63a-8f7a-11f0-86aa-0242ac120003"
        },
        "eval_result": [
            {
                "question_section_name": "体育艺术",
                "question_type": 1,
                "question": "如果不好描述，请选择最接近的情况（可多选运动类型 + 坚持程度）：",
                "answer": [
                    "冰雪运动（滑冰、滑雪、冰球等）",
                    "体操与技巧类（体操、啦啦操、杂技类等）"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "孩子在每天学习和专注方面情况如 何？时间管理和专注力表现怎样？会有厌学和沉迷游戏/短视频的情况吗？",
                "answer": [
                    "缺乏计划，常拖延，易分心，游戏和短视频时间每天2小时以上"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "如果要选一项孩子空闲时间最常做的事情，会是？",
                "answer": [
                    "练习艺术（绘画 / 乐器 / 唱歌 / 表演等）"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "如果有一个机会，可以让孩子带领同学完成一件事，孩子最可能选择什么？",
                "answer": [
                    "带大家排练一场节目 / 艺术创作"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "如果要大致概括孩子周末的安排，以下哪几类最符合？（可多选）",
                "answer": [
                    "娱乐休闲（打游戏、刷手机、看电视、逛街等）",
                    "体育运动（游泳、篮球、足球等）"
                ]
            },
            {
                "question_section_name": "综合 素质",
                "question_type": 1,
                "question": "在班级里，孩子更像：",
                "answer": [
                    "喜欢当班干部、组织大家的人"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "如果有一场比赛， 孩子更想：",
                "answer": [
                    "参加演讲/辩论/策划类活动"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "孩子遇到问题时，更常见的做法是：",
                "answer": [
                    "找人商量，带大家一起解决"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "孩子对哪类内容更感兴趣？",
                "answer": [
                    "艺术与人文类（绘画、写作、音乐、表演、文学历史）"
                ]
            },
            {
                "question_section_name": "综合素质",
                "question_type": 1,
                "question": "假如让孩子当“小老师”，最想讲的内容是：",
                "answer": [
                    "讲一段有趣的历史故事或文学片段"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "孩子在做数学题时，计算是否准确？学过的知识是否能灵活应用到生活里？",
                "answer": [
                    "偶尔出错，大部分能应用"
                ]
            },
            {
                "question_section_name": "体育艺术",
                "question_type": 1,
                "question": "如果学校有社团活动，你更愿意参加以下哪些？（最多选3个）",
                "answer": [
                    "文学类（写作、演讲、读书会）",
                    "公益类（志愿服务、环保行动）",
                    "学术类（数学社、英语角、辩论队）"
                ]
            },
            {
                "question_section_name": "体育艺术",
                "question_type": 1,
                "question": "关于孩子的体育爱好情况，以下哪些符合？（可多选）",
                "answer": [
                    "有专业教练阶段性指导（偶尔培训/短期集训）",
                    "参加过区/市级体育比赛"
                ]
            },
            {
                "question_section_name": "体育艺术",
                "question_type": 1,
                "question": "关于孩子的艺术兴趣和坚持情况，以下哪些符合？",
                "answer": [
                    " 有阶段性训练（1–3 年，间断参与）",
                    "完全自学，纯兴趣爱好"
                ]
            },
            {
                "question_section_name": "体育艺术",
                "question_type": 1,
                "question": "孩子是否经常参加艺术类展示或比赛？",
                "answer": [
                    "经常"
                ]
            },
            {
                "question_section_name": "体育艺术",
                "question_type": 1,
                "question": "孩子是否喜欢通过文学/艺术/表演等方式表达思想或情感？",
                "answer": [
                    "偶尔"
                ]
            },
            {
                "question_section_name": "家庭教育",
                "question_type": 1,
                "question": "如果不好完整描述，请勾选最符合期待的方向（可选 2–4 项）",
                "answer": [
                    "培养责任感 / 独立性",
                    "参加竞赛 / 获得奖项"
                ]
            },
            {
                "question_section_name": "家庭教育",
                "question_type": 1,
                "question": "如果不好完整描述，请勾选最符合{SELF} 家庭关系的情况",
                "answer": [
                    "经常聊天/陪伴",
                    "遇事能沟通",
                    "偶尔交流，时间有限"
                ]
            },
            {
                "question_section_name": "家庭教育",
                "question_type": 1,
                "question": "如果可以改变一件事，你更希望改变的是：",
                "answer": [
                    "孩子的兴趣与坚持（能长期坚持一项爱好/特长）"
                ]
            },
            {
                "question_section_name": "家庭教育",
                "question_type": 1,
                "question": "平时是谁主要陪伴孩子和参与孩子教育？",
                "answer": [
                    "父母双 方"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子在日常英文交流中，一般能做到哪种程度？",
                "answer": [
                    "能连贯地描述经历/观点，参与简单辩论，大体听懂常速英语。"
                ]
            },
            {
                "question_section_name": "性格特质",
                "question_type": 2,
                "question": "请回忆孩子最近一次和同学/朋友发生不愉快的事情，描述一下经过。",
                "answer": [
                    "昨天课间，孩子带的漫画书被同学小王借走后，小王不小心撕坏了封面。孩子看到后很生气，直接抢过书指责小王，两人吵了起来，小王也委屈地说不是故意的。最后老师过来调解，小王道歉，孩子也慢慢平复了情绪，答应一起修补书。"
                ]
            },
            {
                "question_section_name": "性格特质",
                "question_type": 1,
                "question": "你觉得这件事让孩子有成就感，主要是因为：",
                "answer": [
                    "得到了老师/家长的认可"
                ]
            },
            {
                "question_section_name": "性格特质",
                "question_type": 1,
                "question": "当孩子在考试、比赛或测评中表现不理想时，通常会怎么做？",
                "answer": [
                    "很难释怀，总担心下次失败"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": " 快速勾选符合孩子校内表现和学习态度的选项（选3–6个）",
                "answer": [
                    "经常举手",
                    "被点才说",
                    "不愿发言",
                    "偶尔举手"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "如果不 好完整描述，请快速勾选符合孩子的情况（学科 + 竞赛 + 奖项）",
                "answer": [
                    "语文",
                    "艺术/音乐",
                    "数学"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子最近一次的学习成绩怎么样？（月考/期中/期末）",
                "answer": [
                    "偶尔会有B或C（80分左右/满分100）"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子平时成绩在班里排名区段",
                "answer": [
                    "中上"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子平时会主动预习和复习吗？",
                "answer": [
                    "偶尔会主动"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子在阅读英文材料时，通常能理解到什么程度？",
                "answer": [
                    "能读100–150词的小短文，抓到事实信息（如时间/地点/人物）。"
                ]
            },
            {
                "question_section_name": "性格特质",
                "question_type": 2,
                "question": "如何描述孩子的性格？（三个优点/三个缺点）",
                "answer": [
                    "优点：共情力强，家人不适会主动照顾，会安慰哭闹的小伙伴；好奇心足，爱观察蚂蚁、问科普问题，还会模仿手工教程尝试 ；有责任心，能坚持整理书包、照顾盆栽。\n缺点：受挫易急躁，积木倒就哭闹；注意力易分散，写作业常被外界干扰；有时固执，天冷非要穿薄裙，不愿接受"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子在英文写作和语法方面，通常能完成到什么水平？",
                "answer": [
                    "写5–7句连贯段落（现在/一般过去时），能写请假条、日记。"
                ]
            },
            {
                "question_section_name": "学业表现",
                "question_type": 1,
                "question": "孩子是否参加过以下英语考试？请选择最近一次且成绩最高的一项。",
                "answer": [
                    "KET Distinction"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "孩子目前是否参加过学科补习班？主要情况是？",
                "answer": [
                    "没有参加过补习班"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "孩子平时会不会主动去读课外书？通常会选择哪些类型的书？",
                "answer": [
                    "会主动读，但多是自己喜欢的书"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "用一句话来描述孩子的写作水平，更接近哪种？",
                "answer": [
                    "能完成规定题目的作文，条理基本清楚，但常依赖模板，细节少。"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "孩子在玩推理游戏或遇到复杂问题时，会不会主动一步步分析并寻找解决办法？",
                "answer": [
                    "有兴趣，会分析一些"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "在课堂或和别人交流时，孩子会不会主动表达自己的看法？别人能不 能听懂？",
                "answer": [
                    "比较害羞，说得不清楚"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "当遇到不懂的问题时，孩子会怎么找答案？找到后会不会整理学习资料？",
                "answer": [
                    "会用网络或 AI 工具查找，并简单整理"
                ]
            },
            {
                "question_section_name": "学能表现",
                "question_type": 1,
                "question": "孩子在学习新知识后，通常能记住多久？记得牢不牢？",
                "answer": [
                    "记住一部分，但容易忘"
                ]
            }
        ]
    }
    req['student_info']['english_level'] = 'C1'
    req['student_info']['rate'] = 'B'
    req['student_info']['subject_interest'] = "艺术与人文类（绘画、写作、音乐、表演、文学历史），语文，数学"
    req['student_info']['profile_type'] = "SLPB｜体育推广人 🏟️"
    
    res = get_growth_advice_rules(req)

    get_report(res)

