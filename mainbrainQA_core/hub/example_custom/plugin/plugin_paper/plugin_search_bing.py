import pandas as pd
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_paper.prompt_arxiv_paper import arxiv_prompt_1,arxiv_msg_1,arxiv_prompt_2,arxiv_msg_2
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

path = "data/papers.xlsx"
sheet_name = "arxiv_paper"

class AnalysisQuery(PluginBase):
    def process(self,state):
        show_db("AnalysisQuery")
        llm =  model_base().init_tongy()["chat"]
  
        query = state.parameters["query"]
        arxiv_prompt_1.set_system_msg(arxiv_msg_1)
        arxiv_prompt_1.set_human_msg(query)
        msg = arxiv_prompt_1.get_messages()
        res = llm.invoke(msg).content
        res = str2dict(res)
        state.parameters.update(res)
        show_db(f"::  {state}")
        return state


#    
# utils

def get_src(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    src_ = soup.find("div", class_="tptt")
    if src_:
        return src_.get_text(strip=True)
    return ""

def get_abstract_shot(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    abstract_full = soup.find("p", class_="b_lineclamp4")
    if abstract_full:
        return abstract_full.get_text(strip=True)
    return ""
        
def get_ad(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    gg = soup.find("span", class_="b_adSlug b_opttxt b_divdef")
    if gg:
        return True  
    return False


def get_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find("a", target="_blank")
    if title:
        title_text = title.get_text(strip=True)
        return title_text
    return ""
def get_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    ele = soup.find("a", class_="tilk")
    url = ele["href"]
    if url:
        title_text = url['href'] 
        return title_text
    return ""

def search_bing(query: str) -> List[dict]:
    """
    根据用户输入的关键词搜索 Papers with Code 网站
    Args:
        query: 搜索关键词
    Returns:
        包含论文信息的字典列表，每个字典包含标题和链接
    """
    # 构建搜索URL
    base_url = "https://cn.bing.com/search?q={}%20site%3A%20com"
    search_url = base_url.format(query.replace(" ", "+"))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有论文项
    info_items = soup.find_all('li', class_='b_algo')
    # print(type(paper_items))
    results = []
    for info in info_items:
        # print(">>> paper",str(paper))
        info = str(info)
        if info is None:
            continue
        title = get_title(info)
        url = get_url(info)
        src_ = get_src(info)
        abstract = get_abstract_shot(info)
        ad = get_ad(info)
        if not ad:
            results.append({
                "title": title,
                "url": url,
                "from":src_,
                "abstract":abstract
            })
    return results
 

class SearchBing(PluginBase):
    def process(self,state):
        show_db("SearchPaperFromArxiv")
        key_words = state.parameters["key_words"]
        query = " ".join(key_words)
        query = query.replace("arxiv","")
        papers = search_bing(query)
        assert len(papers)!=0,"papers is none"
        if len(papers)==0 or papers is None:
            raise "papers is none"
        state.parameters.update({'paper_info': papers})
        return state
    
    
# class WriteXlxs(PluginBase):
#     def process(self,state):
#         show_db("WriteXlxs")
#         # show_db(f"1::  {state}")
#         new_df = state.parameters["paper_info"]
#         if not os.path.exists(path):
#             wb = Workbook()
#             wb.save(path)
#             ori_num = 0
#         else:
#             try:
#                 exist_df = pd.read_excel(path,sheet_name)
#             except:
#                 exist_df = pd.read_excel(path)
#             exist_df = exist_df.to_dict(orient='records')
#             ori_num = len(exist_df)
#             conn_df = new_df + exist_df
#             unique_df = []
#             for cdf in conn_df:
#                 if cdf not in unique_df:
#                     unique_df.append(cdf)
#             new_df = unique_df
#         # show_db(f"{len(new_df)}   {ori_num}")
#         ex_num = len(new_df) - ori_num
#         show_db(f"查找到{ex_num}篇新论文,并且保存信息。")
#         df_new = pd.DataFrame(new_df)
        
#         with pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists='overlay')  as writer:
#             df_new.to_excel(writer, sheet_name=sheet_name, index=False)
#         return state
        

            
# class  AnalysisResults(PluginBase):
#     def process(self,state):
#         show_db("AnalysisResults")
#         # show_db(f">> {state}")
#         # show_db("done")
#         return state
        

# class isContinue(PluginBase):
#     def process(self,state):
#         query = input("human: ")
#         if query.lower() == "q":
#             state.isLoop = False
#         else:
#             llm =  model_base().init_tongy()["chat"]
#             arxiv_prompt_2.set_system_msg(arxiv_msg_2)
#             arxiv_prompt_2.set_human_msg(query)
#             msg = arxiv_prompt_2.get_messages()
#             res = llm.invoke(msg).content
#             res = str2dict(res)
#             state.parameters.update(res)
#             state.isLoop = True
#         return state
# def routing(state):
#     b = state.isLoop
#     if b:
#         return "continue"
#     else:
#         return "end"
# class arxiv_once(SubGraphBase):
#     def setattr(self):
#         self.nodes = {"WriteXlxs":WriteXlxs().handler,
#                       "SearchPaperFromArxiv":SearchPaperFromArxiv().handler,
#                       "AnalysisQuery":AnalysisQuery().handler,
#                       "AnalysisResults":AnalysisResults().handler,
#                       "isContinue":isContinue().handler
#                       }
#         self.config = UserThreadId("arxiv_1")
#         self.ckp = CheckpointMemory()
#     def __call__(self, builder:StateGraph):
#         for k,v in list(self.nodes.items()):
#             builder.add_node(k,v)
            
#         builder.add_edge(START,"AnalysisQuery")
#         builder.add_edge("AnalysisQuery","SearchPaperFromArxiv")
#         # builder.add_edge("SearchPaperFromArxiv","WriteXlxs") 
#         # builder.add_edge('WriteXlxs','isContinue')
#         # builder.add_conditional_edges('isContinue',routing,{'continue':'SearchPaperFromArxiv','end':'AnalysisResults'})
#         builder.add_edge("SearchPaperFromArxiv",'isContinue') 
#         builder.add_conditional_edges('isContinue',routing,{'continue':'SearchPaperFromArxiv','end':"WriteXlxs"})
#         builder.add_edge('WriteXlxs',"AnalysisResults")
#         builder.add_edge("AnalysisResults",END)
#         self.app = builder.compile(checkpointer=self.ckp)
        
#     def invoke(self,state:MainGraphState):
#         for event in self.app.stream(state, self.config, stream_mode="values"):
#             ...
#         return state
        

