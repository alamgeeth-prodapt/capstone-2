import os
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 1. Configure the MiniLM embedding model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def build_offline_index():
    print("Initializing ChromaDB Persistent Client...")
    
    db = chromadb.PersistentClient(path="../chroma_db")
    chroma_collection = db.get_or_create_collection("telecom_policies")

    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    documents = SimpleDirectoryReader(r"D:\Project_2\data\prodapt-project\projectfiles\data\documents").load_data()

    print("Generating embeddings and writing to ChromaDB. This may take a moment...")
    
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    print("Offline phase complete. Vectors successfully stored in ./data/chroma_db")
    return index

if __name__ == "__main__":
    build_offline_index()