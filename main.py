from study.agent import run_agent
from study.memory import Threememory

def main():
    memory = Threememory()
    while True:
        question = input("请输入你的问题(输入exit退出):")
        if question.lower() == "exit":
            break
        result = run_agent(question,memory)
        print(result)


if __name__ == "__main__":
    main()
