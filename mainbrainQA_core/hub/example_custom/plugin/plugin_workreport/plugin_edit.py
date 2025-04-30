from core.plugin_base import PluginBase
from custom.prompt.prompt_workreport.prompt_workreport import workreport_msg_1,workreport_prompt_1,workreport_msg_2,workreport_prompt_2
from core.model_base import model_base
from common.llm_utils import str2dict
from langgraph.graph import END,START,StateGraph
from common.utils import show_lg,show_db
from copy import deepcopy
import pandas as pd
from datetime import datetime
# 更新工作表格
# 取出齿轮AF36商品，10个
# 入仓齿轮EF31商品，10个
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from core.state_base import MainGraphState
path = r"data/workspace_3.xlsx"
sheet_name = "仓库存档"


test = False

def getnow():
    tm = datetime.now()
    timestamp = pd.Timestamp(tm)
    formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_timestamp


class ReadExcel(PluginBase):
    def process(self,state):
        if test:
            show_db(f"ReadExcel>>  ")
        df = pd.ExcelFile(path)
        data = pd.read_excel(df, sheet_name=sheet_name)
        state.parameters.update({'df':data.to_dict(orient='records')})
        return state


class AnalysisQuery(PluginBase):
    def process(self,state):
        if test:
            show_db(">> AnalysisQuery")
        llm =  model_base().init_tongy()["chat"]
        query = state.parameters["query"]
        workreport_prompt_1.set_system_msg(workreport_msg_1)
        workreport_prompt_1.set_human_msg(query)
        msg = workreport_prompt_1.get_messages()
        while True:
            res = llm.invoke(msg).content
            try:
                res = str2dict(res)
                break
            except:
                show_db("没理解你的意思")
                query = input("human: ")
                workreport_prompt_1.set_human_msg(query)
                msg = workreport_prompt_1.get_messages()
                
        state.parameters.update(res)
        return state
    


class chuCang(PluginBase):
    def process(self,state):
        if test:
            show_db(f"chuCang>>  ")
        value_to_find = state.parameters["name"]
        num = int(state.parameters["num"])
        df = pd.DataFrame(state.parameters['df'])

        filtered_rows = df[df.iloc[:, 0] == value_to_find]
        filtered_rows = filtered_rows.to_dict(orient='records')
        if len(filtered_rows)!=0:
            a0 = filtered_rows[0]
            a1 = int(a0['存仓数量'])-num 
            if a1<0:
                show_db(f"{value_to_find}只能出仓{a0['存仓数量']},库存为0")
                a1 = 0
            else:
                show_db(f"{value_to_find}出仓{num},库存为{a1}")
                
            a0.update({'出仓数量':num,'出仓时间':getnow(),'存仓数量':a1})
            # filtered_rows.
            a0 = pd.DataFrame([a0])
            first_column = df.iloc[:, 0]
            a= a0.iloc[:,0]
            mask = first_column.isin(a)
            clo_num = df[mask].index.tolist()[0]
            
            df = df.drop(index=clo_num)
            df = pd.concat([df.iloc[:clo_num], a0, df.iloc[clo_num:]]).reset_index(drop=True)
            
            state.parameters.update({'df':df.to_dict(orient='records'),'out':f"{value_to_find}的存仓数量为{a1}"})
        else:
            out = f"未查到这个商品{value_to_find}"
            show_db(out)
         
        return state
    
class ruCang(PluginBase):
    def process(self,state):
        if test:
            show_db(f"ruCangl>>  ")
        value_to_find = state.parameters["name"]
        num = int(state.parameters["num"])
        df = pd.DataFrame(state.parameters['df'])
     
        filtered_rows = df[df.iloc[:, 0] == value_to_find]
        filtered_rows = filtered_rows.to_dict(orient='records')

        if len(filtered_rows)!=0:
            a0 = filtered_rows[0]
            a1 = int(a0["存仓数量"])+num
            show_db(f"{value_to_find}入仓{num},库存为{a1}")
            a0.update({"入仓数量":num,"入仓时间":getnow(),"存仓数量":a1})
            a0 = pd.DataFrame([a0])
            first_column = df.iloc[:, 0]
            a= a0.iloc[:,0]
            mask = first_column.isin(a)
            clo_num = df[mask].index.tolist()[0]
            df = df.drop(index=clo_num)
            df = pd.concat([df.iloc[:clo_num], a0, df.iloc[clo_num:]]).reset_index(drop=True)
        else:
            a0 = {'商品名字': value_to_find, '入仓时间': '2000-01-01 01:01:01', '入仓数量': '0', '出仓时间': '1900-01-01 01:01:01', '出仓数量': '0', '存仓数量': '0', '参数': None}
            a1 = int(a0["存仓数量"])+num
            show_db(f"{value_to_find}入仓{num},库存为{a1}")
            a0.update({"入仓数量":num,"入仓时间":getnow(),"存仓数量":a1})
            a0 = pd.DataFrame([a0])
            df = pd.concat([df.iloc[:], a0]).reset_index(drop=True)
        state.parameters.update({'df':df.to_dict(orient='records'),'out':f"{value_to_find}的存仓数量为{a1}"})
   
        return state
    


class AnalysisResults(PluginBase):
    def process(self,state):
        if test:
            show_db(">> AnalysisResults") 
        llm =  model_base().init_tongy()["chat"]
        try:
            out = state.parameters["out"]
            workreport_prompt_2.set_system_msg(workreport_msg_2)
            workreport_prompt_2.set_human_msg(out)
            msg = workreport_prompt_2.get_messages()
            res = llm.invoke(msg).content
            state.latest_response = res
            state.isLoop = True
        except:
            state.isLoop = False

        return state
class WriteExcel(PluginBase):
    def process(self,state):
        if test:
            show_db(f"WriteExcel>>  ")
        
        df = pd.DataFrame(state.parameters["df"])
        df.to_excel(path, index=False,sheet_name=sheet_name)
        show_db("写入数据成功")
        return state


class isContinue(PluginBase):
    def process(self,state):
        if test:
            show_db(f"iscontinue>> ")
        query = input("human: ")
        if query.lower() == "q":
            state.isLoop = False
        else:
            state.parameters['des']=query
            workreport_prompt_1.set_system_msg(workreport_msg_1)
            workreport_prompt_1.set_human_msg(query)
            msg = workreport_prompt_1.get_messages()
            state.user_input = msg
            state.isLoop = True
        return state
    

def routing(state):
    b = state.isLoop
    if b:
        return 'write'
    else:
        return "end"
    
def choose(state):
    return state.parameters["flag"]




class edit_xlsx(SubGraphBase):
    def setattr(self):
        # show_lg("start runing xlxs workflow")
        self.nodes = {"ReadExcel": ReadExcel().handler,
                      "WriteExcel":WriteExcel().handler,
                      "AnalysisQuery":AnalysisQuery().handler,
                      "AnalysisResults":AnalysisResults().handler,
                      "isContinue":isContinue().handler,
                      "chuCang":chuCang().handler,
                      "ruCang":ruCang().handler}

        self.config = UserThreadId("edit_xlsx_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"ReadExcel")
        builder.add_edge("ReadExcel","AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",choose,{'tianjia':"ruCang",'quchu':"chuCang"})
        builder.add_edge("ruCang","AnalysisResults")
        builder.add_edge("chuCang","AnalysisResults")
        builder.add_conditional_edges("AnalysisResults",routing,{"write":"WriteExcel","end":END})
        builder.add_edge("WriteExcel",END)
        self.app = builder.compile(checkpointer=self.ckp)



# class workreport_once(SubGraphBase):
#     def setattr(self):
#         # show_lg("start runing xlxs workflow")
#         self.nodes = {"ReadExcel": ReadExcel().handler,
#                       "WriteExcel":WriteExcel().handler,
#                       "AnalysisQuery":AnalysisQuery().handler,
#                       "AnalysisResults":AnalysisResults().handler,
#                       "isContinue":isContinue().handler,
#                       "chuCang":chuCang().handler,
#                       "ruCang":ruCang().handler}

#         self.config = UserThreadId("hello_1")
#         self.ckp = CheckpointMemory()
#     def __call__(self, builder:StateGraph):
#         for k,v in list(self.nodes.items()):
#             builder.add_node(k,v)
            
#         builder.add_edge(START,"ReadExcel")
#         # builder.add_conditional_edges("AnalysisQuery",routing,{"continue":"ReadExcel","end":'AnalysisResults'})
#         builder.add_edge("ReadExcel","AnalysisQuery")
#         builder.add_conditional_edges("AnalysisQuery",choose,{'tianjia':"ruCang",'quchu':"chuCang"})
#         builder.add_edge("ruCang","AnalysisResults")
#         builder.add_edge("chuCang","AnalysisResults")
#         builder.add_edge("AnalysisResults","WriteExcel")
#         builder.add_edge("WriteExcel",END)
#         self.app = builder.compile(checkpointer=self.ckp)
        
        
# class workreport(PluginBase):
#     def process(self,state):
#         bot =workreport_once()
#         while True:
#             state = bot.invoke(state)
#             query = state.parameters["query"]
#             query = input("human: ")
#             if query == "q":
#                 break
#             state = MainGraphState(
#                 user_input=[],
#                 parameters={"query":query}
#             )
#         return state        


    