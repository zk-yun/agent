import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from study.memory import Threememory
import requests
from study.tool import get_now_time,get_weather,search_web,calculate

load_dotenv()  

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = os.getenv("DEEPSEEK_API_BASE")
)

tools = [{
    "type":"function",
    "function":{
        "name":"get_weather",
        "description":"当用户需要查询某座城市的天气时,调用该函数去查询天气信息"
                      "返回该城市指定日期的最高以及最低温度以及天气情况",
        "parameters":{
            "type":"object",
            "properties":{
                "city":{
                    "type":"string",
                    "description":"需要查询天气的城市名称"
                },
                "day":{
                    "type":"integer",
                    "description":"查询的日期,查询今天则day为0,查询明天则day为1,查询后天则day为2"
                }
            },"required":["city","day"]
        }
    }
},
    {
    "type":"function",
    "function":{
        "name":"search_web",
        "description":"当用户需要查询某个关键词的相关信息时,调用该函数去搜索引擎查询相关信息",
        "parameters":{
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":"需要搜索的关键词"
                }
            },"required":["query"]
        }
    }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4'",
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_now_time",
            "description":"当用户需要获取当地时间或者当你需要得知现在是什么时候时调用该函数"
                        "返回当前时间,格式为YYYY-MM-DD HH-MM-SS",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    }
]

# def get_now_time():
#     time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return time

# def get_weather(city:str,day:int = 0) ->str:
#     """"
#     这是可以查询今天以及未来两天天气的工具函数

#     Args:
#     city: 城市名称
#     day: 查询的日期,今天则days为0,1明天则days为1,后天则days为2

#     Returns:
#     返回city的天气信息
#     """
#     url ="https://api.seniverse.com/v3/weather/daily.json"
#     api_key = os.getenv("SENIVERSE_API_KEY")

#     headers = {
#         "user-agent":
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
#     }

#     params = {
#         "key":api_key,
#         "location":city,
#         "language":"zh-Hans",
#         "unit":"c",
#         "start":0,
#         "days":3
#                 }
#     response = requests.get(url,params=params,headers=headers)
#     if response.status_code == 200:
#         response = response.json()
#         result = response["results"][0]
#         if city not in result["location"]["name"]:
#             raise ValueError("城市名称错误")
#         date = result["daily"][day]["date"]
#         text = result["daily"][day]["text_day"]
#         high = result["daily"][day]["high"]
#         low = result["daily"][day]["low"]
#         return f"{city}在{date}的天气是{text},最高温度{high}°C,最低温度{low}°C"
#     else:
#         return f"查询天气失败,状态码:{response.status_code}"

# def search_web(query:str) ->str:
#     """
#     这是一个模拟搜索引擎的工具函数

#     Args:
#     query: 需要搜索的关键词

#     Returns:
#     返回搜索结果
#     """
#     search_results = {
#         "Python": "Python是一种流行的编程语言,广泛用于数据科学、人工智能和Web开发。",
#         "OpenAI": "OpenAI是一家人工智能研究公司,致力于推动人工智能技术的发展和应用。",
#         "深度学习": "深度学习是一种机器学习方法,使用多层神经网络来建模复杂的数据模式。"
#     }
#     return search_results.get(query, "抱歉，我没有找到相关的搜索结果。")

# def calculate(expression: str) -> str:
#     """安全的数学计算工具。

#     Args:
#         expression: 数学表达式字符串。

#     Returns:
#         计算结果字符串。
#     """
#     try:
#         allowed_chars = set("0123456789+-*/().%^ ")
#         if not all(c in allowed_chars for c in expression):
#             return "错误：表达式包含不允许的字符"
#         result = eval(expression)
#         return f"计算结果：{result}"
#     except Exception as e:
#         return f"计算错误：{str(e)}"
    
search_tools = {
    "get_weather": get_weather,
    "search_web": search_web,
    "calculate": calculate,
    "get_now_time": get_now_time
}

def llm_response(prompt:str) ->str:
    """
    这是最基础的LLM调用方式---输入提示词,得到模型回复,

    这个是agent最底层操作,让LLM思考,所有逻辑都建立在这上面

    Args:
    prompt: 提示词,用户输入的问题或指令

    Returns:
    LLM生成的回复或文本
    """
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [{"role":"user","content":prompt}],
        temperature = 0.8,
        top_p = 0.9,
        max_tokens = 2048,
        stream = False
    )
    return response.choices[0].message.content

def run_agent(user_message:list,memory:Threememory,max_stage:int=5):
    """
    这是一个简单的React agent

    这个函数不加任何框架,是最底层的一个react循环,
    基本所有的agent框架都是在这基础上进行加工,即封装和增强
   
    Args:
    user_messages: 用户输入的消息
    max_stage:循环的最大轮次,可防止死循环

    Returns:
    agent的最终回复
    """
    sys_memory = memory.send_memory_to_llm()
    messages = [
        {"role": "system", "content":
          f"你是一个有用的 AI 助手。当需要获取最新信息或执行计算时，请使用提供的工具。\n{sys_memory}"},
        {"role": "user", "content": user_message}
    ]
    for stage in range(max_stage):
        response = client.chat.completions.create(
            model = "deepseek-chat",
            tools = tools,
            messages = messages,
            stream = False
        )
        reply = response.choices[0].message
        messages.append(reply)
        if not reply.tool_calls:
            final_reply = reply.content
            break
        tool_call = reply.tool_calls[0]
        for tool_call in reply.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"第{stage+1}轮调用工具:{name}")
            function = search_tools.get(name)
            if function is None:
                result = f"错误：未找到工具 {name}"
            else:
                result = function(**args)
                memory.set_working(name,result)
            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content":result
            })
    if not final_reply:
        print("当达到最大轮次时,总结目前得到的信息,给出结果")
        messages.append({"role":"user",
                         "content":"请基于你现在得到的信息给我结果,并且说缺什么,哪些错了"})
        response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = messages,
        stream = False
    )
        final_reply = response.choices[0].message.content
    memory.add_conversation(user_message,final_reply)
    return final_reply
       

