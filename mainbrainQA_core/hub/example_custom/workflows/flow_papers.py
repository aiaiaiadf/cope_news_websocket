from langgraph.graph import END,START,StateGraph
from core.plugin_base import PluginBase
from core.state_base import MainGraphState
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from custom.plugin.plugin_paper import arxiv_once,bdxs_once,findpaper_once,AnalysisQuery,routing
from common.utils import show_db
from copy import deepcopy


class arxiv_workflow(PluginBase):
    def process(self,state):
        # bot =arxiv_once()
        # query = state.parameters["query"]
        # state.parameters = deepcopy({"query":query})
        # while True:
        #     state = bot.invoke(state)
        #     query = input("human: ")
        #     if query == "q":
        #         break
        #     state.parameters.update({"query":query})
        #     show_db(f">>><> {state}")
            
        # return state      
        bot =arxiv_once()
        query = state.parameters["query"]
        state.parameters = deepcopy({"query":query})
        state = bot.invoke(state)
           
        return state 
class bdxs_workflow(PluginBase):
    def process(self,state):
        bot =bdxs_once()
        query = state.parameters["query"]
        state.parameters = deepcopy({"query":query})
        state = bot.invoke(state)
        return state   
        # bot =bdxs_once()
        # query = state.parameters["query"]
        # state.parameters = deepcopy({"query":query})
        # while True:
        #     state = bot.invoke(state)
        #     query = input("human: ")
        #     if query == "q":
        #         break
        #     state.parameters.update({"query":query})
        #     show_db(f">>><> {state}")
            
        # return state      
    
class findpaper_workflow(PluginBase):
    def process(self,state):
        # bot = findpaper_once()
        # query = state.parameters["query"]
        # state.parameters = deepcopy({"query":query})
        # while True:
        #     state = bot.invoke(state)
        #     query = input("human: ")
        #     if query == "q":
        #         break
        #     state.parameters.update({"query":query})
        #     show_db(f">>><> {state}")
            
        # return state  
        bot = findpaper_once()
        query = state.parameters["query"]
        state.parameters = deepcopy({"query":query})
        state = bot.invoke(state)    
        return state  
class papers_flow(SubGraphBase):
    def setattr(self):
        # show_lg("start runing xlxs workflow")
        self.nodes = {"arxiv": arxiv_workflow().handler,
                      "bdxs":bdxs_workflow().handler,
                      "find":findpaper_workflow().handler,
                      "AnalysisQuery":AnalysisQuery().handler,
                      }

        self.config = UserThreadId("paper_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,{"find_wf":"find","arxiv_wf":"arxiv","bdxs_wf":"bdxs"})
        builder.add_edge("find",END)
        builder.add_edge("arxiv",END)
        builder.add_edge("bdxs",END)
        self.app = builder.compile(checkpointer=self.ckp)