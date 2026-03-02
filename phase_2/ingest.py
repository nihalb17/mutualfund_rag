import os
import json
import time
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = "phase_1/data/raw"
CHROMA_DIR = "phase_2/chroma_db"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def ingest_data():
    print("Loading documents from JSON to preserve metadata...")
    
    # We will load from JSON files instead of MD to get the 'url' field directly
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", " ", ""]
    )
    
    for filename in json_files:
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
            text = data.get("raw_text", "")
            url = data.get("url", "https://groww.in")
            
            fund_name = data.get("fund_name", "")
            
            # Create LangChain Document-like objects (manual chunking)
            chunks = text_splitter.split_text(text)
            for chunk in chunks:
                chunk_text = f"Fund Name: {fund_name}\n{chunk}" if fund_name else chunk
                all_chunks.append({
                    "page_content": chunk_text,
                    "metadata": {"source": url}
                })
    
    print(f"Total chunks created: {len(all_chunks)}")

    # Embeddings
    print("Generating embeddings and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Wipe existing DB for fresh start
    if os.path.exists(CHROMA_DIR):
        import shutil
        shutil.rmtree(CHROMA_DIR)
        print("Cleared existing vector store.")

    # Create the vector store and add documents one by one to ensure quota compliance
    print(f"Generating embeddings and storing in ChromaDB one-by-one to avoid rate limits...")
    
    # We need to wrap them back in LangChain Document objects
    from langchain_core.documents import Document
    docs = [Document(page_content=c["page_content"], metadata=c["metadata"]) for c in all_chunks]
    
    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    
    total = len(docs)
    for i, doc in enumerate(docs):
        print(f"Processing chunk {i+1}/{total}...")
        vectorstore.add_documents([doc])
    
    print(f"Ingestion complete. Vector store saved to {CHROMA_DIR}")

if __name__ == "__main__":
    ingest_data()
