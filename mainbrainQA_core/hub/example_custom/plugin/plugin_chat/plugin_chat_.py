from langgraph.graph import END,START,StateGraph

from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from custom.prompt.prompt_chat import (chat_msg_1,chat_prompt_1,
                                         chat_msg_2,chat_prompt_2,
                                         chat_msg_3,chat_prompt_3,
                                         chat_msg_4,chat_prompt_4)
from custom.db.chrom_vector import chromVector
from custom.plugin.plugin_chat.plugin_get_now import GetNow
from custom.plugin.plugin_chat.plugin_get_weather import GetWeather

from common.utils import show_lg,show_db
from common.llm_utils import str2dict,duplicate_removal
from common.utils import dictDotNotation
from datetime import datetime


class AnalysisQuery(PluginBase):
    def process(self,state):
        # show_db("AnalysisQuery")
        llm =  model_base().init_tongy()["chat"]
        query = state.parameters["query"]
        chat_prompt_1.set_system_msg(chat_msg_1)
        chat_prompt_1.set_human_msg(query)
        msg = chat_prompt_1.get_messages()
        state.user_input = msg        
        
        res_dct = dict()
        for k,v in list(res.items()):
            if v != "":
                res_dct[k] = v
        state.parameters.update(res_dct)
        # show_db(f"> {state}")
        return state
    
    
    
class ChooseRAG(PluginBase):
    def process(self,state:MainGraphState):
        # show_db(f">>> ChooseRAG  ")
        query = state.parameters["des"]
        crop = state.parameters["crop"]
        # print(">>   ",query,crop,rag_db)
        rag_info = rag_db[crop].similarity_search(query,k=3)
        state.parameters.update({'rag_info': rag_info})
        return state
    

class Chatsummarize(PluginBase):
    def process(self,state):
        # show_db(f">>> Chatsummarize")
        llm =  model_base().init_tongy()["chat"]
        # state.messages = duplicate_removal(state.messages)
        if len(state.messages) > 4:
            history_msg = state.messages
            # show_db(f"history   {history_msg}")
            chat_prompt_3.set_system_msg(chat_msg_3)
            chat_prompt_3.set_human_msg(f'{history_msg}')
            msg = chat_prompt_3.get_messages()
            res = llm.invoke(msg).content
            state.summarize += res
            state.messages = []
        return state
    

class AnalysisResults(PluginBase):
    def process(self,state:MainGraphState):
        # show_db(f">>> AnalysisResults ")
        b = state.parameters.get("rag_info","")
        if not b:
            rag_info=""
        else:
            rag_info = state.parameters["rag_info"]
        # show_db(f">r> {state.messages}")
        # show_db(f">s> {state.summarize}")
       
        tm = datetime.now().strftime("%Y年%m月%d日 %H时%M分%S秒")
   
        chat_prompt_2.set_system_msg(chat_msg_2.format(rag_info,state.messages,state.summarize))
        state.parameters["rag_info"] = ""
        query = state.parameters["query"]
        llm = model_base().init_tongy()["chat"]
        chat_prompt_2.set_human_msg(f"当前时间为{tm}，用户输入信息为：{query}")
        msg = chat_prompt_2.get_messages()
        res = llm.invoke(msg).content
        
        state.messages += [{'human':query,'ai':res}]
        state.latest_response = res
        show_db(res)
        return state
    
def routing(state):
    # show_db(">> routing")
    # show_db(f">>>   {state}")
    chat_prompt_4.set_system_msg(chat_msg_4)
    chat_prompt_4.set_human_msg(state.parameters["des"])
    msg = chat_prompt_4.get_messages()
    llm =  model_base().init_tongy()["chat"]
    res = llm.invoke(msg).content
    # show_db(f">> {res}")>>
    if res=="ny":
        b = state.parameters.get("crop","")
        if b:
            return 'rag_db'
        else:
            return "history"
    elif res == "time":
        return "time"
    else:
        return "weather"

class chat_once(SubGraphBase):
    def setattr(self):
        self.nodes = {
                      "AnalysisQuery":AnalysisQuery().handler,
                      "ChooseRAG":ChooseRAG().handler,
                       "AnalysisResults":AnalysisResults().handler,
                       "Chatsummarize":Chatsummarize().handler,
                       "GetNow":GetNow().handler,
                       "GetWeather":GetWeather().handler,
                      }
        self.config = UserThreadId("ny_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        builder.recursion_limit =100
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,{'rag_db':"ChooseRAG",
                                                                 "history":"AnalysisResults",
                                                                 "time":"GetNow",
                                                                 "weather":"GetWeather",
                                                                 "other":"AnalysisResults"})
        builder.add_edge("ChooseRAG","AnalysisResults")
        builder.add_edge("GetNow","AnalysisResults")
        builder.add_edge("GetWeather","AnalysisResults")
        builder.add_edge("AnalysisResults","Chatsummarize")
        builder.add_edge("Chatsummarize",END)
        self.app = builder.compile(checkpointer=self.ckp)
    def invoke(self,state:MainGraphState):
        for event in self.app.stream(state, self.config, stream_mode="values"):
            ...
            # print(event)
        return state
        
class chat(PluginBase):
    def process(self,state):
        bot =chat_once()
        while True:
            state = bot.invoke(state)
            query = input("human: ")
            if query == "q":
                break
            state = MainGraphState(
                user_input=[],
                parameters={"query":query}
            )
        return state     


    
