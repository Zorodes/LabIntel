import os
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage
from llama_index.llms.groq import Groq
from llama_index.embeddings.ollama import OllamaEmbedding

PERSIST_DIR = "./storage"
DOCUMENTS_DIR = "./documents"

print("Loading all PDFs from documents folder...")
documents = SimpleDirectoryReader(input_dir=DOCUMENTS_DIR).load_data()
print(f"Loaded {len(documents)} documents")

print("Creating embeddings (using Ollama)...")
embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
print("Embeddings ready")

print("Connecting to Groq API...")
llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)
print("LLM ready")

# Set global settings
Settings.llm = llm  
Settings.embed_model = embed_model
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# PERSISTENCE LOGIC
if os.path.exists(PERSIST_DIR):
    print(f"Index cache found at {PERSIST_DIR}")
    user_input = input("Did you add new files? (y/n): ").strip().lower()
    
    if user_input == 'y':
        print("Loading existing index...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        print("Adding new documents to existing index...")
        # Add only new documents
        for doc in documents:
            index.insert(doc)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("New documents added to index!")
    else:
        print("Loading cached index...")
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        print("Index loaded from cache (no rebuild!)")
else:
    print("Building index for the first time...")
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print(f"Index built and saved to {PERSIST_DIR}")

print("\n" + "="*60)
print("ASKING QUESTIONS")
print("="*60 + "\n")

query_engine = index.as_query_engine(response_mode="compact")

questions = [
    "What are the main topics covered in this document?",
    "What are the key safety hazards mentioned?",
    "Summarize the process or procedure described.",
]

for q in questions:
    print(f"Q: {q}")
    try:
        response = query_engine.query(q)
        print(f"A: {response}\n")
    except Exception as e:
        print(f"Error querying: {e}\n")
    print("-" * 60 + "\n")

print("RAG Pipeline working clean with Groq!")