# University FAQ Chatbot

A chatbot that answers student questions about the BIT program's admissions,
fees, courses and campus facilities using Retrieval-Augmented Generation.
It keeps a persistent chat log and collects user feedback on each answer.

## How it works

1. University FAQ documents in PDF form are split into chunks based on each
   question-and-answer pair, so each chunk contains one complete,
   self-contained piece of information.
2. Each chunk is converted into an embedding using Google's Gemini
   embedding model.
3. Embeddings are stored in a vector database using ChromaDB.
4. When a student asks a question, the system finds the most relevant
   chunks by comparing the question's embedding to the stored chunk
   embeddings.
5. The relevant chunks are passed to Gemini along with the question, and
   Gemini generates an answer grounded in that information to reduce
   made-up answers. If the answer can't be found, the chatbot says so and
   suggests rephrasing rather than guessing.
6. The app displays the answer along with the source text it was based on.
7. Every question, answer and source is logged to a SQLite database, along
   with optional user feedback marking each answer helpful or not helpful.
8. If the Gemini API is temporarily unavailable, the app automatically
   retries a couple of times before showing a friendly error message.

## Tech Stack

- **Language:** Python
- **LLM and Embeddings:** Google Gemini API
- **Vector Database:** ChromaDB
- **Relational Database:** SQLite for chat history and feedback logging
- **Frontend:** Streamlit
- **PDF Parsing:** pdfplumber

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
4. Build the knowledge base. Run this once, or whenever the FAQ document
   changes:
   ```
   cd src
   python build_knowledge_base.py
   ```
5. Run the app:
   ```
   cd ../app
   streamlit run app.py
   ```
6. Open the local URL shown in your terminal, usually http://localhost:8501

## Running Tests

Unit tests check that the document chunking logic works correctly:
```
python tests/test_rag_pipeline.py
```

## Viewing Chat History

To review everything logged in the database, including questions, answers,
sources and feedback:
```
cd src
python view_history.py
```

## Project Structure

```
university-faq-chatbot/
├── data/               # Source FAQ document in PDF form
├── src/                # Core RAG pipeline, database and utility scripts
├── app/                # Streamlit web application
├── models/             # Saved vector database and chat history, auto-generated
├── docs/               # Database ERD and supporting documentation
├── results/            # Evaluation test questions and outcomes
├── tests/              # Unit tests
├── requirements.txt
├── LICENSE
└── README.md
```

## Evaluation

See `results/` for the full test question set and evaluation results,
covering 27 test questions across direct queries, reworded phrasing and
out-of-scope refusals.
