from langgraph.graph import END,START,StateGraph
from mainbrainQA_core.core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from mainbrainQA_core.core.plugin_base import PluginBase
from mainbrainQA_core.core.state_base import MainGraphState
from mainbrainQA_core.common.utils import writeJson,readJson,show_db,show_lg,readConf,show_er,strptime,show_wn_p,show_db_p,timepstr
from mainbrainQA_core.solutions.load_model.model_ollama import model_ollama


class AnalysisQuery(PluginBase):
    async def aprocess(self,state:MainGraphState):
        wkeys_params = readConf("configs/wkeys.conf")
        state.parameters.update({"wkeys_params":wkeys_params})
        # show_db(state)
        return state
    def process(self,state:MainGraphState):
        # show_db_p("hello AnalysisQuery")        
        wkeys_params = readConf("configs/wkeys.conf")
        state.parameters.update({"wkeys_params":wkeys_params})
        # show_wn_p(f">1>>  {state}")
        return state

    

class Cope(PluginBase):
    def process(self, state:MainGraphState):
        # show_db_p("hello Cope")
        wkeys = state.parameters["wkeys_params"]        
        chat = model_ollama().init_custom_model("configs/ollama_classify.key")["chat"]

        msg = state.user_input
        data_dct = state.parameters["data_dct"]
        # show_wn_p(data_dct)

        if isinstance(data_dct["date"],str):
            data_dct["date"] = data_dct["date"].split("_")[0] +"_"+data_dct["date"].split("_")[-1]
        else:
            data_dct["date"] = timepstr(data_dct["date"])
  
        check_data = msg[1].content
        b0 = True
        tmp_labels = ""
        for wkey in wkeys:
            if wkey in check_data:
                b0 = False
                wkey = "Bitcoin" if wkey  == "比特币" else wkey
                wkey = "ETH" if wkey  == "以太坊" else wkey
                tmp_labels += wkey+" "
        if b0:
            chat.invoke(msg).content
            for i in ['ck','hg','other']:
                if i in tmp_labels:
                    tmp_labels = i
                    tmp_labels.replace("ck","筹款").replace("hg","宏观")
                    break
        tmp_labels = "other" if len(tmp_labels)==0 else tmp_labels
        tmp_labels = tmp_labels.strip()
        out_dct = dict(label=tmp_labels, news=data_dct,next="") 
        state.tmp_value = out_dct
        return state
        


class AnalysisResults(PluginBase):
    async def aprocess(self,state:MainGraphState):
        return state
    def process(self,state:MainGraphState):
        # show_db_p("hello AnalysisResults")
        # show_wn_p(f">3>>  {state}")
        return state