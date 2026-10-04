import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase, VectorStoreIndex, Settings
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv

load_dotenv()

# Configure Claude Haiku and HuggingFace Embeddings globally
Settings.llm = Anthropic(model="claude-haiku-4-5-20251001", api_key=os.environ.get("ANTHROPIC_API_KEY"))
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 1. Connect to data/telecom_ops.db using the LlamaIndex SQLDatabase wrapper
engine = create_engine("sqlite:///./telecom_ops.db")
sql_database = SQLDatabase(engine) #

# 2. Create SQLTableNodeMapping for all tables in the schema
table_node_mapping = SQLTableNodeMapping(sql_database) #[cite: 1]

# 3. Define SQLTableSchema objects with context strings for semantic table selection
# These context strings help the embedding model map user queries to the correct telecom data tables.
table_schemas = [
    SQLTableSchema(
        table_name="network_outages",
        context_str="Historical outage records. Describes outage severity, affected customers, and incident IDs." #[cite: 1]
    ),
    SQLTableSchema(
        table_name="network_towers",
        context_str="Tower inventory. Describes tower locations, region, city, technology, and operational status." #[cite: 1]
    ),
    SQLTableSchema(
        table_name="tower_performance",
        context_str="Live network metrics. Describes latency, packet loss, throughput, and signal strength for towers." #[cite: 1]
    ),
    SQLTableSchema(
        table_name="customer_subscriptions",
        context_str="Customer account data. Describes plan names, subscription fees, and account types by region." #[cite: 1]
    )
]

# 4. Build ObjectIndex over table schemas using VectorStoreIndex
obj_index = ObjectIndex.from_objects(
    table_schemas,
    table_node_mapping,
    VectorStoreIndex,
)

# 5. Create SQLTableRetrieverQueryEngine with similarity_top_k of 1 or 2
query_engine = SQLTableRetrieverQueryEngine(
    sql_database=sql_database,
    table_retriever=obj_index.as_retriever(similarity_top_k=2) #[cite: 1]
)

# 6. Expose a single function that accepts a question and returns the synthesized answer
def query_network_analytics(question: str) -> str:
    response = query_engine.query(question)
    return str(response)

if __name__=="__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found in environment variables.")
    else:
        # Scenario 2 Test Question
        test_question = "Which region had the most CRITICAL network outages recently?" #
        
        print(f"Question: {test_question}")
        print("Running semantic SQL query...\n")
        
        try:
            answer = query_network_analytics(test_question)
            print("--- Synthesized Answer ---")
            print(answer)
        except Exception as e:
            print(f"Error during query execution: {e}")