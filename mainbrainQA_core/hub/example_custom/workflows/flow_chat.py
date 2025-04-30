from langgraph.graph import END,START,StateGraph
# from langgraph.prebuilt import ToolNode,ToolExecutor  # 不好用。复杂输入数据格式可能报错。
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_community.cache import SQLiteCache

from custom.plugin.plugin_chat.plugin_chat import chat
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory


class chat_workflow(SubGraphBase):
    try:
        set_llm_cache(SQLiteCache(database_path="history/chat.db"))
    except:
        set_llm_cache(InMemoryCache())
    def setattr(self):
        self.nodes = {
                      "chat":chat().handler,
                      }
        self.config = UserThreadId("ny_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"chat")
        builder.add_edge("chat",END)
        self.app = builder.compile(checkpointer=self.ckp)
        
        
        
