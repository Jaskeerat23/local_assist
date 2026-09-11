import chromadb 
import nltk
import pickle
from . import embeddings
from typing import List, Any, Dict
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
nltk.download('punkt_tab')

class VectorStore:
    def __init__(self, persistent_dir: str, collection_name: str, embedding_model: str = 'Qwen/Qwen3-Embedding-0.6B'):
        self.client = None
        self.collection = None
        self.persisten_dir = persistent_dir
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_manager = embeddings.EmbeddingModel(embedding_model)
        self._create_collection()
    
    def _create_collection(self):
        try:
            self.client = chromadb.PersistentClient(path = self.persisten_dir)
            
            self.collection = self.client.get_or_create_collection(
                name = self.collection_name
            )
        except Exception as e:
            print(f"Cannot create a collection\n{e}")
    
    def embedd_and_store(self, chunk_ids: List[Any], chunks: List[Any]):
        
        try:
            print(f"Creating Embeddings using {self.embedding_model}\n")
            
            docs = [chunk.page_content for chunk in chunks]
            
            embeddings = self.embedding_manager.encode(docs)
            metadata = []
            content = []
            
            for i, doc in enumerate(chunks):
                
                content.append(doc.page_content)
                
                md = {
                    **doc.metadata,
                    'content_length': len(doc.page_content),
                    'doc_index': i
                }
                
                metadata.append(md)
            
            print(f"Sample of embeddings (FIRST 100 NUMBERS)\n{embeddings[0][:100]}")
            
            self.collection.add(
                ids = chunk_ids,
                embeddings = embeddings,
                metadatas = metadata,
                documents = content
            )
            
            print(f"Successfully added {len(chunks)} chunks into the vector store")
            print(f"Total count in vector store is {self.collection.count()}")
            
        except Exception as e:
            print(f"Error inserting documents into collection\n{e}")

class SparseVectorStore:
    def __init__(self, collection_path: str):
        self.collection_path = collection_path
    
    def add_docs_to_store(self, chunks: List[Any]):
        
        try:
            tokenized_chunks = [word_tokenize(chunk.page_content) for chunk in chunks]
            
            bm25Tab = BM25Okapi(tokenized_chunks)
            
            with open(self.collection_path, 'wb') as f:
                pickle.dump(bm25Tab, f)
            
            print(f"Stored BM25 table successfully in {self.collection_path}")
        
        except Exception as e:
            print(f"Error inserting docs into sparse store\n{e}")