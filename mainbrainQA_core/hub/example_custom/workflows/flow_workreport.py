from langgraph.graph import END,START,StateGraph
from core.plugin_base import PluginBase
from core.state_base import MainGraphState
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from custom.plugin.plugin_workreport import anasys_workreport,edit_xlsx,reporting,AnalysisQuery,routing

        
class workreport_once(SubGraphBase):
    def setattr(self):
        # show_lg("start runing xlxs workflow")
        self.nodes = {"anasys": anasys_workreport().invoke,
                      "edit_xlsx":edit_xlsx().invoke,
                      "reporting":reporting().invoke,
                      "AnalysisQuery":AnalysisQuery().handler,
                      }

        self.config = UserThreadId("hello_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,{"anasys":"anasys","edit_xlsx":"edit_xlsx","reporting":"reporting"})
        builder.add_edge("anasys",END)
        builder.add_edge("edit_xlsx",END)
        builder.add_edge("reporting",END)
        self.app = builder.compile(checkpointer=self.ckp)
        
        
        
class workreport_workflow(PluginBase):
    def process(self,state):
        bot = workreport_once()
        while True:
            state = bot.invoke(state)
            query = input("human: ")
            if query == "q":
                break
           
            state = MainGraphState(
                user_input=[],
                parameters={"query":query}
            )
        return state


# class workreport_workflow(SubGraphBase):
#     def setattr(self):
#         # show_lg("start runing xlxs workflow")
#         self.nodes = {"workreport": anasys_workreport().invoke,
#                       "edit_xlsx":edit_xlsx().invoke,
#                       "reporting":reporting().invoke,
#                       "AnalysisQuery":AnalysisQuery().handler,
#                       }

#         self.config = UserThreadId("hello_1")
#         self.ckp = CheckpointMemory()
#     def __call__(self, builder:StateGraph):
#         for k,v in list(self.nodes.items()):
#             builder.add_node(k,v)
            
#         builder.add_edge(START,"AnalysisQuery")
#         builder.add_conditional_edges("AnalysisQuery",routing,{"workreport":"workreport","edit_xlsx":"edit_xlsx","reporting":"reporting"})
#         builder.add_edge("workreport",END)
#         builder.add_edge("edit_xlsx",END)
#         builder.add_edge("reporting",END)
#         self.app = builder.compile(checkpointer=self.ckp)

