import json

with open('/Users/rafantasy/Documents/低龄规划项目/code/resource/题目得分对应标签.json', 'r') as f:
    TAG_MAPPING_DATA = json.load(f)

for p_key in TAG_MAPPING_DATA:
    for s_key in TAG_MAPPING_DATA[p_key]:
        if s_key == '英语能力':
            continue
        for i in range(len(TAG_MAPPING_DATA[p_key][s_key]['选项标签映射'])):
            for key in TAG_MAPPING_DATA[p_key][s_key]['选项标签映射'][i]:
                tag = ''
                if key in ('A',"B"):
                    tag = '积极'
                else:
                    tag = '消极'
                TAG_MAPPING_DATA[p_key][s_key]['选项标签映射'][i][key] = TAG_MAPPING_DATA[p_key][s_key]['选项标签映射'][i][key] + '-' + tag

json_data = json.dumps(TAG_MAPPING_DATA,indent=4,ensure_ascii=False)
with open('data.json', 'w') as file:
    file.write(json_data)