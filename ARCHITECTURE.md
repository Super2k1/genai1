# CV RAG Agent - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                         │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │ Interactive CLI  │              │  Programmatic    │             │
│  │ (interactive_    │              │  API (rag_       │             │
│  │  rag.py)         │              │  agent.py)       │             │
│  └──────────────────┘              └──────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      RAG Agent Core (rag_agent.py)                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐        ┌──────────────────┐                  │
│  │  Document       │        │   Text           │                  │
│  │  Loading        │   →    │   Chunking       │                  │
│  │  (MarkItDown)   │        │   (LangChain)    │                  │
│  └─────────────────┘        └──────────────────┘                  │
│         ↓                             ↓                            │
│    PDF/DOCX Files         Semantic Chunks with                     │
│    (cv/ folder)           Metadata & Indices                       │
│                                 ↓                                  │
│                        ┌──────────────────┐                        │
│                        │  Embeddings      │                        │
│                        │  Generation      │                        │
│                        │  (Google AI)     │                        │
│                        └──────────────────┘                        │
│                                 ↓                                  │
│                        Vector Embeddings                           │
│                        (768 dimensions)                            │
│                                 ↓                                  │
│                        ┌──────────────────┐                        │
│                        │  Vector Store    │                        │
│                        │  (FAISS)         │                        │
│                        └──────────────────┘                        │
│                                 ↓                                  │
│                     Persistent Vector DB                           │
│                   (cv_vector_store/ folder)                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
                        (Query Time: Retrieval + Generation)
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Retrieval & Generation Pipeline                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User Query                                                         │
│     ↓                                                               │
│  ┌──────────────────┐                                              │
│  │  Embed Query     │  (Using same Google AI embeddings)           │
│  │  (Google AI)     │                                              │
│  └──────────────────┘                                              │
│     ↓                                                               │
│  ┌──────────────────┐                                              │
│  │  FAISS Similarity│  (Top-4 similar chunks)                      │
│  │  Search          │                                              │
│  └──────────────────┘                                              │
│     ↓                                                               │
│  ┌──────────────────┐                                              │
│  │  Format Context  │  (Combine chunks with metadata)              │
│  │  (with citations)│                                              │
│  └──────────────────┘                                              │
│     ↓                                                               │
│  ┌──────────────────────────────────────┐                          │
│  │  LLM Generation                      │                          │
│  │  (Google Gemini Pro)                 │                          │
│  │  Input: Query + Context              │                          │
│  │  Output: Answer with Citations       │                          │
│  └──────────────────────────────────────┘                          │
│     ↓                                                               │
│  Response with Sources                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Document Loading (MarkItDown Integration)

**Purpose**: Convert PDF/DOCX to clean, structured text

**Process**:
```
PDF/DOCX File
    ↓
MarkItDown Parser
    ↓
Markdown-formatted Text
    ├─ Headers preserved
    ├─ Lists formatted
    ├─ Tables converted
    └─ Structure maintained
    ↓
Document Objects
    ├─ page_content (text)
    └─ metadata (filename, type, path)
```

**Supported Formats**:
- `.pdf` - PDF documents
- `.docx` - Microsoft Word (modern)
- `.doc` - Microsoft Word (legacy)

**Key Features**:
- Preserves document structure
- Removes noise and formatting artifacts
- Maintains semantic information
- Efficient batch processing

### 2. Text Splitting (RecursiveCharacterTextSplitter)

**Purpose**: Break documents into manageable, semantically coherent chunks

**Configuration**:
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,          # Max characters per chunk
    chunk_overlap=200,        # Overlap for context continuity
    separators=                # Priority order:
        ["\n\n",              # 1. Paragraph breaks
         "\n",                # 2. Line breaks
         " ",                 # 3. Space
         ""]                  # 4. Character (fallback)
    add_start_index=True      # Track position in original
)
```

**Output Structure**:
```
Original Document (43KB)
    ↓
Split into Chunks
    ├─ Chunk 1: 1000 chars, starts at index 0
    ├─ Chunk 2: 950 chars, starts at index 800
    ├─ Chunk 3: 1000 chars, starts at index 1750
    └─ ... (66 total chunks for example doc)
```

**Benefits**:
- Respects paragraph boundaries
- Maintains context with overlap
- Tracks position for reference
- Semantically coherent chunks

### 3. Embedding Generation (Google AI)

**Model**: `models/embedding-001`

**Specifications**:
- Dimension: 768
- Input: Text chunk (up to ~2000 tokens)
- Output: 768-dimensional vector
- Semantic similarity based

**Process**:
```
Text Chunk
    ↓
Google Embedding API
    ↓
768-D Vector
[0.234, -0.156, 0.891, ..., 0.421]
```

**Characteristics**:
- Semantic understanding of content
- Similar meaning = close vectors
- Used for similarity search
- Deterministic (same input = same output)

### 4. Vector Store (FAISS)

**Technology**: Facebook AI Similarity Search

**Architecture**:
```
FAISS Index
├─ Vector Database (index.faiss)
│  ├─ Flat index with ~1000s vectors
│  ├─ L2 distance metric
│  └─ Optimized for search speed
└─ Metadata Store (index.pkl)
   ├─ Document references
   ├─ Source information
   └─ Chunk indices
```

**Operations**:
```
Add Documents
  ↓
Vectorize & Store
  ↓
Create Index
  ↓
Persist to Disk

Query
  ↓
Embed Query
  ↓
Search Index (k=4)
  ↓
Return Top Similar
```

**Performance**:
- Add: O(n) for n documents
- Query: O(log n) search time
- Memory: ~100MB per ~50 CVs
- Disk: Similar to memory

### 5. Retrieval & Generation Pipeline

**Flow**:
```
User Query: "What programming skills are mentioned?"
    ↓
Step 1: Embed Query
    ├─ Convert to 768-D vector
    └─ Use same embedding model
    ↓
Step 2: Search Vector Store
    ├─ Find 4 most similar chunks
    ├─ Score by cosine similarity
    └─ Retrieve full documents
    ↓
Step 3: Format Context
    ├─ Combine chunks
    ├─ Add source citations
    ├─ Create formatted text
    └─ Pass to LLM
    ↓
Step 4: Generate Answer
    ├─ LLM: Gemini Pro
    ├─ Temp: 0.7 (balanced)
    ├─ Context-aware response
    └─ Include citations
    ↓
Step 5: Return Result
    └─ Answer with sources
```

**Context Window**:
```
[System Prompt: COSTAR Framework]
[Retrieved Context: ~4KB]
[User Query: ~100 bytes]
[Total: ~5KB << Model's 30KB limit]
```

### 6. COSTAR Framework Implementation

**COSTAR Application**:

```
Context
├─ CV documents in the knowledge base
├─ Professional background information
└─ Interview/hiring context

Objective
├─ Accurately identify relevant information
├─ Answer specific questions
└─ Provide evidence-based responses

Style
├─ Professional tone
├─ Structured format
├─ Clear presentation

Tone
├─ Helpful and supportive
├─ Impartial and objective
└─ Informative

Audience
├─ HR professionals
├─ Recruiters
└─ Hiring managers

Response
├─ Detailed answers
├─ With citations
├─ Backed by content
└─ Actionable insights
```

**System Prompt Integration**:
```python
system_prompt = """
You are a professional CV Analyst assistant...
[COSTAR guidelines embedded]
Use the retrieve_cv_context tool to find information
Always cite sources
Be objective and factual
"""
```

## Data Flow Diagrams

### Indexing Phase (Offline)

```
cv/ folder
├─ CV1.pdf (43KB)
├─ CV2.docx (38KB)
└─ CV3.pdf (52KB)
    ↓
[MarkItDown Conversion]
    ↓
Documents Collection (3 items)
├─ Doc1: "LLM Powered Autonomous Agents..." (43K chars)
├─ Doc2: "Agent System Overview..." (38K chars)
└─ Doc3: "Building Agents..." (52K chars)
    ↓
[Text Splitting]
    ↓
Chunks Collection (66 items)
├─ Chunk 1: 1000 chars
├─ Chunk 2: 950 chars
├─ ...
└─ Chunk 66: 850 chars
    ↓
[Embedding Generation]
    ↓
Vector Collection (66 items × 768D)
    ↓
[FAISS Indexing]
    ↓
cv_vector_store/
├─ index.faiss (binary vectors)
└─ index.pkl (metadata)
```

### Query Phase (Online)

```
User Input: "What are the main technical skills?"
    ↓
[Embedding]
    ↓
Query Vector (768D)
    ↓
[FAISS Search - Top 4]
    ↓
Retrieved Chunks (4)
├─ Chunk 15: "Python, Machine Learning..."
├─ Chunk 23: "Data Analysis, SQL..."
├─ Chunk 31: "Cloud Computing, AWS..."
└─ Chunk 45: "DevOps, Kubernetes..."
    ↓
[Format with Citations]
    ↓
Context Package:
"Source: CV1.pdf
Content: Python, Machine Learning...

Source: CV2.docx
Content: Data Analysis, SQL..."
    ↓
[Gemini Pro Generation]
    ↓
Response: "Based on the CVs:
- Python (mentioned in CV1.pdf)
- Machine Learning (mentioned in CV1.pdf)
- Data Analysis (mentioned in CV2.docx)
..."
    ↓
User Output
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Document Conversion | MarkItDown | PDF/DOCX → Markdown |
| Text Splitting | LangChain | Semantic chunking |
| Embeddings | Google AI | Vector generation |
| Vector Store | FAISS | Similarity search |
| LLM | Google Gemini Pro | Answer generation |
| Orchestration | LangChain Agents | Tool management |
| Framework | Python 3.10+ | Core language |

## Performance Characteristics

### Indexing Time (Per 100 CVs ~5MB)

```
Document Loading:    ~5-10 seconds
Text Splitting:      ~2-3 seconds
Embedding Gen:       ~30-60 seconds (API calls)
Vector Indexing:     ~2-5 seconds
Total:              ~40-80 seconds
```

### Query Time (Per Question)

```
Query Embedding:     ~200-500ms
Vector Search:       ~5-20ms
Context Formatting:  ~10-50ms
LLM Generation:      ~3-8 seconds
Total:              ~3.5-9 seconds
```

### Storage Requirements

```
Per CV Document:     ~100KB (markdown)
Per Embedding:       ~4KB (768 dims × 4 bytes)
Per 50 CVs:          ~200MB (FAISS + metadata)
Expansion Factor:    ~4-5x original document size
```

## Error Handling & Resilience

```
Error Scenarios:

1. Document Loading Errors
   ├─ Corrupted PDF/DOCX
   ├─ Unreadable file
   └─ → Skip file, log error, continue

2. Embedding Generation Errors
   ├─ API rate limit
   ├─ Network timeout
   └─ → Retry logic, exponential backoff

3. Vector Store Errors
   ├─ Corrupted index
   ├─ Disk space full
   └─ → Rebuild option, graceful fallback

4. Query Processing Errors
   ├─ Empty vector store
   ├─ No similar chunks
   └─ → Inform user, suggest retry
```

## Configuration Parameters

### Text Splitting

```python
chunk_size = 1000              # Optimal for embeddings
chunk_overlap = 200            # 20% overlap for context
separators = ["\n\n", "\n", " ", ""]  # Hierarchy
```

### Retrieval

```python
k = 4                          # Top-4 similar chunks
score_threshold = None         # Return all with >score
```

### LLM

```python
model = "gemini-pro"           # Latest stable model
temperature = 0.7             # Balanced creativity
max_tokens = 2048             # Response length
```

## Scalability Considerations

### Current Limits
- Max CVs: ~1000 (manageable on laptop)
- Max query latency: 10 seconds
- Memory usage: ~500MB-1GB

### For Scaling
- Use GPU for embeddings
- Implement batching for indexing
- Consider distributed FAISS
- Add caching layer
- Implement result pagination

## Security Considerations

```
Data Handling:
├─ API keys → .env file
├─ Documents → Local storage
├─ Embeddings → FAISS (local)
└─ No external transmission

Best Practices:
├─ Use .gitignore for .env
├─ Restrict .env permissions
├─ Don't log sensitive data
└─ Validate user inputs
```

---

**Last Updated**: November 21, 2025
**Version**: 1.0.0
