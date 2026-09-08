import json
from data_ingestion import process_dir, store

def ingest_data(dir: str):
    
    # Step. 1 load docs, chunk them, give them some id
    chunk_ids, chunks = process_dir.load_and_chunk(dir)
    
    with open("D:/local_assist/evaluation/chunks.jsonl", "w", encoding="utf-8") as f:
        for chunk_id, chunk in zip(chunk_ids, chunks):
            record = {
                "chunk_id": chunk_id,
                "chunk_content": chunk.page_content
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    # Step. 2 to convert these chunks into embeddings and then storing them to vector store
    vectorstore = store.VectorStore(persistent_dir = './my_chromadb', collection_name = 'codebase_docs')
    vectorstore.embedd_and_store(chunk_ids, chunks)

if __name__ == "__main__":
    
    ingest_data("D:/Full Stack PBL")