# -*- coding: utf-8 -*-

def str2list(input_str):
    """将"4-5年级"类似的字符串转换为list"""
    if '通用' == input_str:
        return [100]
    
    raw_list = input_str.replace('年级','').split('-')

    assert len(raw_list) in [1,2]

    if len(raw_list) == 2:
        start = int(raw_list[0])
        end = int(raw_list[1])
    else:
        start = int(raw_list[0])
        end = int(raw_list[0])

    return [start+i for i in range(end-start+1)]