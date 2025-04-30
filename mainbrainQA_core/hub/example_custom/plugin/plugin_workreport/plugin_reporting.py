
import pandas as pd
from copy import deepcopy
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_workreport.prompt_reporting import reporting_msg_1,reporting_prompt_1,reporting_msg_2,reporting_prompt_2
from common.utils import show_lg,show_db
from common.llm_utils import str2dict
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from langgraph.graph import END,START,StateGraph

from configs.run_mode import test



class AnalysisQuery(PluginBase):
    def process(self,state):
        
        show_db("触发每日检测工作表")
        llm =  model_base().init_tongy()["chat"]
        query = "读取data/workspace_2.xlsx表格"
        show_db(query)
        state.isLoop = True
        reporting_prompt_1.set_system_msg(reporting_msg_1)
        reporting_prompt_1.set_human_msg(query)
        msg = reporting_prompt_1.get_messages()
        state.user_input = msg
        res = llm.invoke(msg).content
        res = str2dict(res)
        state.parameters = deepcopy(res)
        state.user_input=[]
        return state


class ReadExcel(PluginBase):
    def process(self,state:MainGraphState):
        if test:
            show_db(f"ReadExcel")
        df = pd.ExcelFile(state.parameters["path"])
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
        # show_db(f"AnalysisResults>>")
        llm =  model_base().init_tongy()["chat"]
        reporting_prompt_2.set_system_msg(reporting_msg_2)
        query = """
        对表格数据做分析
        表格数据: {}
        """.format(state.parameters['xlsx'])
        reporting_prompt_2.set_human_msg(query)
        msg = reporting_prompt_2.get_messages()
        res = llm.invoke(msg)
        res = res.content
        res = str2dict(res)
        show_db("post信息：")
        show_db(res)
        state.latest_response = str(res)
        return state


class reporting(SubGraphBase):
    def setattr(self):
        self.nodes = {"ReadExcel": ReadExcel().handler,
                      "AnalysisQuery":AnalysisQuery().handler,
                      "AnalysisResults":AnalysisResults().handler}
        self.config = UserThreadId("hello_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_edge("AnalysisQuery","ReadExcel")
        builder.add_edge("ReadExcel","AnalysisResults")
        builder.add_edge("AnalysisResults",END)
        self.app = builder.compile(checkpointer=self.ckp)
        