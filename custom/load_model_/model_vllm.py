from core.model_base import model_base
from common.utils import readkey
from langchain_openai import ChatOpenAI,OpenAIEmbeddings

class model_vllm(model_base):
    def init_custom_model(self):
        key_api = readkey("configs/vllm.key")
        chat = ChatOpenAI(base_url=key_api['url'],api_key=key_api['key'],model=key_api['chat_n'])
        embed = OpenAIEmbeddings(base_url=key_api['url'],api_key=key_api['key'],model=key_api['embed_n'])
        return {"chat":chat,"embed":embed}
