import pandas as pd
import json

def load_evidence(talent_dim, grade):
    config_file = '/root/code/ai_based_education/resource/SHAI_8字母均衡证据模板_分年级版.xlsx'
    
    raw_data = pd.read_excel(config_file,sheet_name=None)
    # print(raw_data.keys())
    # dict_keys(['A vs S', 'L vs J', 'I vs P', 'R vs B'])
    
    talent_dim = talent_dim.replace('_', ' vs ') 
    
    def split_grade(x):
        x = x.strip().replace('G','')
        grade_info = [int(item) for item in x.split('-')]
        grade_list = ['G'+str(i+grade_info[0]) for i in range(grade_info[-1]-grade_info[0]+1)]
        
        return ','.join(grade_list)
    
    # 筛选人才维度 
    target = raw_data[talent_dim]
    
    # 筛选年级
    target['年级'] = target['年级'].map(split_grade)
    target = target[target['年级'].str.contains(grade)]
    
    def talent_insert(x):
        talent, tag = x.split(' ')
        talent_def = ''
        if 'A' in x:
            talent_def = '体育突出型'
        elif 'S' in x:
            talent_def = '体育一般型'
            tag = '弱'
        elif 'L' in x:
            talent_def = '领导型'
        elif 'J' in x:
            talent_def = '协作执行型'
            tag = '弱'
        elif 'I' in x:
            talent_def = '艺术/人文突出型'
        elif 'P' in x:
            talent_def = '艺术一般/偏实用型'
            tag = '弱'
        elif 'R' in x:
            talent_def = '理工思维突出型'
        elif 'B' in x:
            talent_def = '理工思维一般型'
            tag = '弱'
        
        return talent_def+'-'+tag

    target['分类'] = target['分类'].map(talent_insert)
    
    tags_list = list(target['分类'].unique())

    res_def = {}
    res_score = {}
    for tag in tags_list:
        tmp_evi = target[target['分类']==tag]
        res_def[tag] = [tmp_evi.iloc[i]['证据'].strip() for i in range(len(tmp_evi))]
        res_score[tag] = [{tmp_evi.iloc[i]['证据'].strip():'具体分数'} for i in range(len(tmp_evi))]

    # print(json.dumps(res_def,indent=4,ensure_ascii=False))
    # print(json.dumps(res_score,indent=4,ensure_ascii=False))
    return res_def, res_score


if __name__ == '__main__':
    load_evidence('R_B', 'G5')


