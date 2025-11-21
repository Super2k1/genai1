# Quick Start Guide - CV RAG Agent

## 5-Minute Setup

### 1. Verify Installation ✓
```powershell
cd c:\Users\lilia\OneDrive\Desktop\googelaistudio

# Check if dependencies are installed
pip list | grep -E "langchain|faiss|markitdown|google"
```

### 2. Prepare Your CVs ✓
- Create a folder named `cv` in your project root (if it doesn't exist)
- Place your PDF and DOCX CV documents in this folder
- The system supports: `.pdf`, `.docx`, `.doc`

```powershell
# Example folder structure
googelaistudio/
├── cv/
│   ├── John_Doe_CV.pdf
│   ├── Jane_Smith_CV.docx
│   └── Bob_Johnson_CV.pdf
```

### 3. Configure API Key ✓
Ensure your `.env` file contains:
```
GOOGLE_API_KEY=your_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikeys

### 4. Choose Your Interface

#### Option A: Interactive CLI (Recommended for beginners)
```powershell
python interactive_rag.py
```

Features:
- User-friendly menu
- Ask questions in natural language
- View loaded documents
- Example queries included

#### Option B: Examples Script
```powershell
python examples.py
```

Features:
- 7 different usage examples
- Document inspection
- Chunking analysis
- Error handling demonstration

#### Option C: Direct Python Usage
```powershell
python
```

```python
from rag_agent import CVRAGAgent

# Create and initialize agent
agent = CVRAGAgent()
agent.initialize_pipeline()

# Ask a question
result = agent.query("What programming skills are mentioned?")
print(result)
```

## Common Tasks

### Load documents and check what was loaded
```powershell
python examples.py
# Select option 2: Document Inspection
```

### Ask your first question
```powershell
python interactive_rag.py
# Select option 1: Ask a question about CVs
```

### See how text is split into chunks
```powershell
python examples.py
# Select option 3: Chunking Analysis
```

### Rebuild the vector store after adding new CVs
```powershell
python interactive_rag.py
# Select option 2: Reinitialize with new documents
# Choose 'y' for rebuild
```

### Process multiple queries at once
```powershell
python examples.py
# Select option 5: Multiple Related Queries
```

## Example Queries to Try

```
1. "What are the main technical skills mentioned in these CVs?"

2. "Which candidates have experience with Python and machine learning?"

3. "Summarize the educational background of all candidates"

4. "What certifications or special achievements are mentioned?"

5. "List the most common job titles or roles in these CVs"

6. "What are the key differences in experience levels?"

7. "Identify any relevant soft skills mentioned"

8. "Which candidates have international experience?"
```

## Understanding the Process

```
Your Question
    ↓
Convert to Embedding (Google AI)
    ↓
Search FAISS Vector Store
    ↓
Retrieve Top 4 Similar Chunks
    ↓
Pass to Google Gemini LLM
    ↓
Generate Answer with Citations
    ↓
Display Response
```

## File Structure After Setup

```
googelaistudio/
├── rag_agent.py              # Main RAG system
├── interactive_rag.py        # Interactive interface
├── examples.py               # Usage examples
├── README_RAG.md            # Full documentation
├── cv/                       # Your CV documents
│   ├── CV1.pdf
│   ├── CV2.docx
│   └── ...
├── cv_vector_store/          # Auto-created vector store
│   ├── index.faiss
│   └── index.pkl
└── .env                      # Your API key
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'faiss'"
```powershell
pip install faiss-cpu
```

### "GOOGLE_API_KEY not found"
1. Ensure `.env` file exists in project root
2. Add: `GOOGLE_API_KEY=your_key_here`
3. Restart your terminal/IDE

### "No documents loaded from cv folder"
1. Check that `cv/` folder exists
2. Add some PDF or DOCX files to it
3. Ensure files are readable and not corrupted

### "Vector store not found"
- Delete `cv_vector_store/` folder
- Run `python interactive_rag.py`
- Choose option 2 to rebuild
- Choose 'y' for rebuild

### "Poor quality answers"
1. Ensure your CV documents are readable and well-formatted
2. Use more specific questions
3. Try increasing chunk size for more context
4. Verify documents have meaningful content

## Performance Tips

1. **First run**: May take longer (generating embeddings)
2. **Subsequent runs**: Faster (loads existing vector store)
3. **Large document sets**: Consider breaking into batches
4. **Memory usage**: Depends on number of documents (~100MB per ~50 CVs)

## Next Steps

1. ✓ Try the interactive CLI
2. ✓ Ask your first question
3. ✓ Review the full README_RAG.md for advanced features
4. ✓ Customize parameters for your use case
5. ✓ Integrate into your workflow

## Support & Documentation

- **Full Documentation**: See `README_RAG.md`
- **Concept Documentation**: 
  - `docs/rag.md` - RAG concepts
  - `docs/markitdown_docs.md` - Document conversion
  - `docs/recursive character splitter.md` - Text splitting

## Key Features

✓ Supports PDF, DOCX documents
✓ Automatic text extraction with structure preservation
✓ Semantic chunking for better results
✓ Google AI embeddings for accuracy
✓ FAISS for fast retrieval
✓ LLM-powered answer generation
✓ Source citations
✓ Persistent vector store
✓ Detailed logging
✓ Error handling

---

**Ready?** Start with: `python interactive_rag.py`

Good luck! 🚀
