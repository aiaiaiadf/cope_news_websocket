import pandas as pd
from copy import deepcopy
from core.plugin_base import PluginBase
from core.model_base import model_base
from common.utils import show_db

from custom.prompt.prompt_paper.prompt_main import main_msg,main_prompt


class AnalysisQuery(PluginBase):
    def process(self,state):
        # show_db("AnalysisQuery")
        # show_db(f" >< {state}")
        query = state.parameters["query"]
        main_prompt.set_system_msg(main_msg)
        main_prompt.set_human_msg(query)
        msg = main_prompt.get_messages()
        llm =  model_base().init_tongy()["chat"] 
        res = llm.invoke(msg).content
        # show_db(f">--> {res}")
        tmp_dct = {"flag":res}
        tmp_dct.update(state.parameters)
        state.parameters = deepcopy(tmp_dct)

        return state

    
def routing(state):
    # show_db(f"routing > {state.parameters['flag']}")
    return state.parameters["flag"]
  