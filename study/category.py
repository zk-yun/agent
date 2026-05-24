from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = os.getenv("DEEPSEEK_API_BASE")
)

def call_llm_with_json(prompt:str,system_prompt:str=""):
    """
    这是一个llm的调用函数,返回json格式

    Args:
    prompt: 用户输入的提示词
    system_prompt: 系统提示词,可以用来引导模型的行为,比如让模型以某个角色的身份去回答问题"

    Returns:
    返回模型的回答,格式为json
    """
    messages =[]
    if system_prompt:
        messages.append({"role":"system","content":system_prompt})
    messages.append({"role":"user","content":prompt})
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = messages,
        response_format = {
            "type":"json_object"
        },
        stream = False
    )
    reply = response.choices[0].message.content
    return json.loads(reply)

def plan_execute(task:str)->dict:
    """"
    这是agent中的plan_execute类型,
    调用该函数可以将用户的任务分为多个步骤,然后再依次进行,
    适合处理复杂任务,缺点是不灵活

    Args:
    task: 用户输入的任务
    """
    system_prompt = (""""
        角色
        -你是一个任务专家,你可以将用户的任务分为多个子任务,
        规则
        -你会将任务以json格式返回,
        -格式为:{"step1":[{"step2":xxx,"step3":xxx,"step4":step5,"step6":[],...}]}
        -并且你可以说出每个步骤依赖哪个步骤
        """)
    user_prompt = f"请将以下任务分解为多个步骤:{task}"
    return call_llm_with_json(user_prompt,system_prompt)

def reflect_message(original:str,criteria:str):
    sys_prompt = (
        "你是一个反思专家,你可以根据用户给出的标准来反思和改进原始的回答"
        "你需要根据标准来分析原始回答的优缺点,并给出改进建议,并且必须是以json格式返回"
        '{"h1":xxx,"h2":[{"h3":xxx}]}'
    )
    prompt = (
        f"原始回答:{original}\n"
        f"评判标准:{criteria}\n"
        f"请评估并改进"
    )
    return call_llm_with_json(prompt,sys_prompt)
