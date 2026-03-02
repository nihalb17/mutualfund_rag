import pytest
from fastapi.testclient import TestClient
from phase_3.api import app
from phase_3.pipeline import MutualFundRAG
import os

client = TestClient(app)

def test_api_connection():
    """Verify the FastAPI server is reachable."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_retriever_logic():
    """Verify that the retriever initialization and a basic ask works."""
    rag = MutualFundRAG()
    # Use a query that should definitely be in the Axis data
    result = rag.ask("What is Axis Liquid Fund?")
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) > 0

def test_citation_mapping():
    """Verify that the response includes correct source URLs."""
    rag = MutualFundRAG()
    result = rag.ask("Expense ratio of Axis Midcap Fund")
    
    # Check if at least one Groww link is in sources
    has_groww_link = any("groww.in" in source for source in result["sources"])
    assert has_groww_link

def test_chat_endpoint():
    """Verify the /chat endpoint returns a valid response."""
    response = client.post("/chat", json={"message": "What is the NAV of Axis Small Cap Fund?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
