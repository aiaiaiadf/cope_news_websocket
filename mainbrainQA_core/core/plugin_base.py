from abc import abstractmethod
from mainbrainQA_core.core.state_base import MainGraphState

class PluginBase():
    def __init__(self) -> None:
        pass
    @abstractmethod
    def process(self,state:MainGraphState):
        return state

    def handler(self,state:MainGraphState):
        state = self.process(state)
        return state
        # output = self.process(state)
        # state.tmpout = output
        # return state
    @abstractmethod
    async def aprocess(self,state:MainGraphState):
        ...

    async def ahandler(self,state:MainGraphState):
        # output = await self.aprocess(state)
        # state.tmpout = output
        # return state
        state = await self.aprocess(state)
        return state