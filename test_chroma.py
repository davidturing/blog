import chromadb
try:
    client = chromadb.Client()
    print("ChromaDB initialized successfully!")
except Exception as e:
    print(f"ChromaDB initialization failed: {e}")
