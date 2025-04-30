from abc import abstractmethod
from langchain_core.messages import SystemMessage,HumanMessage

class prompt_base():
    def __init__(self) -> None:
        self.messages = []

    def set_system_msg(self,s1:str=""):
        self.system_msg = SystemMessage(
            content=s1)
    
    def set_human_msg(self,s1:str):
        self.human_msg = HumanMessage(
                content=s1)

        if len(self.messages)==2:
            self._release()
        self.messages = [self.system_msg,self.human_msg]
    def get_messages(self):
        return self.messages
    
    def aget_messages(self):
        return {"SystemMessage":self.messages[0],"HumanMessage":self.messages[1]} 
    def _release(self):
        self.messages = []
    








streamlinehistory_prompt = prompt_base()
streamlinehistory_msg ="""
        # 角色
        你是一个聊天记录总结助手。
        ## 技能
        使用最简洁的语言，总结HumanMessage和AIMessage的聊天内容。你需要同时关注HumanMessage和AIMessage值。
        """
