import pickle
from data_ingestion import store, embeddings
from typing import List, Any, Dict
from rank_bm25 import BM25Okapi
from collections import Counter
from nltk.tokenize import word_tokenize

class Retrieval:
    def __init__(self, vector_store: store.VectorStore, sparse_store_path: str, k: int, n_results: int = 10, embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"):
        self.k = k # k is for smoothning factor using in RRF, THIS IS NOT TOP_K documents
        self.vector_store = vector_store
        self.sparse_store_path = sparse_store_path
        self.embedding_manager = embeddings.EmbeddingModel(embedding_model)
        self.n_results = n_results
    
    def bm25_retrieval(self, query: str):
        
        bm25Tab = list()
        with open(self.sparse_store_path, 'rb') as f:
            bm25Tab = pickle.load(f)
        
        chunk_ids = list()
        
        with open('data/chunk_ids.pkl', 'rb') as f:
            chunk_ids = pickle.load(f)
        
        query = word_tokenize(query)
        
        doc_scores = bm25Tab.get_scores(query)
        
        comb_list = [(chunk_id, score) for chunk_id, score in zip(chunk_ids, doc_scores)]
        
        res = sorted(comb_list, key = lambda x: x[1], reverse = True)
        
        # res = [(i, chunk_id, score) for i, chunk_id, score in enumerate(res, start = 1)]
        
        top_res = res[:self.n_results]
        
        print("Maximum score:", max(doc_scores))
        print("Minimum score:", min(doc_scores))

        
        relevant_docs = {
            'ids' : [chunk_id for chunk_id, _ in top_res],
            'ranks' : [i for i in range(1, len(top_res) + 1)],
            'scores': [score for _, score in top_res]
        }
        
        return relevant_docs
    
    def retrieval_engine(self, query: str) -> Dict[Any, Any]:
        
        try:
            query_embs = self.embedding_manager.encode([query])[0]
            
            relevant_docs = self.vector_store.collection.query(
                query_embeddings = query_embs,
                n_results = self.n_results,
                include = ['metadatas', 'documents', 'distances']
            )
            
            ranks = [i for i in range(1, len(relevant_docs["ids"][0]) + 1)]
            
            relevant_docs.update({'ranks' : ranks})
            
            return relevant_docs
            
        except Exception as e:
            print(f"Error fetching relevant documents\n{e}")
    
    def rrf(self, all_chunk_ids: List[Any], dense_ranks: Dict, sparse_ranks: Dict) -> List[Any]:
        '''
        This function is implementation of Reciprocal Rank Fusion
        RRF(d) = Sum (r e R) 1/(k + rank(r, d))
        '''
        
        resultant_rank = []
        
        for chunk_id in all_chunk_ids:
            rank_score = 0
            
            if dense_ranks.get(chunk_id, 0) != 0:
                rank_score += 1/(self.k + dense_ranks[chunk_id])
            
            if sparse_ranks.get(chunk_id, 0) != 0:
                rank_score += 1/(self.k + sparse_ranks[chunk_id])
            
            resultant_rank.append((chunk_id, rank_score))
        
        resultant_rank = sorted(resultant_rank, key = lambda x: x[1], reverse = True)
        
        return resultant_rank[:self.n_results]
    
    def hybrid_search(self, query: str):
        
        dense_docs = self.retrieval_engine(query)
        bm25_docs = self.bm25_retrieval(query)
        
        dense_ranks = {chunk_id : rank for chunk_id, rank in zip(dense_docs['ids'][0], dense_docs['ranks'])}
        sparse_ranks = {chunk_id : rank for chunk_id, rank in zip(bm25_docs['ids'], bm25_docs['ranks'])}
        # print(dense_docs['ids'][0])
        # print(bm25_docs['ids'])
        all_chunk_ids = set()
        for chunk_id in dense_docs['ids'][0]:
            all_chunk_ids.add(chunk_id)
            
        for chunk_id in bm25_docs['ids']:
            all_chunk_ids.add(chunk_id)
        # print(self.rrf(all_chunk_ids, dense_ranks, sparse_ranks))
        resultant_ranks = [(chunk_id, i) for i, (chunk_id, _) in enumerate(self.rrf(all_chunk_ids, dense_ranks, sparse_ranks), start = 1)]
        res_chunk_ids = [chunk_id for chunk_id, _ in resultant_ranks]
        
        res_docs = self.vector_store.collection.get(
            ids = res_chunk_ids,
            include = ['documents', 'metadatas']
        )
        
        return res_docs


if __name__ == "__main__":
    
    vector_store = store.VectorStore(persistent_dir = './my_chromadb', collection_name = 'codebase_docs') # this must be same as ingest.py
    retrieval_engine = Retrieval(vector_store)
    
    relevant_docs = retrieval_engine.retrieval_engine("explain the backend code for routes")