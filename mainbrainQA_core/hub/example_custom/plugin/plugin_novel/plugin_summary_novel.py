import pandas as pd
from copy import deepcopy
try:
    from langchain_community.document_loaders import Docx2txtLoader
except:
    from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langgraph.graph import END,START,StateGraph

from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from custom.prompt.prompt_novel.prompt_summary_novel import (summary_msg_1,summary_prompt_1,
                                             summary_msg_2,summary_prompt_2,
                                             summary_msg_3,summary_prompt_3,
                                             summary_msg_4,summary_prompt_4)
from common.utils import show_lg,show_db
from common.llm_utils import str2dict,duplicate_removal


test = True

class AnalysisQuery(PluginBase):
    def process(self,state):
        if test:
            show_db(">> AnalysisQuery")
        llm =  model_base().init_tongy()["chat"]
        query = state.parameters["query"]
        summary_prompt_1.set_system_msg(summary_msg_1)
        summary_prompt_1.set_human_msg(query)
        msg = summary_prompt_1.get_messages()
        while True:
            res = llm.invoke(msg).content
            try:
                res = str2dict(res)
                b1 = res.get("path","")
                b2 = res.get("des","")
                if b1 and b2:
                    state.isLoop = True
                elif b2 and (not b1):
                    state.isLoop = False
                elif (not b2):
                    raise
                break
            except:
                show_db("没理解你的意思")
                query = input("human: ")
                summary_prompt_1.get_messages(query)
                msg = summary_prompt_1.get_messages()
                
        # state.isLoop = True
        # show_db(f">>  {res}")
        # show_db(f">>>  {state}")
        state.parameters.update(res)
        
        return state

def routing(state):
    b = state.isLoop
    if b:
        return "ReadDocx"
    else:
        return "AnalysisResults"


class ReadDocx(PluginBase):
    def process(self,state):
        if test:
            show_db(">> ReadDocx")
        tmp_lst = list()
        path = state.parameters["path"]
        # show_db(f">1>  {state}")
        loader = Docx2txtLoader(path)
        content = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size =300, chunk_overlap=20, separators=["\n\n", "\n", " ", "", "。", "，", "；"])
        texts = text_splitter.split_documents(content)
        for text in texts:
            tmp_lst.append([text.page_content])
        state.messages += tmp_lst
        # show_db(f">1>>  {state}")
        return state
    
class Summary(PluginBase):
    def process(self,state):
        if test:
            show_db(">> Summary")
        llm =  model_base().init_tongy()["chat"]
        summary_prompt_2.set_system_msg(summary_msg_2)
        
        summary_ = ""
        for text in state.messages:
            if text == "":
                continue
            summary_prompt_2.set_human_msg(text[0])
            msg = summary_prompt_2.get_messages()
            res = llm.invoke(msg).content
            summary_ += res
            
        summary_prompt_3.set_system_msg(summary_msg_3)
        summary_prompt_3.set_human_msg(summary_)
        msg = summary_prompt_3.get_messages()
        llm =  model_base().init_tongy()["chat"]
        res = llm.invoke(msg).content
        
        state.messages +=[res]
        return state


class AnalysisResults(PluginBase):
    def process(self,state):
        if test:
       
            show_db(">> AnalysisResults")
        llm =  model_base().init_tongy()["chat"]
        summary_prompt_4.set_system_msg(summary_msg_4.format(state.messages[-1]))
        
        summary_prompt_4.set_human_msg(state.parameters["des"])
        msg = summary_prompt_4.get_messages()
        
        res = llm.invoke(msg).content
        show_db(res)
        state.latest_response = res
        return state




class summary_once(SubGraphBase):
    def setattr(self):
        self.nodes = {
                      "AnalysisQuery":AnalysisQuery().handler,
                      "ReadDocx":ReadDocx().handler,
                     "Summary":Summary().handler,
                     "AnalysisResults":AnalysisResults().handler,
                      }
        self.config = UserThreadId("summary_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        builder.recursion_limit =100
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,{"ReadDocx":"ReadDocx","AnalysisResults":"AnalysisResults"})

        builder.add_edge("ReadDocx","Summary")
        builder.add_edge("Summary","AnalysisResults")
        builder.add_edge("AnalysisResults",END)
        
       
        self.app = builder.compile(checkpointer=self.ckp)
    def invoke(self,state:MainGraphState):
        for event in self.app.stream(state, self.config, stream_mode="values"):
            ...
        return state
        

class summary_novel(PluginBase):
    def process(self,state):
        bot =summary_once()
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


    