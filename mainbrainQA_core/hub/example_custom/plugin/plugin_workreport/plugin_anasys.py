import pandas as pd
from copy import deepcopy
from core.state_base import MainGraphState
from langgraph.graph import END,START,StateGraph
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_workreport.prompt_xlxs import xlxs_msg_1,xlxs_prompt_1,xlxs_msg_2,xlxs_prompt_2
from common.utils import show_lg,show_db
from common.llm_utils import str2dict
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
#  表格data/workspace_1.xlsx中，周几有体育课？
# 周三和周四都有体育课。
# 谁请假了
# 一周2节体育课够吗


class AnalysisQuery(PluginBase):
    def process(self,state):
        llm =  model_base().init_tongy()["chat"]
        # show_db(f">anasys>> AnalysisQuery")
        query = state.parameters["query"]# input("human: ")
        state.isLoop = True
        xlxs_prompt_1.set_system_msg(xlxs_msg_1)
        xlxs_prompt_1.set_human_msg(query)
        msg = xlxs_prompt_1.get_messages()
        while True:
            res = llm.invoke(msg).content
            try:
                res = str2dict(res)
                b2 = res.get("des","")
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
                if "q" in query:
                    return 
                    break
                xlxs_prompt_1.set_human_msg(query)
                msg = xlxs_prompt_1.get_messages()
                
        state.parameters.update(res)
        state.user_input=[]
        return state


class ReadExcel(PluginBase):
    def process(self,state:MainGraphState):
        # show_db(f">anasy>ReadExcel>>  ")
        path = "data/workspace_1.xlsx"
        # path = state.parameters["path"]
        df = pd.ExcelFile(path)
        sheet_names = df.sheet_names
        all_sheets_data = {}
        for sheet_name in sheet_names:
            data = pd.read_excel(df, sheet_name=sheet_name)
            data = data.to_dict(orient='records')
            all_sheets_data[sheet_name] = data
        state.parameters.update({'xlsx': all_sheets_data})
        return state

class AnalysisResults(PluginBase):
    def process(self,state):
        # show_db(f">anasy> AnalysisResults>>")
        llm =  model_base().init_tongy()["chat"]
        # show_db(f">state>>  {state}")
        xlxs_prompt_2.set_system_msg(xlxs_msg_2.format(state.parameters['xlsx']))
        xlxs_prompt_2.set_human_msg(state.parameters["des"])
        msg = xlxs_prompt_2.get_messages()
        res = llm.invoke(msg).content
        show_db(f"{res}")
        # show_lg("~~~~~~~~~~~~~~~~~~~~")
        state.latest_response = res
        return state


def routing(state):
    b = state.isLoop
    if b:
        return "ReadExcel"
    else:
        return "AnalysisResults"
    
    
class  anasys_workreport(SubGraphBase):
    def setattr(self):
        show_lg("start runing anasys workflow")
        self.nodes = {
            "AnalysisQuery":AnalysisQuery().handler,
            "ReadExcel": ReadExcel().handler,
            "AnalysisResults":AnalysisResults().handler}
        self.config = UserThreadId("hello_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
        builder.add_edge(START,"AnalysisQuery")
        # builder.add_conditional_edges("AnalysisQuery",routing,["ReadExcel","AnalysisResults",END])
        builder.add_edge("AnalysisQuery","ReadExcel")
        builder.add_edge("ReadExcel","AnalysisResults")
        builder.add_edge("AnalysisResults",END)
        
        self.app = builder.compile(checkpointer=self.ckp)
    def invoke(self,state:MainGraphState):
        # print("123123")
        for event in self.app.stream(state, self.config, stream_mode="values"):
            # print("event>>>   ",event)
            ...
            # state.parameters.update(event)
        return state
          