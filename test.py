# -*- encoding:utf-8 -*-
import requests
import json
from data import proc

if __name__ == '__main__':
    headers = {'content-type': 'application/json'}
    
    # req = {}
    # pred_data = {}
    # pred_data['name'] = '李同学'
    # pred_data['gender'] = '男'
    # pred_data['city_location'] = 'SH'
    # pred_data['school_type'] = '公立'
    # pred_data['current_grade'] = 'G3'
    # pred_data['profile_type'] = 'LRDE'
    # pred_data['english_level'] = 'cefr-A2'
    # pred_data['rate'] = 'A档'
    # pred_data['college_goal_path'] = ['美国本科']
    # pred_data['subject_interest'] = '数学'
    # pred_data['id'] = '12345'
    # req['student_info'] = pred_data
    # req['eval_result'] = [ 
    #     {   
    #         "question_section_name":"性格特征",
    #         "question_type":2,
    #         "question":"如果让你描述一下孩子的性格（优点和短板），你会怎样描述？",
    #         "answer":"我觉得自己挺开朗的，愿意帮助别人，但有时候太急躁。"
    #     }   
    # ]

    req = proc.main(2)

    req = {
        "student_info": {
            "name": "大头儿子",
            "gender": "男",
            "school_type": "国际",
            "current_grade": "G12",
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

    # print(req)
    
    # # 开放问题小结
    # r = requests.post("http://127.0.0.1:5000/open_question", data=json.dumps(req), headers=headers)
    
    # # 人才画像
    r = requests.post("http://127.0.0.1:5000/instant_profile", data=json.dumps(req), headers=headers)
    
    # # swot分析
    # r = requests.post("http://127.0.0.1:5000/swot", data=json.dumps(req), headers=headers)
    
    # # 成长建议
    # r = requests.post("http://127.0.0.1:5000/growth_advice", data=json.dumps(req), headers=headers)
    
    print(json.dumps(r.json(),indent=4,ensure_ascii=False))
