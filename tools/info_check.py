import sys
import json

'''
输入参数格式校验
'''
def input_valid_instant_profile(req_input):
    if ('student_info' not in req_input) or ('eval_result' not in req_input):
        return False
    
    if ('name' not in req_input['student_info'])\
        or ('gender' not in req_input['student_info'])\
        or ('school' not in req_input['student_info'])\
        or ('school_type' not in req_input['student_info'])\
        or ('current_grade' not in req_input['student_info'])\
        or ('city_location' not in req_input['student_info'])\
        or ('college_goal_path' not in req_input['student_info'])\
        or ('id' not in req_input['student_info']):
        return False

    return True 
    

def input_valid_growth_advice(req_input):
    if ('student_info' not in req_input) or ('eval_result' not in req_input):
        return False
    
    if ('name' not in req_input['student_info'])\
        or ('gender' not in req_input['student_info'])\
        or ('school' not in req_input['student_info'])\
        or ('school_type' not in req_input['student_info'])\
        or ('current_grade' not in req_input['student_info'])\
        or ('city_location' not in req_input['student_info'])\
        or ('college_goal_path' not in req_input['student_info'])\
        or ('subject_interest' not in req_input['student_info'])\
        or ('profile_type' not in req_input['student_info'])\
        or ('english_level' not in req_input['student_info'])\
        or ('rate' not in req_input['student_info'])\
        or ('id' not in req_input['student_info']):
        return False

    return True 
