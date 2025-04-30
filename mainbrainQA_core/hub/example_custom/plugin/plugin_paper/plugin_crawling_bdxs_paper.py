import pandas as pd
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_paper.prompt_bdxs_paper import bdxs_prompt_1,bdxs_msg_1,bdxs_prompt_2,bdxs_msg_2,bdxs_prompt_3,bdxs_msg_3
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
from urllib.parse import unquote,quote
import time

path = "data/papers.xlsx"
sheet_name = "baiduxueshu_paper"


class AnalysisQuery(PluginBase):
    def process(self,state):
        show_db("AnalysisQuery")
        llm =  model_base().init_tongy()["chat"]
  
        query = state.parameters["query"]
        bdxs_prompt_1.set_system_msg(bdxs_msg_1)
        bdxs_prompt_1.set_human_msg(query)
        msg = bdxs_prompt_1.get_messages()
        res = llm.invoke(msg).content
        res = str2dict(res)
        # b1 = res.get("path","")
        # if not b1:
        #     state.isLoop = True
        # else:
        #     state.isLoop = False
        state.parameters.update(res)
        show_db(f"::  {state}")
        return state


#    
# utils

def encode_str(query:str):
    query = quote(query)
    return query 

def get_abstract_shot(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    url = soup.find("h3",class_="t c_font")
    url = url.find('a')['href']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    abstract = soup.find("p",class_="abstract")
    if abstract:
        return abstract.get_text(strip=True)
    else:
        return ""
def get_time(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tm = soup.find('span', class_='sc_time')
    if tm:
        return tm.get_text(strip=True)
    return ""


def get_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find("h3",class_="t c_font")
    if title:
        title_text = title.get_text(strip=True)
        return title_text
    return ""

def get_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # 获取 class="title is-5 mathjax" 的内容
    url = soup.find("div",class_="result sc_default_result xpath-log")["mu"]
    if url:
        # 提取文本并去除多余的空白
        title_text = url# .get_text(strip=True)
        return title_text
    return ""

def search_papers(query: str,max_page:int=1) -> List[dict]:
    """
    根据用户输入的关键词搜索 Papers with Code 网站
    Args:
        query: 搜索关键词
    Returns:
        包含论文信息的字典列表，每个字典包含标题和链接
    """
    # 构建搜索URL
    base_url = "https://xueshu.baidu.com/s?wd={}&pn={}&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&sc_hit=1"
    query = encode_str(query.replace(" ", "+"))
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # }
    # headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    results = []
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "Referer": "https://xueshu.baidu.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
    for i in range(max_page):
        
        time.sleep(0.5)
        search_url = base_url.format(query,str(i*10))
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到所有论文项
        # paper_items = soup.find_all("div",class_="result sc_default_result xpath-log")#class_='arxiv-result')
        paper_items = soup.find_all("div",class_='result sc_default_result xpath-log')
        for paper in paper_items:
            # print(">>> paper",str(paper))
            paper = str(paper)
            if paper is None:
                continue
            title = get_title(paper)
            url = get_url(paper)
            time_ = get_time(paper)
            abstract = get_abstract_shot(paper)
            results.append({
                "title": title,
                "url": url,
                "authors":"",
                "date":time_,
                "abstract":abstract
            })
            print(results)
        
    return results   
  
 

class SearchPaperFromBDXS(PluginBase):
    def process(self,state):
        show_db("SearchPaperFromBDXS")
        key_words_cn = state.parameters["key_words"]
        key_words_zn = state.parameters["key_words_en"]
        key_words = [key_words_cn,key_words_zn]
        papers_lst = []
        
        llm =  model_base().init_tongy()["chat"]
        bdxs_prompt_2.set_system_msg(bdxs_msg_2)
        
        for kw in key_words:
            query = " ".join(kw)
            papers = search_papers(query)
            
            for paper in papers:
                bdxs_prompt_2.set_human_msg(f"关键字为：{query},论文摘要{paper['abstract']}")
                msg = bdxs_prompt_2.get_messages()
                res = llm.invoke(msg).content
                if res:
                    papers_lst.append(paper)

            papers_lst += papers
        state.parameters.update({'paper_info': papers_lst})
        return state
    
    
class WriteXlxs(PluginBase):
    def process(self,state):
        show_db("WriteXlxs")
        # show_db(f"1::  {state}")
       
        new_df = state.parameters["paper_info"]
        if not os.path.exists(path):
            wb = Workbook()
            wb.save(path)
            ori_num = 0
        else:
            try:
                exist_df = pd.read_excel(path,sheet_name)
            except:
                exist_df = pd.read_excel(path)
            exist_df = exist_df.to_dict(orient='records')
            ori_num = len(exist_df)
            conn_df = new_df + exist_df
            unique_df = []
            for cdf in conn_df:
                if cdf not in unique_df:
                    unique_df.append(cdf)
            new_df = unique_df
        # show_db(f"{len(new_df)}   {ori_num}")
        ex_num = len(new_df) - ori_num
        show_db(f"查找到{ex_num}篇新论文,并且保存信息。")
        df_new = pd.DataFrame(new_df)
        
        with pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists='overlay')  as writer:
            df_new.to_excel(writer, sheet_name=sheet_name, index=False)
        return state
        

            
class  AnalysisResults(PluginBase):
    def process(self,state):
        show_db("AnalysisResults")
        # show_db(f">> {state}")
        show_db("done")
        return state
        

class isContinue(PluginBase):
    def process(self,state):
        query = input("human: ")
        if query.lower() == "q":
            state.isLoop = False
        else:
            llm =  model_base().init_tongy()["chat"]
            bdxs_prompt_3.set_system_msg(bdxs_msg_3)
            bdxs_prompt_3.set_human_msg(query)
            msg = bdxs_prompt_3.get_messages()
            res = llm.invoke(msg).content
            res = str2dict(res)
            state.parameters.update(res)
            state.isLoop = True
        return state
def routing(state):
    b = state.isLoop
    if b:
        return "continue"
    else:
        return "end"
class bdxs_once(SubGraphBase):
    def setattr(self):
        self.nodes = {"WriteXlxs":WriteXlxs().handler,
                      "SearchPaperFromBDXS":SearchPaperFromBDXS().handler,
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
        builder.add_edge("AnalysisQuery","SearchPaperFromBDXS")
        # builder.add_edge("SearchPaperFromArxiv","WriteXlxs") 
        # builder.add_edge('WriteXlxs','isContinue')
        # builder.add_conditional_edges('isContinue',routing,{'continue':'SearchPaperFromArxiv','end':'AnalysisResults'})
        builder.add_edge("SearchPaperFromBDXS",'isContinue') 
        builder.add_conditional_edges('isContinue',routing,{'continue':'SearchPaperFromBDXS','end':"WriteXlxs"})
        builder.add_edge('WriteXlxs',"AnalysisResults")
        builder.add_edge("AnalysisResults",END)
        self.app = builder.compile(checkpointer=self.ckp)
        
    def invoke(self,state:MainGraphState):
        for event in self.app.stream(state, self.config, stream_mode="values"):
            ...
        return state
        

