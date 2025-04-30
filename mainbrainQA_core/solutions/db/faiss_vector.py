try:
    from langchain_community.vectorstores import FAISS
except:
    from langchain.vectorstores import FAISS
import faiss,os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.in_memory import InMemoryDocstore
from core.db_base import db_base


class  faissVector(db_base):

    def _splitSentence(self,pth):
        full_text = self._getFile(pth)
        if full_text!=None:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size =self.chunk_sz, chunk_overlap=self.chunk_op, separators=["\n\n", "\n", " ", "", "。", "，", "；"])
            texts = text_splitter.split_documents(full_text)
            return texts
        else:
            return ""
    
    def _embeddingAndVectorDB(self,docu_txt,save_db_dir):
        index = faiss.IndexFlatL2(len(self.emmbeddings.embed_query("hello world")))
        vector_store = FAISS(
            embedding_function=self.emmbeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        updir = os.path.splitext(save_db_dir)[-1]
        """
        for para in paragraphs:
            # summary 作为摘要或者标题,做为全局检索或者映射.
            documents += [Document(page_content=para.page_content,metadata={"summary":"123"})]
            print(para.page_content)
            uuids += [str(i)]
            i+=1
            print("=====================")
        """
        
        indx = [str(i+1) for i in range(len(docu_txt))]
        vector_store.add_documents(documents=docu_txt,ids=indx)
        vector_store.save_local(save_db_dir)

        # db = FAISS.from_documents(documents=docu_txt,embedding=self.emmbeddings)
        # db.save_local(folder_path=save_db_dir)
        return vector_store
    
    def _vectorFromDb(self,db_dir):
        vectordb = FAISS.load_local(folder_path=db_dir,embeddings=self.emmbeddings, allow_dangerous_deserialization=True)
        # vectordb = FAISS.load_local(db_dir,self.emmbeddings, allow_dangerous_deserialization=True)
        return vectordb