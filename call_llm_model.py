import os
from openai import OpenAI
import asyncio
import time
from datetime import datetime

import logging
logger = logging.getLogger("service_log")

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-fdfccf797a9042119a34ab37b00db290",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def call_model(msgs):
    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        # model="qwen3-30b-a3b-instruct-2507",
        model="qwen-max-latest",
        messages=msgs,
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
        extra_body={"enable_thinking": False},
        stream=True,
        stream_options={"include_usage": True}
    )

    result = ''
    for chunk in completion:
        # result += chunk.model_dump_json()['choices']
        if chunk.choices:
            result += chunk.choices[0].delta.content

    return result

async def async_call_model(talent_msg):
    loop = asyncio.get_running_loop()

    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型开始时间{start_time}")
    print("异步调用大模型开始时间",start_time)
    
    talent_dim,msgs = talent_msg
    model_resp = await loop.run_in_executor(None, call_model, msgs)
    
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"异步调用大模型结束时间{end_time}")
    print("异步调用大模型结束时间",end_time)
    
    return (talent_dim, model_resp)
    
async def run_async_tasks(talent_msg_list): 
    # 初始化任务
    tasks = [async_call_model(x) for x in talent_msg_list]

    # 执行任务
    results = await asyncio.gather(*tasks)

    return results


if __name__ == '__main__':
    talent_msg_list = [('A_S',[{'role':'user','content':'体育'}]),('R_B',[{'role':'user','content':'音乐'}])]
    res = asyncio.run(run_async_tasks(talent_msg_list))
    print(res)
