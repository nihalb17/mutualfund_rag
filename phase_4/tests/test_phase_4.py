import pytest
from phase_3.pipeline import MutualFundRAG

@pytest.fixture
def rag():
    return MutualFundRAG()

def test_advice_filter(rag):
    """Query 'Should I invest?' -> Expect disclaimer."""
    queries = [
        "Should I invest in Axis Midcap?",
        "Is it good to buy Axis Liquid fund now?",
        "Give me some investment advice on mutual funds"
    ]
    for q in queries:
        result = rag.ask(q)
        assert result["answer"] == "I am only here to provide information regarding mutual funds."

def test_out_of_scope_filter(rag):
    """Query 'Weather in Delhi' -> Expect out-of-scope response."""
    result = rag.ask("What is the weather in Delhi?")
    # The LLM prompt handles this if not caught by pre-guardrails
    assert "I don't have an answer to the question you are asking." in result["answer"]

def test_unknown_scheme_filter(rag):
    """Query 'HDFC Fund' -> Expect 'I dont have information regarding the scheme'."""
    queries = [
        "What is the NAV of HDFC Liquid Fund?",
        "Tell me about SBI Small Cap fund",
        "Axis Bluechip Fund returns" # Axis but not in our 7 links
    ]
    for q in queries:
        result = rag.ask(q)
        assert result["answer"] == "I dont have information regarding the scheme."

def test_factual_adherence(rag):
    """Verify it still answers factual questions within scope."""
    result = rag.ask("What is the expense ratio of Axis Midcap Fund?")
    assert "0." in result["answer"] or "%" in result["answer"]
    assert len(result["sources"]) > 0
    assert "groww.in" in result["sources"][0]
