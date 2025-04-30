from langgraph.graph import END,START,StateGraph

from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from custom.plugin.plugin_hello_world import HelloWorld


class helloLLM_workflow(SubGraphBase):
    def setattr(self):
        self.nodes = {"hello":HelloWorld().handler}
        self.config = UserThreadId("hello_1")
        self.ckp = CheckpointMemory()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
        builder.add_edge(START,"hello")
        builder.add_edge("hello",END)
        self.app = builder.compile(checkpointer=self.ckp)

