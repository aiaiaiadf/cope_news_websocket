from mainbrainQA_core.core.model_base import model_base
try:
    from langchain_ollama import OllamaEmbeddings,ChatOllama
except:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.chat_models import ChatOllama
from mainbrainQA_core.common.utils import readkey


class model_ollama(model_base):
    def init_custom_model(self,key_path=""):
        if key_path is "":
            key_api = readkey("configs/ollama.key")
        else:
            key_api = readkey(key_path)
        if key_api.get("temperature"):
            chat = ChatOllama(base_url=key_api['url'],model=key_api['chat_n'],temperature=float(key_api["temperature"]))
        else:
            chat = ChatOllama(base_url=key_api['url'],model=key_api['chat_n'])
        embed = OllamaEmbeddings(base_url=key_api['url'],model=key_api['embed_n'])
        return {"chat":chat,"embed":embed}