import pandas as pd


def eval_result():
    df = pd.read_excel('/root/code/ai_based_education/data/Mock1_2.xlsx',sheet_name=None)['Mock1'].fillna('')
    # print(df.columns)
    """
    Index(['维度', '题号', '问题类型', '子维度', '问题', '选项A', '选项B', '选项C', '选项D', '选项E',
       '选项F', '提示词（开放式问题UI展示）', '学生示例（开放式问题UI展示）', '家长示例（开放式问题UI展示）', '计算规则',
       'Mock答案1', 'Mock答案2', 'Mock答案3'],
      dtype='object')
    """
    res = [[],[],[]]
    for i in range(len(df)):
        item = df.iloc[i]
        question_section_name = item['维度']
        question_type = 1 if item['问题类型'] == '选择题' else 2
        question = item['问题']
        if item['子维度'] in ['教育期待','亲子关系与陪伴']:
            question = question.split('家长作答版：')[1].strip('✦ “').strip('“').strip()
        ans_1 = item['Mock答案1（5年级）']
        ans_2 = item['Mock答案2（5年级）']
        ans_3 = item['Mock答案3（7年级）']
        res[0].extend([
            {
            'question_section_name': question_section_name,
            'question_type': question_type,
            'question': question,
            'answer': ans_1
            }
        ])
        res[1].extend([
            {
            'question_section_name': question_section_name,
            'question_type': question_type,
            'question': question,
            'answer': ans_2
            }
        ])
        res[2].extend([
            {
            'question_section_name': question_section_name,
            'question_type': question_type,
            'question': question,
            'answer': ans_3
            }
        ])
    return res

def main(idx):
    results = eval_result()
    req = {
        "student_info": {
            "name": "李同学",
            "gender": "男",
            "school_type": "公立",
            "current_grade": "G5",
            "city_location": "深圳",
            "college_goal_path": ["港澳台本科"],
            "id": "11223"
        },
        "eval_result": results[idx]
    }
    
    import json
 
    # print(json.dumps(req,indent=4,ensure_ascii=False))
    return req

if __name__ == '__main__':
    main()
