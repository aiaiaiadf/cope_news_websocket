import platform
from typing import TypedDict
# from langchain_deepseek import ChatDeepSeek
# from langgraph.graph import StateGraph
from core.state_base import MainGraphState
from core.plugin_base import PluginBase
from custom.prompt.prompt_joke_peom.prom_ import  joke_msg,joke_prompt,peom_msg,peom_prompt
from core.graph_base import MainGraphBase

import asyncio

from langchain_ollama.chat_models import ChatOllama
from core.graph_base import SubGraphBase,UserThreadId,CheckpointMemory
from langgraph.graph import END,START,StateGraph

joke_model = ChatOllama(base_url="http://0.0.0.0:11434",model="qwen2.5:1.5b")
poem_model = ChatOllama(base_url="http://0.0.0.0:11434",model="qwen2.5:1.5b")



class generate_joke(PluginBase):
    async def aprocess(self,state:MainGraphState):
        query = state.user_input_lst
        print("Writing joke...\n")

        joke_response = await joke_model.ainvoke(
            query,
        )
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return state.parameters.update({"joke": joke_response.content})

class generate_poem(PluginBase):
    async def aprocess(self,state:MainGraphState):
        query = state.user_input_lst
        print("\nWriting poem...\n")
   
        poem_response = await poem_model.ainvoke(
            query,
        )
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return state.parameters.update({"poem": poem_response.content})


class create_graph(MainGraphBase):
    def setattr(self):
        self.nodes = {"generate_joke":generate_joke().ahandler,
                      "generate_poem": generate_poem().ahandler}
        self.config = UserThreadId("hello_1")
        self.ckp = CheckpointMemory()
        return super().setattr()
    def __call__(self, builder:StateGraph):
        for k,v in list(self.nodes.items()):
            builder.add_node(k,v)
    
        builder.set_entry_point("generate_joke")
        # Add edges
        builder.add_edge("generate_joke", "generate_poem")
        # Set the final node
        builder.set_finish_point("generate_poem")
        self.app = builder.compile(checkpointer=self.ckp)




graph = create_graph()

print(">>>   ",graph.config)
async def main():
    thinking_started = False
    
    State = MainGraphState()
    query="cats"
    joke_prompt.set_system_msg(joke_msg)
    joke_prompt.set_human_msg(query)
    msg = joke_prompt.get_messages()
    
    State.user_input = msg
    # msg = {"SystemMessage":msg[0],"HumanMessage":msg[1]}
    # State.user_input_dct = msg
    print(">><<<  ",msg)
    async for msg, metadata in graph.app.astream(State,config=graph.config,stream_mode="messages",):
        node = metadata["langgraph_node"]
        if node == "generate_joke":
            if msg.content:
                if thinking_started:
                    print("\n</thinking>\n")
                    thinking_started = False
                # print(">>><<<<")
                print(msg.content, end="", flush=True)
            if "reasoning_content" in msg.additional_kwargs:
                if not thinking_started:
                    print("<thinking>")
                    thinking_started = True
                print(msg.additional_kwargs["reasoning_content"], end="", flush=True)
        if node == "generate_poem":
            print(msg.content, end="", flush=True)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
