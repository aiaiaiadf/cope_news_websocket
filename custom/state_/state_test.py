from core.state_base import (StrSateBase,
                             MessagesState,
                             GloobalState,
                             ParameterState,
                             HistoryState)


class MainGraphState(MessagesState,StrSateBase,GloobalState,HistoryState,ParameterState):
    pass