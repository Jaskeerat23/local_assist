from data_ingestion import process_dir, store

def ingest_data(dir: str):
    
    # Step. 1 load docs, chunk them, give them some id
    chunk_ids, chunks = process_dir.load_and_chunk(dir)
    
    # Step. 2 to convert these chunks into embeddings and then storing them to vector store
    vectorstore = store.VectorStore(persistent_dir = './my_chromadb', collection_name = 'codebase_docs')
    vectorstore.embedd_and_store(chunk_ids, chunks)

if __name__ == "__main__":
    
    ingest_data("D:/Full Stack PBL")