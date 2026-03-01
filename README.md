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
- **LLM:** Groq (cloud) / Ollama (local)
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

## 📄 License

MIT License

---

Built by **Akshay** 🚀
