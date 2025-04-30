from langgraph.graph import END,START,StateGraph
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory

from custom.plugin.plugin_ny import AnalysisQuery,AnalysisTIme,AnalysisResults,Irrigation

from common.utils import show_lg

class ny_workflow(SubGraphBase):
    def setattr(self):
        # show_lg("start runing nongye workflow")
        self.nodes = {"AnalysisTIme": AnalysisTIme().handler,"AnalysisQuery":AnalysisQuery().handler,
                      "AnalysisResults":AnalysisResults().handler,"Irrigation":Irrigation().handler,}
                    #   "Chatbot":Chatbot}
        self.config = UserThreadId("ny_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
            
        builder.add_edge(START,"AnalysisQuery")
        builder.add_edge("AnalysisQuery","AnalysisTIme")
        builder.add_edge("AnalysisTIme","Irrigation")
        builder.add_edge("Irrigation","AnalysisResults")
        builder.add_edge("AnalysisResults",END)
        # builder.add_conditional_edges("AnalysisResults",routing_2,{"continue":"AnalysisQuery","end":END})
        self.app = builder.compile(checkpointer=self.ckp)
        
        
        
