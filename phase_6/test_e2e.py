import pytest
from phase_3.pipeline import MutualFundRAG

@pytest.fixture
def rag_system():
    return MutualFundRAG()

def test_e2e_factual_query(rag_system):
    """Test a full factual query flow."""
    query = "What is the NAV of Axis Bluechip Fund?"
    # Note: Even if Bluechip isn't specifically in our 7-fund list, we check if it handles it (it might be in general knowledge or guardrailed)
    # Let's use one we KNOW we have: Axis Large Cap
    query = "What is the NAV of Axis Large Cap Fund?"
    result = rag_system.ask(query)
    
    assert "answer" in result
    assert "sources" in result
    assert "70.07" in result["answer"] # Based on raw json nav
    assert any("axis-large-cap" in s for s in result["sources"])

def test_e2e_guardrail_advice(rag_system):
    """Test guardrail against investment advice in E2E."""
    query = "Should I buy Axis Midcap fund today?"
    result = rag_system.ask(query)
    assert "information regarding mutual funds" in result["answer"].lower()

def test_e2e_guardrail_out_of_scope(rag_system):
    """Test out-of-scope guardrail in E2E."""
    query = "Who is the Prime Minister of India?"
    result = rag_system.ask(query)
    assert "don't have an answer" in result["answer"].lower()

def test_e2e_unknown_scheme(rag_system):
    """Test unknown fund guardrail in E2E."""
    query = "Detail the performance of SBI Small Cap Fund."
    result = rag_system.ask(query)
    assert "dont have information regarding the scheme" in result["answer"].lower()
