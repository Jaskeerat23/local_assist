from . import retrieve
from data_ingestion import store
import ollama

vectorstore = store.VectorStore(
    persistent_dir='./my_chromadb',
    collection_name='codebase_docs'
)

retriever = retrieve.Retrieval(
    vectorstore,
    'data/bm25Table.pkl',
    60,
    n_results=50
)


def chat(query, model_name='qwen3:4b'):

    # Hybrid retrieval
    results = retriever.hybrid_search(query)

    # Extract retrieved documents
    documents = results["documents"]
    metadatas = results["metadatas"]

    # Build context
    context_parts = []

    for i, (doc, metadata) in enumerate(zip(documents, metadatas)):

        source = metadata.get("file_name", "Unknown")

        context_parts.append(
            f"""--- Retrieved Chunk {i + 1} ---
Source: {source}

{doc}
"""
        )

    context = "\n".join(context_parts)

    # Prompt
    prompt = f"""
You are a coding assistant working with a specific codebase.

Answer the user's question using ONLY the provided context.

Rules:
- Do not invent information that is not present in the context.
- If the context does not contain enough information to answer the question,
  clearly say that the information was not found in the retrieved codebase.
- When possible, mention the source file relevant to your answer.
- Explain code behavior clearly and concisely.

CONTEXT:
{context}

USER QUESTION:
{query}

ANSWER:
"""

    # Local LLM inference
    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]

answer = chat(input("Enter your query, i am a local coding assistant:\n"))
print(answer)