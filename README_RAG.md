# CV RAG Agent

A professional Retrieval Augmented Generation (RAG) system for analyzing CV documents using LangChain, Google AI, MarkItDown, and FAISS.

## Overview

This project implements a sophisticated RAG agent that:

1. **Loads Documents**: Extracts text from PDF and DOCX files in the `cv/` folder using MarkItDown
2. **Processes Text**: Splits documents into semantic chunks using LangChain's `RecursiveCharacterTextSplitter`
3. **Generates Embeddings**: Creates vector embeddings using Google's AI embedding model
4. **Stores Vectors**: Saves embeddings in a FAISS vector store for efficient retrieval
5. **Answers Questions**: Uses the LLM to generate context-aware answers based on retrieved CV data

### COSTAR Framework Application

This agent follows the COSTAR framework for optimal performance:

- **Context**: CV documents and professional background information
- **Objective**: Accurately answer questions about candidate qualifications and experience
- **Style**: Professional, structured, and clear communication
- **Tone**: Helpful, impartial, and informative
- **Audience**: HR professionals, recruiters, and hiring managers
- **Response**: Detailed, evidence-based answers with citations

## Project Structure

```
googelaistudio/
├── rag_agent.py              # Core RAG agent implementation
├── interactive_rag.py        # Interactive CLI interface
├── cv/                       # Input folder for CV documents (PDF/DOCX)
├── cv_vector_store/          # FAISS vector store (auto-generated)
├── docs/
│   ├── rag.md               # RAG concepts documentation
│   ├── markitdown_docs.md   # MarkItDown documentation
│   └── recursive character splitter.md  # Text splitting documentation
├── requiments.txt           # Python dependencies
└── .env                     # Environment variables (GOOGLE_API_KEY)
```

## Installation

### Prerequisites

- Python 3.10+
- Google AI API key (from https://makersuite.google.com/app/apikeys)

### Setup Steps

1. **Create Virtual Environment** (Optional but recommended):
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. **Install Dependencies**:
```powershell
pip install -r requiments.txt
pip install faiss-cpu langchain-community
```

3. **Configure Environment**:
Create or update `.env` file with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

4. **Prepare CV Documents**:
Place your PDF and DOCX documents in the `cv/` folder.

## Usage

### Interactive CLI Mode (Recommended)

Run the interactive interface:

```powershell
python interactive_rag.py
```

This provides a user-friendly menu to:
- Ask questions about CVs
- View loaded documents
- See example queries
- Reinitialize with new documents

### Programmatic Usage

Use the `CVRAGAgent` class directly in your code:

```python
from rag_agent import CVRAGAgent

# Initialize the agent
agent = CVRAGAgent(cv_folder="cv", chunk_size=1000, chunk_overlap=200)

# Initialize the RAG pipeline
if agent.initialize_pipeline(rebuild=False):
    # Query the agent
    result = agent.query("What are the main skills in these CVs?")
    print(result)
```

### Batch Processing

Process multiple queries:

```python
from rag_agent import CVRAGAgent

agent = CVRAGAgent()
agent.initialize_pipeline()

queries = [
    "What programming languages are mentioned?",
    "Summarize the educational backgrounds",
    "List key technical skills"
]

for query in queries:
    print(f"\nQuery: {query}")
    result = agent.query(query)
    print(f"Answer: {result}")
```

## Configuration

### CVRAGAgent Parameters

```python
CVRAGAgent(
    cv_folder="cv",              # Folder containing CV documents
    chunk_size=1000,             # Characters per chunk
    chunk_overlap=200,           # Overlap between chunks
    vector_store_path="cv_vector_store"  # Where to save FAISS store
)
```

### Text Splitting Strategy

The agent uses `RecursiveCharacterTextSplitter` with these separators (in order):
1. Double newlines (`\n\n`)
2. Single newlines (`\n`)
3. Spaces (` `)
4. Characters (fallback)

This preserves paragraph structure while ensuring reasonable chunk sizes.

## How It Works

### 1. Document Loading

- Scans `cv/` folder for `.pdf`, `.docx`, and `.doc` files
- Uses MarkItDown to convert documents to clean Markdown text
- Preserves document structure (headers, lists, tables)
- Stores metadata (filename, file type, path)

### 2. Text Chunking

- Splits documents into overlapping chunks
- Default: 1000 characters with 200-character overlap
- Maintains semantic boundaries (paragraphs before sentences)
- Adds index information for context tracking

### 3. Embedding Generation

- Uses Google's `embedding-001` model
- Converts text chunks to 768-dimensional vectors
- Efficient semantic similarity matching

### 4. Vector Storage

- Stores embeddings in FAISS (Facebook AI Similarity Search)
- Supports fast similarity search
- Persists to disk for reuse
- Allows incremental updates

### 5. Retrieval & Generation

- Converts user query to embedding
- Searches FAISS for top-4 similar chunks
- Passes retrieved context to Google Gemini Pro LLM
- Generates context-aware response with source citations

## Example Queries

```
"What are the main technical skills mentioned in the CVs?"
"Which candidates have experience with data science?"
"What programming languages are used?"
"Summarize the educational backgrounds"
"List key achievements or awards mentioned"
"What are the most common job titles?"
"Which candidates have international experience?"
```

## Advanced Features

### Rebuild Vector Store

To rebuild the vector store with new documents:

```python
agent = CVRAGAgent()
agent.initialize_pipeline(rebuild=True)
```

### Manual Document Processing

```python
# Load documents
docs = agent.load_documents()

# Create chunks
chunks = agent.chunk_documents(docs)

# Create vector store
agent.create_vector_store(chunks)

# Save for later use
agent.save_vector_store()
```

### Load Existing Vector Store

```python
agent = CVRAGAgent()
if agent.load_vector_store():
    print("Vector store loaded successfully")
    result = agent.query("Your question here")
```

## Logging

The system provides detailed logging:

```python
import logging

# Configure logging level
logging.getLogger("rag_agent").setLevel(logging.DEBUG)
```

Logs include:
- Document loading progress
- Chunking statistics
- Embedding generation
- Query retrieval
- Processing time and errors

## Performance Optimization

### Tips for Better Results

1. **Chunk Size**: Increase for broader context, decrease for precision
2. **Chunk Overlap**: Higher overlap captures more context but uses more storage
3. **Number of Retrieved Documents**: Adjust `k` parameter in similarity_search (default: 4)
4. **Prompt Tuning**: Customize the system prompt in `setup_agent()` method

### Memory Management

- FAISS stores vectors in memory by default
- For large document collections, consider using FAISS with disk-based indices
- Vector store is persisted locally for fast reloading

## Troubleshooting

### "GOOGLE_API_KEY not found"
- Ensure `.env` file exists in the project root
- Check that `GOOGLE_API_KEY` is correctly set
- Restart Python process after updating `.env`

### No documents loaded
- Verify `cv/` folder exists and contains PDF/DOCX files
- Check file permissions
- Ensure MarkItDown can read the files

### Vector store errors
- Delete `cv_vector_store/` folder to force rebuild
- Check disk space availability
- Verify FAISS installation: `pip install --upgrade faiss-cpu`

### Poor response quality
- Increase number of retrieved documents (change `k` in `similarity_search`)
- Adjust chunk size and overlap
- Ensure document quality and clarity
- Add more specific context in queries

## Dependencies

Key packages used:

- **langchain**: Orchestration and chaining
- **langchain-google-genai**: Google AI integration
- **langchain-community**: Additional components
- **markitdown**: Document conversion
- **faiss-cpu**: Vector similarity search
- **python-dotenv**: Environment variable management

See `requiments.txt` for complete list.

## API Reference

### CVRAGAgent Class

#### Methods

- `load_documents()` → List[Document]
- `chunk_documents(documents)` → List[Document]
- `create_vector_store(chunks)` → FAISS
- `save_vector_store()`
- `load_vector_store()` → bool
- `initialize_pipeline(rebuild)` → bool
- `query(question)` → str
- `create_retrieval_tool()` → callable
- `setup_agent()` → AgentExecutor

### InteractiveCVRAG Class

#### Methods

- `initialize(rebuild)`
- `ask_question()`
- `view_documents()`
- `show_examples()`
- `run()`

## Future Enhancements

Potential improvements:

- [ ] Web UI with Streamlit
- [ ] Multi-language support
- [ ] Document tagging and filtering
- [ ] Advanced search with filters
- [ ] Batch analysis and reporting
- [ ] Integration with ATS systems
- [ ] Performance metrics dashboard
- [ ] Custom prompt templates
- [ ] Question history and analytics

## License

This project is provided as-is for educational and professional use.

## Support

For issues, questions, or suggestions:
1. Check the troubleshooting section
2. Review the logs for detailed error messages
3. Verify all dependencies are correctly installed
4. Ensure Google API key is valid and has proper permissions

---

**Last Updated**: November 21, 2025
**Version**: 1.0.0
