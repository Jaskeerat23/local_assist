import chromadb
import embeddings

class VectorStore:
    def __init__(self, persistent_dir: str, collection_name: str, embedding_model: str = 'Qwen/Qwen3-Embedding-0.6B'):
        self.client = None
        self.collection = None
        self.persisten_dir = self.persisten_dir
        self.collection_name = self.collection_name
        self.embedding_model = embedding_model
        self.embedding_manager = embeddings.EmbeddingModel(embedding_model)
    
    def _create_collection(self):
        try:
            self.client = chromadb.PersistentClient(path = self.persisten_dir)
            
            self.collection = self.client.get_or_create_collection(
                name = self.collection_name
            )
        except Exception as e:
            print(f"Cannot create a collection\n{e}")
    
    def add_docs_to_store(self, chunk_ids, chunks):
        
        if self.collection.count() == len(chunks):
            print(f"The vector store already have documents inserted, total count = {self.collection.count()}\n")
            return
        
        try:
            print(f"Creating Embeddings using {self.embedding_model}\n")
            
            embeddings = self.embedding_manager.encode(chunks)
            metadata = []
            content = []
            
            for i, doc in enumerate(chunks):
                
                content.append(doc.page_content)
                
                md = doc.metadata
                md['content_length'] = len(doc.page_content)
                md['doc_index'] = i
                
                metadata.append(md)
            
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