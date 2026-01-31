import os
import chromadb

# Configuration
DB_PATH = os.path.join("知识库", "chroma_db")
COLLECTION_NAME = "books_knowledge_base"
QUERY_TEXT = "数据物主 数据标准 认证数据源 元数据注册 数据质量 数据分类分级"

def main():
    print(f"Connecting to ChromaDB at {DB_PATH}...")
    
    collection = None
    try:
        # Try new API (0.4.x+)
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        print("Using ChromaDB 0.4+ API")
    except AttributeError:
        # Fallback to old API (0.3.x)
        print("Using ChromaDB 0.3.x API")
        from chromadb.config import Settings
        chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=DB_PATH
        ))
        collection = chroma_client.get_collection(name=COLLECTION_NAME)

    if not collection:
        print("Failed to access collection.")
        return

    print(f"Querying for: '{QUERY_TEXT}'")
    
    count = collection.count() # Check available documents
    n_results = min(count, 10) if count > 0 else 1 # Safely limit results to 5
    
    results = collection.query(
        query_texts=[QUERY_TEXT],
        n_results=n_results
    )

    print("\n--- Results ---\n")
    
    # Handle different result structures if necessary, usually it's dict
    documents = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    distances = results.get('distances', [[]])[0]

    if not documents:
        print("No results found.")
    
    for i, doc in enumerate(documents):
        meta = metadatas[i] if i < len(metadatas) else {}
        dist = distances[i] if i < len(distances) else "N/A"
        
        print(f"Result {i+1} (Distance: {dist}):")
        print(f"File: {meta.get('filename', 'Unknown')}")
        print(f"Content Preview:\n{doc[:2000]}...") # Show larger preview
        print("-" * 40)

if __name__ == "__main__":
    main()
