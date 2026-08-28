"""
Unit tests for the RAG pipeline core functions.
Run with: python tests/test_rag_pipeline.py

These tests check individual pieces of the pipeline work correctly
in isolation, before testing the full system end-to-end (integration
testing, done manually through the app itself).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from rag_pipeline import load_and_chunk_document


def test_chunking_produces_chunks():
    """Test that chunking a real document produces at least one chunk."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "university_faq.pdf")
    chunks = load_and_chunk_document(filepath)
    assert len(chunks) > 0, "Chunking should produce at least one chunk"
    print(f"PASS: test_chunking_produces_chunks ({len(chunks)} chunks created)")


def test_each_chunk_starts_with_q():
    """Test that every chunk starts with 'Q:' as expected from our
    Q&A-based chunking strategy."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "university_faq.pdf")
    chunks = load_and_chunk_document(filepath)
    for i, chunk in enumerate(chunks):
        assert chunk.startswith("Q:"), f"Chunk {i} does not start with 'Q:': {chunk[:50]}"
    print(f"PASS: test_each_chunk_starts_with_q (all {len(chunks)} chunks verified)")


def test_chunks_are_not_empty():
    """Test that no chunk is empty or just whitespace."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "university_faq.pdf")
    chunks = load_and_chunk_document(filepath)
    for i, chunk in enumerate(chunks):
        assert len(chunk.strip()) > 0, f"Chunk {i} is empty"
    print(f"PASS: test_chunks_are_not_empty (all {len(chunks)} chunks verified)")


def test_chunk_contains_answer_marker():
    """Test that each chunk contains an answer part ('A:'), confirming
    the Q&A pair structure is preserved during chunking."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "university_faq.pdf")
    chunks = load_and_chunk_document(filepath)
    chunks_with_answers = [c for c in chunks if "A:" in c]
    assert len(chunks_with_answers) == len(chunks), \
        "Every chunk should contain both a question and an answer"
    print(f"PASS: test_chunk_contains_answer_marker (all {len(chunks)} chunks verified)")


if __name__ == "__main__":
    print("Running RAG pipeline unit tests...\n")
    test_chunking_produces_chunks()
    test_each_chunk_starts_with_q()
    test_chunks_are_not_empty()
    test_chunk_contains_answer_marker()
    print("\nAll tests passed!")
