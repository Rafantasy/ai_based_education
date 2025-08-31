# 测试
- 安装包要求：flask
- step1: 执行run_app.py(保证在后台一直run)
- step2: 执行 test.py

# run_app说明
- produe_growth_advice：生成年级成长建议
- get_growth_advice_rules：生成知识库召回规则
  - 示例及字段说明
    ---
    {
        "name": "李同学",
        "school_type": "学校类型",
        "current_grade": "当前年级",
        "profile_type": "画像类型",
        "rate": "档次(A档/B档，通过英语测试结果划分得到)",
        "college_goal_path": "目标升学路径",
        "subject_interest": "感兴趣学科",
        "recall_rules": {
            "university_recommendation": {
                "db_name": "知识库名称",
                "requirement": "生成要求（对应"0825升学规划&成长建议板模版.xlsx"中"标准内容/条目（输出）"这一列）",
                "module_name": "该条规则召回的知识最终应该包含在每一年级成长建议中的哪一部分；如果这里包含多个模块，则由大模型自行判断"
            },
            "grade_list": {
                "G3": [
                    {
                        "db_name": "知识库名称（可能包含多个，用","分割）",
                        "requirement": "生成要求（对应"0825升学规划&成长建议板模版.xlsx"中"标准内容/条目（输出）"这一列）",
                        "module_name": "该条规则召回的知识最终应该包含在每一年级成长建议中的哪一部分；如果这里包含多个模块，则由大模型自行判断"
                    },
                    ...
                ]
            }
        }
    }
    ---
  - 特殊说明：db_name中除了所用知识库名称之外，还可能出现“固定值”，“大模型生成”这两个值；
    - 如果db_name='固定值'，让大模型对"requirement"字段的内容进行改写，然后放到最终成长建议里；
    - 如果db_name=='大模型'，让大模型参考"requirement"字段的内容进行生成，然后放到最终成长建议里。