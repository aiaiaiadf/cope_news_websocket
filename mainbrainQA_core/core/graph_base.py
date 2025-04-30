import os
import abc
import copy
from typing import Dict
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from mainbrainQA_core.common.utils import show_lg
from mainbrainQA_core.core.model_base import model_base
from mainbrainQA_core.core.state_base import MainGraphState,StrSateBase
from mainbrainQA_core.core.prompt_base import streamlinehistory_msg,streamlinehistory_prompt

# def UserThreadId(thread_id:str,user_id:str="user_1")->Dict:
#     return {"configurable":{"thread_id":thread_id,"user_id":user_id,"recursion_limit": 500}} 

def UserThreadId(thread_id:str,user_id:str="user_1")->Dict:
    return {"configurable":{"thread_id":thread_id,"user_id":user_id,"recursion_limit": 100}} 

def CheckpointMemory(db_file:str=""):
    if db_file == "":
        return MemorySaver()
    else:
        return SqliteSaver.from_conn_string(db_file)



class SubGraphBase():
    def __init__(self) -> None:
        builder = StateGraph(MainGraphState,input=MainGraphState,output=MainGraphState)
        self.setattr()
        self.__call__(builder)
    @abc.abstractmethod
    def setattr(self):
        """
        nodes      定义工作流s     self.nodes = {"hello":HelloWorld}
        config     定义线程id      self.config = config
        ckp        定义检查点      self.ckp = memory
        这里需要一个条件边 做路由
        """
        pass
        
    @abc.abstractmethod
    def __call__(self,builder):
        """
        定义图络结构
        builder.add_node("hello",HelloWorld)
        builder.add_edge(START,"hello")
        builder.add_edge("hello",END)
        
        self.app = builder.compile(checkpointer=self.ckp)
        """
        pass
    def _print_class_name(self):
        show_lg(f"start runing  {self.__class__.__name__}")
    def invoke(self,state:MainGraphState):
        self._print_class_name()
        state = self.app.invoke(state,config=self.config)
        # state.latest_response = res
        return state
    async def ainvoke(self,state:MainGraphState):
        self._print_class_name()
        state = await self.app.ainvoke(state,config=self.config)
        # state.latest_response = res
        return state
    
    # def draw_struct(self,file,xray=1):
    #     graph_txt = self.app.get_graph(xray=xray).draw_png()
    #     assert graph_txt,"image data is null"
    #     with open(file,'wb') as f:
    #         f.write(graph_txt)
            
            

class  MainGraphBase():
    def __init__(self) -> None:
        builder = StateGraph(MainGraphState,input=MainGraphState,output=MainGraphState)
        self.setattr()
        self.__call__(builder)
    @abc.abstractmethod
    def setattr(self):
        """
        nodes      定义工作流s     self.nodes = {"hello":HelloWorld}
        config     定义线程id      self.config = config
        ckp        定义检查点      self.ckp = memory
        这里需要一个条件边 做路由
        """
        pass
        
    @abc.abstractmethod
    def __call__(self,builder):
        """
        定义图络结构
        builder.add_node("hello",HelloWorld)
        builder.add_edge(START,"hello")
        builder.add_edge("hello",END)
        
        self.app = builder.compile(checkpointer=self.ckp)
        """
        pass
 
    def invoke(self,state:MainGraphState):
        state = self.app.invoke(state,config=self.config)
        # state_ = copy.deepcopy(state)
        # print(f"state <invoke<<<    {state_}")
        # state_ = self.app.invoke(state_,config=self.config)
        # print("<><<<<   ",self.app.__dict__)
        # print(f"state >invoke>>>    {state_}")
        return state
    async def ainvoke(self,state:MainGraphState):
        state = await self.app.ainvoke(state,config=self.config)
        return state
    
    def stream(self,state:MainGraphState):
        state = self.app.invoke(state,config=self.config)
        res = state.latest_response
        for out in res:
            yield(out)
    async def astream(self,state:MainGraphState):
        state = await self.app.ainvoke(state,config=self.config)
        res = state.latest_response
        for out in res:
            yield(out)
        
    # def draw_struct(self,file,xray=1):
    #     graph_txt = self.app.get_graph(xray=xray).draw_png()
    #     assert graph_txt,"image data is null"
    #     with open(file,'wb') as f:
    #         f.write(graph_txt)