
class Threememory:
    def __init__(self,max_term:int=10):
        self.short_memory = []
        self.working = {}
        self.long_memory = []
        self.max_term = max_term
        self.summary = ""
 
    def add_conversation(self,user_prompt:str,assistant_reply:str):
        self.short_memory.append((user_prompt,assistant_reply))
        if len(self.short_memory) > self.max_term:
            self.compress_memory()

    def compress_memory(self):
        old_pair = self.short_memory.pop(0)
        combine = f"用户问:{old_pair[0]}\n助手答:{old_pair[1]}"
        self.long_memory.append(combine)
        if not self.summary:
            self.summary = f"早期的对话摘要:\n{combine}"
        else:
            self.summary += f"\n...\n{combine}"

    def set_working(self,key:str,value:str):
        self.working[key] = value

    def get_working(self,key:str):
        return self.working.get(key,"")

    def send_memory_to_llm(self):
        part = []
        part.append(f"历史摘要:{self.summary}")
        if self.working:
            wk_items = "\n".join(f"{key}: {value}"for key,value in self.working.items())
            part.append(f"当前工作记忆:\n{wk_items}")
        if self.short_memory:
            sm_items = "\n".join(f"用户:{a[0]}\n助手:{a[1]}" for a in self.short_memory)
            part.append(f"近期对话:\n{sm_items}")
        return "\n".join(part)

