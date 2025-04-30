from langgraph.graph import END,START,StateGraph
# from langgraph.prebuilt import ToolNode,ToolExecutor  # 不好用。复杂输入数据格式可能报错。


from custom.plugin.plugin_novel import summary_novel,cope_novel,AnalysisQuery,routing

from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_community.cache import SQLiteCache

# class summary_workflow(SubGraphBase):
#     def setattr(self):
#         self.nodes = {
#                       "summary_novel":summary_novel().handler,
#                       }
#         self.config = UserThreadId("summary_1")
#         self.ckp = CheckpointMemory()
#     def __call__(self, builder:StateGraph):
#         builder.recursion_limit =100
#         for k,v in list(self.nodes.items()):
#             builder.add_node(k,v)
            
#         builder.add_edge(START,"summary_novel")
#         builder.add_edge("summary_novel",END)
#         self.app = builder.compile(checkpointer=self.ckp)

# class cope_workflow(SubGraphBase):
#     def setattr(self):
#         self.nodes = {
#                       "cope_once":cope_novel().handler,
#                       }
#         self.config = UserThreadId("cope_1")
#         self.ckp = CheckpointMemory()
#     def __call__(self, builder:StateGraph):
#         builder.recursion_limit =100
#         for k,v in list(self.nodes.items()):
#             builder.add_node(k,v)
            
#         builder.add_edge(START,"cope_once")
#         builder.add_edge("cope_once",END)
#         self.app = builder.compile(checkpointer=self.ckp)
        
# class novel_workflow(SubGraphBase):
#     try:
#         set_llm_cache(SQLiteCache(database_path="history/chatny.db"))
#     except:
#         set_llm_cache(InMemoryCache())
#     def setattr(self):
#         self.nodes = {
#                       "AnalysisQuery":AnalysisQuery().handler,
#                       "summary_workflow":summary_workflow().invoke,
#                       "cope_workflow":cope_workflow().invoke,
#                       }
#         self.config = UserThreadId("novel_1")
#         self.ckp = CheckpointMemory()
#     def __call__(self, builder:StateGraph):
#         builder.recursion_limit =100
#         for k,v in list(self.nodes.items()):
#             builder.add_node(k,v)
#         builder.add_edge(START,"AnalysisQuery")
#         builder.add_conditional_edges("AnalysisQuery",routing,["summary_workflow","cope_workflow"])
#         builder.add_edge("summary_workflow",END)
#         builder.add_edge("cope_workflow",END)
#         self.app = builder.compile(checkpointer=self.ckp)


class novel_workflow(SubGraphBase):
    try:
        set_llm_cache(SQLiteCache(database_path="history/chatny.db"))
    except:
        set_llm_cache(InMemoryCache())
    def setattr(self):
        self.nodes = {
                      "AnalysisQuery":AnalysisQuery().handler,
                      "summary_workflow":summary_novel().handler,
                      "cope_workflow":cope_novel().handler,
                      }
        self.config = UserThreadId("novel_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        builder.recursion_limit =100
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,["summary_workflow","cope_workflow"])
        builder.add_edge("summary_workflow",END)
        builder.add_edge("cope_workflow",END)
        self.app = builder.compile(checkpointer=self.ckp)