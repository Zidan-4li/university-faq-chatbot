import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from rag_pipeline import load_and_chunk_document

FAQ_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "university_faq.pdf")


def test_chunking_produces_chunks():
    chunks = load_and_chunk_document(FAQ_PATH)
    assert len(chunks) > 0
    print(f"PASS: test_chunking_produces_chunks ({len(chunks)} chunks created)")


def test_each_chunk_starts_with_q():
    chunks = load_and_chunk_document(FAQ_PATH)
    for i, chunk in enumerate(chunks):
        assert chunk.startswith("Q:"), f"Chunk {i} does not start with 'Q:': {chunk[:50]}"
    print(f"PASS: test_each_chunk_starts_with_q (all {len(chunks)} chunks verified)")


def test_chunks_are_not_empty():
    chunks = load_and_chunk_document(FAQ_PATH)
    for i, chunk in enumerate(chunks):
        assert len(chunk.strip()) > 0, f"Chunk {i} is empty"
    print(f"PASS: test_chunks_are_not_empty (all {len(chunks)} chunks verified)")


def test_chunk_contains_answer_marker():
    chunks = load_and_chunk_document(FAQ_PATH)
    chunks_with_answers = [c for c in chunks if "A:" in c]
    assert len(chunks_with_answers) == len(chunks)
    print(f"PASS: test_chunk_contains_answer_marker (all {len(chunks)} chunks verified)")


if __name__ == "__main__":
    print("Running RAG pipeline unit tests...\n")
    test_chunking_produces_chunks()
    test_each_chunk_starts_with_q()
    test_chunks_are_not_empty()
    test_chunk_contains_answer_marker()
    print("\nAll tests passed!")
