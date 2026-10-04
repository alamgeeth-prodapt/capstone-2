import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

# 1. Configure the MiniLM embedding model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 2. Add precise chunking settings
# Reduce chunk_size to isolate specific policy sections (e.g., just Zone B pricing)
Settings.chunk_size = 256 
# Keep a small overlap so sentences at the edges are not lost
Settings.chunk_overlap = 25 
Settings.text_splitter = SentenceSplitter(chunk_size=256, chunk_overlap=25)

def build_offline_index():
    print("Initializing ChromaDB Persistent Client...")
    db = chromadb.PersistentClient(path="../chroma_db")
    chroma_collection = db.get_or_create_collection("telecom_policies",metadata={"hnsw:space": "cosine"})

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Loading policy documents from ./data/documents...")
    documents = SimpleDirectoryReader(r"D:\Project_2\data\prodapt-project\projectfiles\data\documents").load_data()

    print("Generating precise embeddings...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    return index

if __name__ == "__main__":
    build_offline_index()