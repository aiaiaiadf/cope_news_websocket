from core.model_base import model_base
from core.plugin_base import PluginBase
from common.utils import show_db
from common.thirdparty import get_weather
from custom.prompt.prompt_weather import weather_prompt,weather_msg 


class GetWeather(PluginBase):
    def process(self,state):
        query = state.parameters["query"]
        llm =  model_base().init_tongy()["chat"]
        weather_prompt.set_system_msg(weather_msg)
        weather_prompt.set_human_msg(query)
        msg = weather_prompt.get_messages()
        address = llm.invoke(msg).content
        try:
            res = get_weather(address)
        except:
            res = f"{address} 不在查询范围"
        # show_db(res)
        state.messages += [{'human':query,'ai':res}]
        return state
 


