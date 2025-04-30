import pandas as pd
from copy import deepcopy
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_novel.prompt_main import main_msg,main_prompt
from common.utils import show_lg,show_db
from common.llm_utils import str2dict,duplicate_removal




class AnalysisQuery(PluginBase):
    def process(self,state):
        # show_db("AnalysisQuery")
        # query = state.parameters["query"]
        query = "".join(state.parameters["keyWords"])
        main_prompt.set_system_msg(main_msg)
        main_prompt.set_human_msg(query)
        msg = main_prompt.get_messages()
        llm =  model_base().init_tongy()["chat"] 
        # show_db("main msg>..>  ",msg)
        res = llm.invoke(msg).content
        state.parameters["flag"]=res
        # show_db("main res>..>  ",res)
        return state

    
def routing(state):
    return state.parameters["flag"]
  