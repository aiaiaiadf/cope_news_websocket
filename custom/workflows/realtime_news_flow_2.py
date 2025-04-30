from langgraph.graph import END,START,StateGraph
from mainbrainQA_core.core.graph_base import MainGraphBase,UserThreadId,CheckpointMemory
from custom.plugin.plugin_realtime_news_2.plugin_nodes import AnalysisQuery,Cope,AnalysisResults

from mainbrainQA_core.common.utils import show_lg

class realtime_news_flow_2(MainGraphBase):
    def setattr(self):
        # show_lg("start runing nongye workflow")
        self.nodes = {
            # "AnalysisQuery":AnalysisQuery().ahandler,
            # "Cope":Cope().ahandler,
            # "AnalysisResults":AnalysisResults().ahandler,
            "AnalysisQuery":AnalysisQuery().handler,
            "Cope":Cope().handler,
            "AnalysisResults":AnalysisResults().handler
        }
                    
        self.config = UserThreadId("cope_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_edge("AnalysisQuery","Cope")
        builder.add_edge("Cope","AnalysisResults")
        builder.add_edge("AnalysisResults",END)
        self.app = builder.compile(checkpointer=self.ckp)
   
        
        
        
