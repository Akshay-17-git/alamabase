# 🛡️ SentraShield QA Tool

An AI-powered security questionnaire answering tool built with Streamlit, Ollama (local LLM), and FAISS vector search. This application uses Retrieval-Augmented Generation (RAG) to automatically answer security questionnaires based on your reference documentation.

**100% Free** - Uses local models (no API costs!)

## Features

- **User Authentication**: Secure login/signup with SQLite database
- **Multi-format Support**: Parse PDFs, TXT, and DOCX reference documents
- **RAG-powered Answers**: Generate accurate answers using semantic search + local Ollama LLM
- **User Isolation**: Each user has their own FAISS vector index (namespace support)
- **Review & Edit**: Manually edit generated answers before export
- **DOCX Export**: Export completed questionnaires to professional Word documents
- **Confidence Scoring**: See confidence scores for each answer

## Architecture

```
sentrashield-qa-tool/
├── app.py              # Main Streamlit application
├── auth.py             # Login/signup logic
├── db.py               # SQLite database setup + queries
├── parser.py           # Questionnaire + PDF parsing
├── embedder.py         # Chunking + FAISS vector indexing
├── rag.py              # Retrieval + answer generation
├── exporter.py         # DOCX export functionality
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── .streamlit/         # Streamlit configuration
```

### Technology Stack

- **Frontend**: Streamlit
- **Database**: SQLite
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **LLM**: Ollama (local, free)
- **Embeddings**: Sentence-Transformers (local, free)
- **PDF Parsing**: pdfplumber

## Prerequisites

1. **Install Ollama** (for local LLM):
   ```bash
   # macOS/Linux
   brew install ollama
   
   # Windows: Download from https://ollama.ai
   ```

2. **Download an LLM model**:
   ```bash
   ollama pull llama3    # Recommended (requires ~4GB)
   # Or: ollama pull mistral
   # Or: ollama pull phi
   ```

3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd sentrashield-qa-tool
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## How to Use

### Step 1: Sign Up / Log In
- Create an account with your email and password
- Each user has isolated access to their own data and knowledge base

### Step 2: Build Knowledge Base
- Upload reference documents (PDF, TXT, or DOCX)
- Click "Build Knowledge Base" to process and index documents
- The system uses sentence-transformers to create embeddings

### Step 3: Upload Questionnaire
- Upload a security questionnaire in PDF format
- Click "Generate Answers" to start AI processing

### Step 4: Review & Edit
- Navigate to the Review tab
- Click on each question to view and edit the answer
- Save your changes

### Step 5: Export
- Navigate to the Export tab
- Download as DOCX or CSV format

## Important Notes

### Ollama Not Running?
If you see "Ollama is not running", make sure:
1. Ollama is installed: `brew install ollama` (macOS) or download from ollama.ai (Windows)
2. Ollama server is running: `ollama serve`
3. Model is downloaded: `ollama pull llama3`

### First Run
On first run, sentence-transformers will download the embedding model (~90MB). This is a one-time download.

## What I'd Improve With More Time

1. **Better LLM**: Use a larger model like llama3:70b for better quality
2. **Multi-model Support**: Allow users to choose between different Ollama models
3. **Batch Processing**: Add async processing for multiple questionnaires
4. **Admin Dashboard**: View all users and manage questionnaires
5. **Version History**: Track changes to answers over time

## License

MIT License
