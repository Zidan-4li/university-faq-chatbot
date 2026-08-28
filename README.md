# University FAQ Chatbot (RAG)

A chatbot that answers student questions about admissions, fees, courses, and
campus facilities using Retrieval-Augmented Generation (RAG).

## How it works

1. University FAQ documents are split into chunks based on each question-and-answer
   pair, so each chunk contains one complete, self-contained piece of information.
2. Each chunk is converted into an embedding (a numerical representation of
   its meaning) using Google's Gemini embedding model.
3. Embeddings are stored in a vector database (ChromaDB).
4. When a student asks a question, the system finds the most relevant chunks
   by comparing the question's embedding to the stored chunk embeddings.
5. The relevant chunks are passed to Gemini along with the question, and
   Gemini generates an answer grounded in that information (reducing made-up
   answers).
6. The app displays the answer along with the source text it was based on.

## Tech Stack

- **Language:** Python
- **LLM & Embeddings:** Google Gemini API
- **Vector Database:** ChromaDB
- **Frontend:** Streamlit

## Setup Instructions

1. Clone this repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your Gemini API key:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   Get a free key at https://aistudio.google.com/apikey
4. Build the knowledge base (run once, or whenever the FAQ document changes):
   ```
   cd src
   python build_knowledge_base.py
   ```
5. Run the app:
   ```
   cd ../app
   streamlit run app.py
   ```
6. Open the local URL shown in your terminal (usually http://localhost:8501)

## Project Structure

```
university-faq-chatbot/
├── data/               # Source FAQ documents
├── src/                # Core RAG pipeline code
├── app/                # Streamlit web application
├── models/             # Saved vector database (auto-generated)
├── docs/               # Project documentation
├── results/            # Evaluation results
├── tests/              # Test cases
├── requirements.txt
└── README.md
```

## Evaluation

See `results/` for retrieval accuracy and answer correctness testing against
a set of sample questions.
