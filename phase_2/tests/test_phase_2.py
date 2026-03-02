import os
import pytest

CHROMA_DIR = "phase_2/chroma_db"

def test_vector_db_persistence():
    """Verify ChromaDB files are created and non-empty."""
    if not os.path.exists(CHROMA_DIR):
        pytest.skip("ChromaDB directory not found. Run ingestion first.")
    
    assert len(os.listdir(CHROMA_DIR)) > 0

def test_embedding_retrieval():
    """Verify that a simple query returns at least one document from the vector store."""
    from langchain_community.vectorstores import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from dotenv import load_dotenv
    
    load_dotenv()
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    
    results = vectorstore.similarity_search("What is Axis Liquid Fund?", k=1)
    assert len(results) > 0
    assert "Axis" in results[0].page_content
