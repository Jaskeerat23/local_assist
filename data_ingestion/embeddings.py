from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import process_dir
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"device is {device}")

class EmbeddingModel:
    def __init__(self, model_name: str = 'Qwen/Qwen3-Embedding-0.6B'):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.model = SentenceTransformer(self.model_name, device = device)
        except Exception as e:
            print(f"Error loading the embedding model\n{e}")
    
    def encode(self, chunks: List[Any]):
        docs = [doc.page_content for doc in chunks]
        embs = self.model.encode(docs)
        
        return embs

if __name__ == "__main__":
    embedding_manager = EmbeddingModel()
    embs = embedding_manager.encode(process_dir.load_and_chunk("D:/Full Stack PBL"))
    
    print(f"SAMPLE OF EMBEDDINGS (first 300 numbers):\n{embs[0][:300]}")