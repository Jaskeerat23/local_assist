import json
from app import retrieve
from data_ingestion import store

def eval_retrieval(record, n_results = 5, dataset_path: str = 'evaluation/rag_eval_dataset.json'):
    json_data = ""
    recall = []
    with open(dataset_path, 'r') as f:
        json_data = json.load(f)
    
    # the dataset returned is list of json basically -> List[JSON]
    vector_store = store.VectorStore(persistent_dir = './my_chromadb', collection_name = 'codebase_docs') # this must be same as ingest.py
    retrivalEngine = retrieve.Retrieval(vector_store = vector_store, n_results = n_results)
    
    for i, sample in enumerate(json_data, start = 1):
        
        print(f"Retrieving context for {i} question...")
        
        query = sample['question']
        relevant_chunk_ids = set(sample['relevant_chunk_ids'])
        
        relevant_docs = retrivalEngine.retrieval_engine(query)
        
        ret_chunk_ids = set(relevant_docs["ids"][0])
        
        recall_k = len(ret_chunk_ids.intersection(relevant_chunk_ids))/len(relevant_chunk_ids)
        recall.append(recall_k)        
    print(f"Recall over whole dataset is {recall}")
    print(f"Avg. Recall over whole dataset is {sum(recall)/len(recall)}")
    
    record.update({'summary' : input('Give some summary of changes: ')})
    record.update({'n_results' : n_results})
    record.update({'recall@k' : recall})
    record.update({'average recall@k' : sum(recall)/len(recall)})
    
    with open('evaluation/metrics.jsonl', 'a') as f:
        
        json.dump(record, f, indent=4)
        f.write('\n')


if __name__ == "__main__":
    record = dict({})
    
    abort = int(input("Warning! Records fields must be changed each time during new tests!!\nType 1 to continue and 0 to abort: "))
    
    if not abort:
        exit(0)
    
    #Update these fields each time if there is any change
    record.update({'chunk_size' : 1000})
    record.update({'chunk_overlap' : 200})
    record.update({'embedding_model' : 'Qwen/Qwen3-Embedding-0.6B'})
    record.update({'search_type' : 'dense embeddings'})
    
    eval_retrieval(record, n_results=20)