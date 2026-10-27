"""
Unit tests for ThreatLens AI RAG retriever and grounded security assistant.
"""

import pytest
from src.retriever import ThreatLensRetriever
from src.rag_assistant import ThreatLensSecurityAssistant

@pytest.fixture(scope="module")
def retriever():
    return ThreatLensRetriever(persist_dir="vector_store")

@pytest.fixture(scope="module")
def assistant(retriever):
    return ThreatLensSecurityAssistant(retriever=retriever)

def test_retriever_returns_relevant_chunks(retriever):
    query = "How to respond to SYN flood Denial of Service attack?"
    results = retriever.retrieve(query, top_k=3)
    assert len(results) > 0
    top_hit = results[0]
    assert "score" in top_hit
    assert "text" in top_hit
    assert "source" in top_hit
    assert "title" in top_hit
    assert top_hit["score"] > 0.20

def test_assistant_generates_grounded_citations(assistant):
    query = "What does a high Flow Packets per second rate indicate?"
    response = assistant.generate_response(query, top_k=2)
    assert "answer" in response
    assert "citations" in response
    assert len(response["citations"]) > 0
    assert response["retrieved_count"] > 0
    # Check citation structure
    cit = response["citations"][0]
    assert "citation_id" in cit
    assert "title" in cit
    assert "excerpt" in cit

def test_assistant_handles_unsupported_out_of_scope_query(assistant):
    # Query completely outside cybersecurity scope with high score threshold
    obscure_query = "What is the recipe for baking chocolate chip cookies?"
    response = assistant.generate_response(obscure_query, score_threshold=0.60)
    assert "Insufficient Evidence" in response["answer"]
    assert len(response["citations"]) == 0
