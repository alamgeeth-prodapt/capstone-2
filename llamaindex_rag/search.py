import chromadb
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DB = PROJECT_ROOT / "chroma_db"

def test_vector_search(query: str) -> str:

    db = chromadb.PersistentClient(path=str(CHROMA_DB))

    chroma_collection = db.get_collection("telecom_policies")

    vector_store = ChromaVectorStore(
        chroma_collection=chroma_collection
    )

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context
    )

    retriever = index.as_retriever(
        similarity_top_k=2
    )

    nodes = retriever.retrieve(query)

    results = []

    for i, node in enumerate(nodes, 1):
        results.append(
            f"Chunk {i}:\n{node.text}"
        )

    return "\n\n".join(results)


if __name__ == "__main__":
    result = test_vector_search(
        "What is the purpose of the roaming policy?"
    )

    print(result)