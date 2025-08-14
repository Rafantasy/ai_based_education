import json

with open('/Users/rafantasy/Documents/低龄规划项目/code/resource/题目得分对应标签.json', 'r') as f:
    TAG_MAPPING_DATA = json.load(f)

with open('/Users/rafantasy/Documents/低龄规划项目/code/resource/画像及计算规则.json', 'r') as f:
    PROFILE_DATA = json.load(f)


def compute_sub_dim_score(qa_data):
    dim_score = {}

    for p_key in qa_data:
        total_question_num = sum([len(TAG_MAPPING_DATA[p_key][s_key]['选项标签映射']) for s_key in TAG_MAPPING_DATA[p_key]])
        if '学业表现' == p_key:
            total_question_num += 1 
        dim_score[p_key] = {
            'sub_question_score':[0 for x in range(total_question_num)]
        }
        for s_key in qa_data[p_key]: 
            # TODO: 开放性问题处理
            if '' == s_key:
                continue

            tmp_tag_data = TAG_MAPPING_DATA[p_key][s_key]['选项标签映射']

            # 实际回答题目数量应该和知识库里题目保持一致
            assert len(qa_data[p_key][s_key]) == len(tmp_tag_data)

            tag_opt_list = []
            # 提取知识库中每个子维度问题的候选选项列表
            if '英语能力' != s_key:
                """
                # 对标签选项进行排序，方便计算分数
                排序后的选项为[C,B,A]，则分数分别为[0,1,2]

                # 英语能力的标签为正确答案，因此不用排序
                """
                tag_opt_list = [[opt for opt in tmp_tag_data[i]] for i in range(len(tmp_tag_data))]
                for i in range(len(tag_opt_list)):
                    sub_opt_list = tag_opt_list[i]
                    # sub_opt_list.sort(key=lambda x:list(x.keys())[0],reverse=True)
                    sub_opt_list.sort(reverse=True)
                    tag_opt_list[i] = sub_opt_list
            else:
                tag_opt_list = tmp_tag_data 

            if s_key not in dim_score[p_key]:
                dim_score[p_key][s_key] = 0

            for i in range(len(tag_opt_list)):
                tmp_ans = qa_data[p_key][s_key][i]['answer'].strip()
                tmp_score = 0
                if '英语能力' != s_key: 
                    tmp_score = tag_opt_list[i].index(tmp_ans)
                else:
                    tmp_score = 1 if tmp_ans == tag_opt_list[i] else 0 

                dim_score[p_key][s_key] += tmp_score
                dim_score[p_key]['sub_question_score'][qa_data[p_key][s_key][i]['question_idx']-1] = tmp_score
    
    return dim_score


def compute_sub_dim_tag(qa_data, sub_dim_score):
    dim_tag = {}

    for p_key in qa_data:
        dim_tag[p_key] = {}
        for s_key in qa_data[p_key]:
            if '' == s_key:
                continue
            if '英语能力' != s_key:
                dim_tag[p_key][s_key] = []

                # TODO: 开放性问题处理
                if '' == s_key:
                    continue

                tmp_tag_data = TAG_MAPPING_DATA[p_key][s_key]['选项标签映射']

                # 实际回答题目数量应该和知识库里题目保持一致
                assert len(qa_data[p_key][s_key]) == len(tmp_tag_data)

                for i in range(len(tmp_tag_data)):
                    tmp_ans = qa_data[p_key][s_key][i]['answer'].strip()
                    dim_tag[p_key][s_key].extend([tmp_tag_data[i][tmp_ans]])
            else:
                tmp_tag_data = TAG_MAPPING_DATA[p_key][s_key]['回答标签映射']
                score_level = [int(x) for x in tmp_tag_data]
                score_level.sort()

                target_level = 0
                tmp_sub_dim_score = sub_dim_score[p_key][s_key]
                for i in range(len(score_level)):
                    if tmp_sub_dim_score <= score_level[i]:
                        target_level = score_level[i]
                        break
                dim_tag[p_key][s_key] = tmp_tag_data[str(target_level)]['标签']
    
    return dim_tag


def compute_profile_score(sub_dim_score):
    profile_list = list(PROFILE_DATA.keys())

    profile_score = {}

    for profile in profile_list:
        profile_score[profile] = 0
        tmp_rule = PROFILE_DATA[profile]
        if len(tmp_rule['precondition']) > 0:
            precondition_flag = 0
            for i in range(len(tmp_rule['precondition'])):
                tmp_precond = tmp_rule['precondition'][i]
                tmp_score = sum([sub_dim_score[tmp_precond['dimension']]['sub_question_score'][x-1] for x in tmp_precond['question_list']])
                if tmp_score >= tmp_precond['score_threshold']:
                    precondition_flag = 1
                    break
            if precondition_flag: 
                profile_score[profile] = sum([sub_dim_score[tmp_rule['dimension']]['sub_question_score'][x-1] for x in tmp_rule['question_list']])
        else:
            profile_score[profile] = sum([sub_dim_score[tmp_rule['dimension']]['sub_question_score'][x-1] for x in tmp_rule['question_list']])


    return profile_score


def get_profile(profile_score):
    res = ''
    max_score = 0
    for profile in profile_score:
        if max_score < profile_score[profile]:
            max_score = profile_score[profile]
            res = profile
    
    return res