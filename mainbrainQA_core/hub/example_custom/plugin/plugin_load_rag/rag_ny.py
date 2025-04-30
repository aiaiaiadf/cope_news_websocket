from langgraph.graph import END,START,StateGraph

from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from core.model_base import model_base
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from custom.prompt.prompt_chat import (chat_msg_1,chat_prompt_1,
                                         chat_msg_2,chat_prompt_2,
                                         chat_msg_3,chat_prompt_3,
                                         chat_msg_4,chat_prompt_4)
from custom.db.chrom_vector import chromVector
from custom.plugin.plugin_chat.plugin_get_now import GetNow
from custom.plugin.plugin_chat.plugin_get_weather import GetWeather

from common.utils import show_lg,show_db
from common.llm_utils import str2dict,duplicate_removal
from common.utils import dictDotNotation
from datetime import datetime

params = dict(data = "data/db",
                chunk_sz = 200,
                chunk_op = 40)

db_params = dictDotNotation(params)
corp_map = {
        "大白菜":"dabaicai",
        "大豆":"dadou",
        "红薯":"hongshu",
        "黄瓜":"huanggua",
        "棉花":"mianhua",
        "小麦":"xiaomai",
        "西红柿":"xihongshi",
        "芸豆":"yundou",
        "玉米":"yumi",
        "冬小麦":"WinterWheat"
}



def LoadRAG():
    show_db("load rag...")
    embed =  model_base().init_qfan()["embed"]
    db_store = chromVector(db_params)
    db_store._set_embed(embed)
    rag_db = db_store.loopVectorFromDb()
    return rag_db

rag_db =LoadRAG()


