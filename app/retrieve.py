from data_ingestion import store, embeddings
from typing import List, Any, Dict

class Retrieval:
    def __init__(self, vector_store: store.VectorStore, embedding_model: str = "Qwen/Qwen3-Embedding-0.6B", n_results: int = 10):
        self.vector_store = vector_store
        self.embedding_manager = embeddings.EmbeddingModel(embedding_model)
        self.n_results = self.n_results
    
    def retrieval_engine(self, query: str) -> Dict[Any]:
        
        try:
            query_embs = self.embedding_manager.encode([query])[0]
            
            relevant_docs = self.vector_store.collection.query(
                query_embeddings = query_embs,
                n_results = self.n_results,
                include = ['metadatas', 'documents', 'distances']
            )
            
            ranks = [i for i in range(1, self.n_results + 1)]
            
            relevant_docs.update({'ranks' : ranks})
            
            return relevant_docs
            
        except Exception as e:
            print(f"Error fetching relevant documents\n{e}")


if __name__ == "__main__":
    
    vector_store = store.VectorStore(persistent_dir = './my_chromadb', collection_name = 'codebase_docs') # this must be same as ingest.py
    retrieval_engine = Retrieval(vector_store)
    
    relevant_docs = retrieval_engine.retrieval_engine("explain the backend code for routes")