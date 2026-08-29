"""
RAG Pipeline for University FAQ Chatbot
=========================================
This file contains the core logic of our chatbot:
1. Load documents
2. Split them into chunks
3. Convert chunks into embeddings (numerical representations)
4. Store embeddings in a vector database (Chroma)
5. Retrieve relevant chunks for a user's question
6. Generate an answer using Gemini, based only on retrieved chunks
"""

import os
from google import genai
from google.genai import types
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

client = genai.Client(api_key=API_KEY)

# Always resolve the vector store path relative to this file's location,
# so it works correctly whether we run from src/, app/, or anywhere else.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PERSIST_DIR = os.path.join(_PROJECT_ROOT, "models", "chroma_db")


# -------------------------------------------------------------------
# STEP 1: Load and chunk the document
# -------------------------------------------------------------------
def load_and_chunk_document(filepath, chunk_size=500, chunk_overlap=50):
    """
    Reads a PDF file and splits it into chunks based on Q&A pairs
    (each chunk starts at a "Q:" marker). This keeps each question and
    its answer together as one complete unit, instead of cutting text
    at an arbitrary character count that could split a sentence or
    answer in half.
    """
    import pdfplumber

    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Split the document at every "Q:" marker, keeping the marker attached.
    # The first split part (before the very first "Q:") is document header
    # text (title, section headings before any question), not a real Q&A
    # pair, so we skip it.
    raw_parts = text.split("Q:")
    chunks = []
    for part in raw_parts[1:]:
        part = part.strip()
        if part:
            chunks.append("Q:" + part)

    return chunks


# -------------------------------------------------------------------
# STEP 2 & 3: Create embeddings and store in Chroma vector database
# -------------------------------------------------------------------
class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Custom embedding function that uses Gemini's embedding model."""

    def __call__(self, input):
        embeddings = []
        for text in input:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
            embeddings.append(result.embeddings[0].values)
        return embeddings


def build_vector_store(chunks, collection_name="university_faq", persist_dir=None):
    if persist_dir is None:
        persist_dir = DEFAULT_PERSIST_DIR
    """
    Takes text chunks, embeds them, and stores them in a Chroma
    vector database saved to disk (so we don't have to rebuild it
    every time we run the app).
    """
    db_client = chromadb.PersistentClient(path=persist_dir)

    # Delete old collection if it exists (so we can rebuild cleanly)
    try:
        db_client.delete_collection(collection_name)
    except Exception:
        pass

    embed_fn = GeminiEmbeddingFunction()
    collection = db_client.create_collection(name=collection_name, embedding_function=embed_fn)

    # Add chunks with unique IDs
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)

    return collection


def get_existing_collection(collection_name="university_faq", persist_dir=None):
    """Loads an already-built vector store (so we don't rebuild every run)."""
    if persist_dir is None:
        persist_dir = DEFAULT_PERSIST_DIR
    db_client = chromadb.PersistentClient(path=persist_dir)
    embed_fn = GeminiEmbeddingFunction()
    return db_client.get_collection(name=collection_name, embedding_function=embed_fn)


# -------------------------------------------------------------------
# STEP 4: Retrieve relevant chunks for a given question
# -------------------------------------------------------------------
def retrieve_relevant_chunks(collection, question, top_k=3):
    """
    Searches the vector store for the chunks most similar (relevant)
    to the user's question. Returns the top_k most relevant chunks.
    """
    results = collection.query(query_texts=[question], n_results=top_k)
    retrieved_chunks = results["documents"][0]
    return retrieved_chunks


# -------------------------------------------------------------------
# STEP 5: Generate an answer using Gemini, grounded in retrieved chunks
# -------------------------------------------------------------------
def generate_answer(question, retrieved_chunks, max_retries=2):
    """
    Builds a prompt that includes the retrieved context, then asks
    Gemini to answer ONLY based on that context. This is what makes
    it "grounded" (reduces hallucination) instead of a plain chatbot.

    Automatically retries a couple of times if the API is temporarily
    unavailable (a common, expected occurrence with external services),
    and returns a friendly message instead of crashing if it still
    fails after retries.
    """
    import time

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""You are a helpful university FAQ assistant. Answer the student's
question using ONLY the information provided in the context below.
If the answer is not contained in the context, say "I don't have that
information in the university documents I have access to. Please contact
the relevant office directly." Do not make up information.

Context:
{context}

Question: {question}

Answer:"""

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2)  # brief pause before retrying
                continue

    # All retries failed — return a friendly message instead of crashing
    return ("Sorry, the AI service is currently experiencing high demand and "
            "isn't responding right now. Please wait a moment and try asking "
            "your question again.")


# -------------------------------------------------------------------
# Full pipeline function (used by the app)
# -------------------------------------------------------------------
def answer_question(collection, question, top_k=3):
    """
    Full RAG flow: retrieve relevant chunks, then generate an answer.
    Returns both the answer and the source chunks (for citation display).
    """
    retrieved_chunks = retrieve_relevant_chunks(collection, question, top_k)
    answer = generate_answer(question, retrieved_chunks)
    return answer, retrieved_chunks
