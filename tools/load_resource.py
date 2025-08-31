import pandas as pd
from utils.func_str import str2list

def load_growth_advice_rule():
    raw_data = pd.read_excel('./resource/升学规划&成长建议板模版.xlsx',sheet_name='模版（通用&个性化）').fillna('')

    # 补充列
    value = """db_英语能力知识库,db_A档&B档升学路径对标本科要求知识库
db_A档&B档升学路径对标本科要求知识库
固定值
固定值
固定值
db_【画像知识库】,db_竞赛_活动知识库
db_英语能力知识库
固定值
db_英语能力知识库
db_竞赛_活动知识库
大模型生成
大模型生成
db_【画像知识库】,db_竞赛_活动知识库
大模型生成
大模型生成
大模型生成
大模型生成
db_【画像知识库】
大模型生成
大模型生成
大模型生成
大模型生成
大模型生成
db_A档&B档升学路径对标本科要求知识库
固定值
db_【画像知识库】,db_A档&B档升学路径对标本科要求知识库,db_英语能力知识库
db_【画像知识库】,db_A档&B档升学路径对标本科要求知识库,db_英语能力知识库
固定值
大模型生成
db_竞赛_活动知识库
db_竞赛_活动知识库
db_竞赛_活动知识库,db_【美国大学夏校知识库】
固定值
固定值
db_A档&B档升学路径对标本科要求知识库,db_英语能力知识库
大模型生成
大模型生成
db_竞赛_活动知识库
db_竞赛_活动知识库
db_科研知识库
大模型生成
db_【美国大学夏校知识库】
大模型生成
db_A档&B档升学路径对标本科要求知识库""".split('\n')
    raw_data['知识库'] = ''
    for i in range(len(raw_data)):
        raw_data.loc[i, '知识库'] = value[i]

    # 拆分人才画像
    cols = ['人才画像']
    df1 = raw_data.drop(columns=cols,axis=1)
    for x in cols:
        df1 = df1.join(raw_data[x].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename(x))
    df1 = df1.reset_index(drop=True)

    # 拆分适用年级
    cols = ['适用年级']
    df2 = df1.drop(columns=cols,axis=1)
    for x in cols:
        df2 = df2.join(df1[x].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename(x))
    df2 = df2.reset_index(drop=True)

    # 适用年级转换为list
    df2['适用年级'] = df2['适用年级'].apply(str2list)

    # 继续拆分适用年级
    df3 = df2.explode('适用年级')

    return df3