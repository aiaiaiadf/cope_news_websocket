import pandas as pd
from copy import deepcopy
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_novel.prompt_cope_novel import novel_msg_1,novel_prompt_1,novel_msg_2,novel_prompt_2,novel_msg_3,novel_prompt_3
from common.utils import show_lg,show_db
from common.llm_utils import str2dict,duplicate_removal


from langgraph.graph import END,START,StateGraph
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory

test = False

class AnalysisQuery(PluginBase):
    def process(self,state):
        if test:
            show_db("AnalysisQuery")
        # show_db(f">state>>   {state}")
        query = state.parameters["query"]
        novel_prompt_1.set_system_msg(novel_msg_1)
        novel_prompt_1.set_human_msg(query)
        msg = novel_prompt_1.get_messages()
        # show_db(f">>>   {msg}")
        llm =  model_base().init_tongy()["chat"]
        res = llm.invoke(msg).content
        
        b = state.parameters.get("novel","")
        if b!="" and res=='Generate':
            res = ["Generate","Writer"]
        if state.isLoop:
            state.isLoop = False
       
        state.parameters.update({"routing_1":res})
        # show_db(res)
        return state

    
def routing(state):
    if test:
        show_db(state)
    res = state.parameters["routing_1"]
    # show_db(f">> routing {res}")
    if isinstance(res,list):
        return res
    else:
        return [res]
    
class Generate(PluginBase):
    def process(self,state):
        if test:
            show_db("Generate")
        query =  state.parameters["query"]
        novel_prompt_2.set_system_msg(novel_msg_2)
        novel_prompt_2.set_human_msg(query)
        msg = novel_prompt_2.get_messages()
        llm =  model_base().init_tongy()["chat"]
        res = llm.invoke(msg).content
        res = str2dict(res)
        # show_db(res)
        # state.parameters = deepcopy({"novel":res})
        # state.parameters.update({"novel":res})
        state.messages += [res]
        show_db(res)
        return state
    
class Improve(PluginBase):
    def process(self,state:MainGraphState):
        if test:
            show_db("Improve")
        # print(">state>>  ",state)
        # print(">state>>  ",state.parameters)
        
        query = state.parameters["query"]
        # novel_prompt_3.set_system_msg(novel_msg_3.format(state.parameters["novel"]))
        novel_prompt_3.set_system_msg(novel_msg_3.format(state.messages[-1]))
        novel_prompt_3.set_human_msg(query)
        msg = novel_prompt_3.get_messages()
            
        llm =  model_base().init_tongy()["chat"]
        res = llm.invoke(msg).content
        res = str2dict(res)
        show_db(res)
        # state.parameters = deepcopy({"novel":res})
        # state.parameters.update({"novel":res})
        state.messages += [res]
        return state


class Writer(PluginBase):
    def process(self,state):
        if test:
            show_db("Writer")
        Pth = "new_novel.md"
        with open(Pth,'w') as file:
            file.write(f"# {state.messages[-1]['title']}\n")
            file.write(f"\n")
            file.write(f"## abstract\n")
            file.write(f" {state.messages[-1]['abstract']}\n")
            file.write(f"\n")
            file.write(f"## text\n")
            file.write(f" {state.messages[-1]['text']}\n")
            file.write(f"\n")
            file.write(f"## summarize\n")
            file.write(f"{state.messages[-1]['summarize']}\n")
            file.write(f"\n")
        show_db(f"saved to {Pth}. done! ")
        return state
    



class novel_once(SubGraphBase):
    def setattr(self):
        self.nodes = {
                      "AnalysisQuery":AnalysisQuery().handler,
                      "Generate":Generate().handler,
                     "Improve":Improve().handler,
                     "Writer":Writer().handler,
                      }
        self.config = UserThreadId("ny_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        builder.recursion_limit =100
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,["Improve","Generate","Writer"])
        for n in list(self.nodes.keys()):
            if n not in ["AnalysisQuery"]:
                builder.add_edge(n,END)
    
        # self.app = builder.compile(checkpointer=self.ckp, interrupt_before=["AnalysisQuery"])
        self.app = builder.compile(checkpointer=self.ckp)
    def invoke(self,state:MainGraphState):
        for event in self.app.stream(state, self.config, stream_mode="values"):
            # print("event>>>   ",event)
            ...
            # state.parameters.update(event)
        return state
        

class cope_novel(PluginBase):
    def process(self,state):
        bot =novel_once()
        while True:

            state = bot.invoke(state)
            query = state.parameters["query"]
            query = input("human: ")
            if query == "q":
                break
            state = MainGraphState(
                user_input=[],
                parameters={"query":query}
            )
        return state        


    