"""
Run this script ONCE to build the vector store from your FAQ document.
This reads the document, chunks it, creates embeddings, and saves
everything to disk so the app can use it later without rebuilding.
"""

from rag_pipeline import load_and_chunk_document, build_vector_store

if __name__ == "__main__":
    print("Loading and chunking document...")
    chunks = load_and_chunk_document("../data/university_faq.txt")
    print(f"Created {len(chunks)} chunks.")

    print("Building vector store (this calls the Gemini embedding API)...")
    collection = build_vector_store(chunks)
    print("Vector store built and saved successfully!")
    print(f"Total chunks stored: {collection.count()}")
