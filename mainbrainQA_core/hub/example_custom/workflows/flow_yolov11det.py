from langgraph.graph import END,START,StateGraph
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory

from custom.plugin.plugin_det_image import DetImageResults,AnalysisQuery,AnalysisResults,routing,isContinue
from common.utils import show_lg

class detImage_workflow(SubGraphBase):
    def setattr(self):
        # show_lg("start runing detImage workflow")
        self.nodes = {"DetImage":DetImageResults().handler,
                      "AnalysisQuery":AnalysisQuery().handler,
                      "AnalysisResults":AnalysisResults().handler,
                      "isContinue":isContinue().handler}
        self.config = UserThreadId("hello_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_conditional_edges("AnalysisQuery",routing,{"continue":"DetImage","end":"AnalysisResults"})
        builder.add_edge("DetImage","AnalysisResults")
        builder.add_edge("AnalysisResults","isContinue")
        builder.add_conditional_edges("isContinue",routing,{"continue":"AnalysisQuery","end":END})
        
        
        self.app = builder.compile(checkpointer=self.ckp)
        
        
        




