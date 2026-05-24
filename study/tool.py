from datetime import datetime
import os
import requests

def get_now_time():
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return time

def get_weather(city:str,day:int = 0) ->str:
    """"
    这是可以查询今天以及未来两天天气的工具函数

    Args:
    city: 城市名称
    day: 查询的日期,今天则days为0,1明天则days为1,后天则days为2

    Returns:
    返回city的天气信息
    """
    url ="https://api.seniverse.com/v3/weather/daily.json"
    api_key = os.getenv("SENIVERSE_API_KEY")

    headers = {
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
    }

    params = {
        "key":api_key,
        "location":city,
        "language":"zh-Hans",
        "unit":"c",
        "start":0,
        "days":3
                }
    response = requests.get(url,params=params,headers=headers)
    if response.status_code == 200:
        response = response.json()
        result = response["results"][0]
        if city not in result["location"]["name"]:
            raise ValueError("城市名称错误")
        date = result["daily"][day]["date"]
        text = result["daily"][day]["text_day"]
        high = result["daily"][day]["high"]
        low = result["daily"][day]["low"]
        return f"{city}在{date}的天气是{text},最高温度{high}°C,最低温度{low}°C"
    else:
        return f"查询天气失败,状态码:{response.status_code}"
def search_web(query:str) ->str:
    """
    这是一个模拟搜索引擎的工具函数

    Args:
    query: 需要搜索的关键词

    Returns:
    返回搜索结果
    """
    search_results = {
        "Python": "Python是一种流行的编程语言,广泛用于数据科学、人工智能和Web开发。",
        "OpenAI": "OpenAI是一家人工智能研究公司,致力于推动人工智能技术的发展和应用。",
        "深度学习": "深度学习是一种机器学习方法,使用多层神经网络来建模复杂的数据模式。"
    }
    return search_results.get(query, "抱歉，我没有找到相关的搜索结果。")

def calculate(expression: str) -> str:
    """安全的数学计算工具。

    Args:
        expression: 数学表达式字符串。

    Returns:
        计算结果字符串。
    """
    try:
        allowed_chars = set("0123456789+-*/().%^ ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"
    
search_tools = {
    "get_weather": get_weather,
    "search_web": search_web,
    "calculate": calculate
}