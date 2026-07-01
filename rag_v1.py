import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.ollama import OllamaEmbedding

# 1. Force override the API Key string directly if OS environment variables are acting up
# os.environ["GROQ_API_KEY"] = "gsk_..." 

print("📄 Loading PDF...")
documents = SimpleDirectoryReader(input_files=["sample4.txt"]).load_data()
print(f"✅ Loaded {len(documents)} documents")

print("🧠 Creating embeddings (using Ollama)...")
embed_model = OllamaEmbedding(model_name="nomic-embed-text", base_url="http://localhost:11434")
print("✅ Embeddings ready")

print("🤖 Connecting to Groq API...")
# SWAPPED: Using the ultra-stable, non-speculative 70B production model ID
llm = Groq(
    model="llama-3.3-70b-versatile",  # NEW 
    api_key=os.getenv("GROQ_API_KEY")
)
print("✅ LLM ready")

# Set global settings
Settings.llm = llm  
Settings.embed_model = embed_model
# Adjust chunk settings slightly to give the model better structured paragraphs
Settings.chunk_size = 512
Settings.chunk_overlap = 50

print("💾 Building index...")
index = VectorStoreIndex.from_documents(documents)
print("✅ Index ready")

print("\n" + "="*60)
print("🎯 ASKING QUESTIONS")
print("="*60 + "\n")

# Explicitly use simple response mode to avoid internal LlamaIndex looping bugs
query_engine = index.as_query_engine(response_mode="compact")

questions = [
    "What are the main topics covered in this document?",
    "What are the key safety hazards mentioned?",
    "Summarize the process or procedure described.",
]

for q in questions:
    print(f"❓ Q: {q}")
    try:
        response = query_engine.query(q)
        print(f"✅ A: {response}\n")
    except Exception as e:
        print(f"❌ Error querying: {e}\n")
    print("-" * 60 + "\n")

print("✨ RAG Pipeline working clean with Groq!")