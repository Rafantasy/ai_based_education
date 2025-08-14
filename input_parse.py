import pandas as pd
import json

def parse(input_file):
    raw_data = pd.read_excel(input_file,sheet_name=None)
    # print(raw_data.keys())
    
    def single_student(key_info,key_qa):
        basic_info = raw_data[key_info].fillna('')
        columns = list(basic_info.columns)
        tmp_basic_info = [columns[0]+'：'+columns[1]]
        for i in range(len(basic_info)):
            tmp_basic_info.extend([basic_info.iloc[i][columns[0]] + '：' + basic_info.iloc[i][columns[1]]]) 
    
        qa_info = raw_data[key_qa].fillna('')
        tmp_qa_info = {}
        primary_dim = ''
        primary_q_idx = 0
        for i in range(len(qa_info)):
            item = qa_info.iloc[i]
            tmp_primary_dim = item['维度']
            tmp_sub_dim = item['子维度']
            tmp_ans = item['学生作答']

            # tmp_idex = item['题号']
            if tmp_primary_dim != primary_dim:
                primary_dim = tmp_primary_dim
                primary_q_idx = 0
                tmp_qa_info[primary_dim] = {}
            if tmp_sub_dim not in tmp_qa_info[primary_dim]:
                tmp_qa_info[primary_dim][tmp_sub_dim] = []

            primary_q_idx += 1
            tmp_qa_info[primary_dim][tmp_sub_dim].extend([{'answer':tmp_ans,'question_idx':primary_q_idx}]) 
    
        # print(json.dumps(tmp_qa_info,indent=4,ensure_ascii=False))
        # print(tmp_qa_info.keys())
        return tmp_basic_info, tmp_qa_info 

    student_list = []
    eval_qa_list = []
    
    res_info, res_qa = single_student('A同学基础信息','A同学答题记录')
    student_list.extend([res_info])
    eval_qa_list.extend([res_qa])
    
    res_info, res_qa = single_student('B同学基础信息','B同学答题记录')
    student_list.extend([res_info])
    eval_qa_list.extend([res_qa])


    res_info, res_qa = single_student('C同学基础信息','C同学答题记录')
    student_list.extend([res_info])
    eval_qa_list.extend([res_qa])


    res_info, res_qa = single_student('D同学基础信息','D同学答题记录')
    student_list.extend([res_info])
    eval_qa_list.extend([res_qa])

    res_info, res_qa = single_student('E同学基础信息','E同学答题记录')
    student_list.extend([res_info])
    eval_qa_list.extend([res_qa])

    return student_list, eval_qa_list 

if __name__ == '__main__':
    student_list, eval_qa_list = parse('/Users/rafantasy/Documents/低龄规划项目/5个学生的Mock样本.xlsx')
    print(student_list)