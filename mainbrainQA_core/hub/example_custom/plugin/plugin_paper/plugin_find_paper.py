import pandas as pd
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_paper.prompt_find_paper import find_prompt_1,find_msg_1,find_prompt_2,find_msg_2
from common.utils import show_lg,show_db
from common.llm_utils import str2dict
import requests
from bs4 import BeautifulSoup
from typing import List
import re
import os
from openpyxl import Workbook, load_workbook
from copy import deepcopy
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from langgraph.graph import END,START,StateGraph
import tqdm


path = r"data/papers.xlsx"
sheet_name_arxiv = "arxiv_paper"
sheet_name_bdxs = "bdxs_paper"

class AnalysisQuery(PluginBase):
    def process(self,state):
        # show_db("AnalysisQuery")
        llm =  model_base().init_tongy()["chat"]
        query = state.parameters["query"]
        find_prompt_1.set_system_msg(find_msg_1)
        find_prompt_1.set_human_msg(query)
        msg = find_prompt_1.get_messages()
        res = llm.invoke(msg).content
        res = str2dict(res)
        state.parameters.update(res)
        return state


    
    
class FindPaper(PluginBase):
    def process(self,state):
        # show_db("FindPaper")
        exist_dfs = pd.read_excel(path,sheet_name=sheet_name_arxiv)
        exist_dfs = exist_dfs.to_dict(orient='records')
        
        wks = set(state.parameters["key_words_en"]+state.parameters["key_words"])
        wks = ",".join(list(wks))
        llm =  model_base().init_tongy()["chat"]
        find_prompt_2.set_system_msg(find_msg_2)
        papers_lst= []
        show_db(">>👇这里应该做成异步，加快速度<<")
        for df in tqdm.tqdm(exist_dfs):
            find_prompt_2.set_human_msg(f"关键字：{wks}，摘要：{df['abstract']}")
            msg = find_prompt_2.get_messages()
            res = llm.invoke(msg).content

            if int(res)>0:
                papers_lst += [df]
        state.messages += papers_lst
        return state
        

            
class  AnalysisResults(PluginBase):
    def process(self,state):
        # show_db("AnalysisResults")
        for i,paper_info in  enumerate(state.messages):
            show_db(f"{i+1}   {paper_info}")
        # show_db("done")
        return state
        

class isContinue(PluginBase):
    def process(self,state):
        query = input("human: ")
        if query.lower() == "q":
            state.isLoop = False
        else:
            state.parameters["query"]=query
            state.isLoop = True
        return state
def routing(state):
    b = state.isLoop
    if b:
        return "continue"
    else:
        return "end"
class findpaper_once(SubGraphBase):
    def setattr(self):
        self.nodes = {
                      "FindPaper":FindPaper().handler,
                      "AnalysisQuery":AnalysisQuery().handler,
                      "AnalysisResults":AnalysisResults().handler,
                      "isContinue":isContinue().handler
                      }
        self.config = UserThreadId("arxiv_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_edge("AnalysisQuery","FindPaper")
        builder.add_edge("FindPaper","AnalysisResults") 
        builder.add_edge("AnalysisResults",END)
        self.app = builder.compile(checkpointer=self.ckp)
    def invoke(self,state:MainGraphState):
        for event in self.app.stream(state, self.config, stream_mode="values"):
            ...
        return state
        

