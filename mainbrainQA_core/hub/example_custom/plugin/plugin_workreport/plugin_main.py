import pandas as pd
from copy import deepcopy
from core.plugin_base import PluginBase
from core.model_base import model_base
from custom.prompt.prompt_workreport.prompt_main import main_msg,main_prompt


class AnalysisQuery(PluginBase):
    def process(self,state):
        query = state.parameters["query"]
        main_prompt.set_system_msg(main_msg)
        main_prompt.set_human_msg(query)
        msg = main_prompt.get_messages()
        llm =  model_base().init_tongy()["chat"] 
        res = llm.invoke(msg).content
        tmp_dct = {"flag":res}
        tmp_dct.update(state.parameters)
        state.parameters = deepcopy(tmp_dct)
        return state

    
def routing(state):
    return state.parameters["flag"]
  