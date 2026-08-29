import os
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")

client = genai.Client(api_key=API_KEY)

# Resolve path relative to this file so it works from any working directory
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PERSIST_DIR = os.path.join(_PROJECT_ROOT, "models", "chroma_db")


def load_and_chunk_document(filepath, chunk_size=500, chunk_overlap=50):
    """Reads a PDF and splits it into chunks by Q&A pair."""
    import pdfplumber

    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Skip index 0 (document header before the first question)
    raw_parts = text.split("Q:")
    chunks = []
    for part in raw_parts[1:]:
        part = part.strip()
        if part:
            chunks.append("Q:" + part)

    return chunks


class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
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

    db_client = chromadb.PersistentClient(path=persist_dir)

    try:
        db_client.delete_collection(collection_name)
    except Exception:
        pass

    embed_fn = GeminiEmbeddingFunction()
    collection = db_client.create_collection(name=collection_name, embedding_function=embed_fn)

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)

    return collection


def get_existing_collection(collection_name="university_faq", persist_dir=None):
    if persist_dir is None:
        persist_dir = DEFAULT_PERSIST_DIR
    db_client = chromadb.PersistentClient(path=persist_dir)
    embed_fn = GeminiEmbeddingFunction()
    return db_client.get_collection(name=collection_name, embedding_function=embed_fn)


def retrieve_relevant_chunks(collection, question, top_k=3):
    results = collection.query(query_texts=[question], n_results=top_k)
    return results["documents"][0]


def generate_answer(question, retrieved_chunks, max_retries=2):
    context = "\n\n".join(retrieved_chunks)

    prompt = f"""You are a helpful university FAQ assistant. Answer the student's
question using ONLY the information provided in the context below.
If the answer is not contained in the context, say exactly: "I couldn't find
a clear answer to that in the university documents I have access to. Try
rephrasing your question with more specific terms (for example, naming the
exact program, fee type, or policy you're asking about), or contact the
relevant office directly." Do not make up information.

Context:
{context}

Question: {question}

Answer:"""

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            return response.text
        except ServerError:
            if attempt < max_retries:
                time.sleep(2)
                continue

    return ("Sorry, the AI service is currently experiencing high demand and "
            "isn't responding right now. Please wait a moment and try asking "
            "your question again.")


def answer_question(collection, question, top_k=3):
    retrieved_chunks = retrieve_relevant_chunks(collection, question, top_k)
    answer = generate_answer(question, retrieved_chunks)
    return answer, retrieved_chunks
