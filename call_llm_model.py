import os
from openai import OpenAI


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
