# SentraShield QA Tool

An AI-powered questionnaire answering system that uses Retrieval-Augmented Generation (RAG) to automatically answer security questionnaires based on your reference documents.

## 🚀 Live Demo

[**https://alamabase-rcxtn2ssb4vuwqf2zbjpza.streamlit.app/**](https://alamabase-rcxtn2ssb4vuwqf2zbjpza.streamlit.app/)

Click **"Demo Login"** button on the login page - no credentials needed!

## 📝 Note

For full source code and deployment instructions, check the GitHub repo: https://github.com/Akshay-17-git/alambase

## 📋 Sample Documents

Download sample documents from the `sample_docs/` folder in the repository:
- **Security_Questionnaire.pdf** - Sample questionnaire to test
- **Authentication_Documentation.pdf** - Reference doc
- **Compliance_Statement.pdf** - Reference doc
- **Incident_Response_Plan.pdf** - Reference doc
- **Infrastructure_Overview.pdf** - Reference doc
- **Security_Policy.pdf** - Reference doc

## 📋 Features

| Feature | Description |
|---------|-------------|
| **User Authentication** | Secure login/signup with SQLite database |
| **Multi-format Support** | Parse PDFs, TXT, and DOCX documents |
| **RAG-powered Answers** | Generate accurate answers with citations from reference docs |
| **Confidence Scoring** | View confidence scores for each answer |
| **Review & Edit** | Manually edit AI-generated answers before export |
| **DOCX Export** | Export completed questionnaires to Word documents |

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Database:** SQLite
- **Vector Search:** FAISS (Facebook AI Similarity Search)
- **LLM:** Groq (cloud)
- **Embeddings:** Sentence-Transformers

## 📦 Deployment

### Streamlit Cloud (Recommended)

1. Deploy to [Streamlit Cloud](https://share.streamlit.io)
2. Add your Groq API key in **App Settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"
```

Get free API key: https://console.groq.com/keys

### Local Development

```bash
# Clone the repository
git clone https://github.com/Akshay-17-git/alamabase.git
cd alamabase

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📁 Project Structure

```
├── app.py          # Main Streamlit application
├── auth.py         # Authentication module
├── db.py           # SQLite database operations
├── parser.py       # Document parsing (PDF, TXT, DOCX)
├── embedder.py     # FAISS vector indexing
├── rag.py          # RAG answer generation
├── exporter.py     # DOCX export functionality
└── requirements.txt
```

## 🔑 Demo Account

The live demo has a built-in demo account. Simply click the **Demo Login** button on the login page to explore the app without registration.

## 📖 How to Use

### 1. How to Install Dependencies

Install all required Python packages from requirements.txt:

```bash
pip install -r requirements.txt
```

Required packages include:
- streamlit - Web framework
- faiss-cpu - Vector similarity search
- sentence-transformers - Text embeddings
- groq - Cloud LLM API
- python-docx - Word document export
- PyPDF2, pdfplumber - PDF parsing
- python-dotenv - Environment variables

### 2. How to Run Locally

```bash
# Clone the repository
git clone https://github.com/Akshay-17-git/alambase.git
cd alambase

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with your Groq API key:
# GROQ_API_KEY=your_api_key_here

# Run the Streamlit app
streamlit run app.py
```

The app will open at http://localhost:8501

### 3. How to Setup SQLite Database

The database is automatically created on first run. To reset:

```bash
# Delete existing database
rm database.db

# Run the app - it will create a new database with:
# - Demo user account (demouser / demopass)
# - Required tables for users and answers
streamlit run app.py
```

### 4. How to Upload Documents & Questionnaire

1. **Login** - Use demo credentials (demouser/demopass) or click "Demo Login"
2. **Upload Reference Documents** - Go to "Upload Docs" tab and upload:
   - PDF files (.pdf)
   - Text files (.txt)
   - Word documents (.docx)
3. **Upload Questionnaire** - Go to "Upload Questionnaire" tab and upload your security questionnaire (PDF or TXT)
4. **Generate Answers** - Click "Generate Answers" to auto-answer questions using RAG

### 5. Expected Output

The system will generate:
- **AI-generated answers** with relevant citations from your uploaded documents
- **Confidence scores** (0-100%) indicating answer quality
- **Evidence snippets** showing which document sections were used
- **Exportable DOCX file** with all answers for submission

Example output format:
```
Question: How do you handle data encryption?
Answer: We use AES-256 encryption for all data at rest...
Confidence: 85%
Source: Security_Policy.pdf (Page 3)
```

### 6. Known Limitations

- **PDF parsing quality** - Complex PDFs with images/tables may not parse correctly
- **Context window** - LLM has limited context; very long documents may be truncated
- **Answer accuracy** - AI may generate incorrect answers; always review before submission
- **No multi-user sync** - Each user has isolated document storage (FAISS index per user)
- **Ollama speed** - Local LLM is slower than Groq cloud API
- **No web scraping** - Must manually upload all reference documents

### 7. Future Improvements

- [ ] Add support for more file formats (Excel, CSV, HTML)
- [ ] Implement web scraping for automatic reference document collection
- [ ] Add team collaboration features with shared document libraries
- [ ] Improve PDF parsing with OCR for scanned documents
- [ ] Add answer history and versioning
- [ ] Implement custom LLM model selection
- [ ] Add more detailed analytics dashboard
- [ ] Support for batch questionnaire processing

## 📄 License

MIT License

---

Built by **Akshay** 🚀
