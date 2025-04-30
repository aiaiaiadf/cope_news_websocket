try:
    from langchain_community.vectorstores import Chroma
except:
    from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from core.db_base import db_base
import warnings
warnings.filterwarnings("ignore")

class chromVector(db_base):
    # def __init__(self,db_params:dict) -> None:
    #     self._parser(db_params)

    def _splitSentence(self,pth):  
        full_text = self._getFile(pth)
        if full_text!=None:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size =self.chunk_sz, chunk_overlap=self.chunk_op, separators=["\n\n", "\n", " ", "", "。", "，", "；"])
            texts = text_splitter.split_documents(full_text)
            return texts
        else:
            return ""
    
    def _embeddingAndVectorDB(self,docu_txt,save_db_dir):
        db = Chroma.from_documents(documents=docu_txt,embedding=self.emmbeddings, persist_directory=save_db_dir)
        return db
    
    def _vectorFromDb(self,db_dir):
        vectordb = Chroma(persist_directory=db_dir,
                          embedding_function=self.emmbeddings)
        return vectordb