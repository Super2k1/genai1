# CV RAG Agent - Visual Process Flow & Diagrams

## Complete System Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    CV RAG AGENT - COMPLETE PIPELINE                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

INITIALIZATION PHASE (First Run)
═════════════════════════════════════════════════════════════════════════════

Step 1: DOCUMENT LOADING
┌───────────────────────────────────────────────────────────────┐
│ Input: cv/ folder with PDF, DOCX files                        │
│                                                               │
│ cv/                                                           │
│ ├─ CV1.pdf (John_Doe)                                        │
│ ├─ CV2.docx (Jane_Smith)                                     │
│ └─ CV3.pdf (Bob_Johnson)                                     │
│                                                               │
│ Process: MarkItDown Conversion                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ PDF → [Extraction] → [Cleanup] → Markdown Text       │  │
│ │ DOCX → [Parsing] → [Formatting] → Structured Text    │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Output: 3 Document Objects with metadata                     │
│ ├─ Doc1: 43K chars, source: CV1.pdf                         │
│ ├─ Doc2: 38K chars, source: CV2.docx                        │
│ └─ Doc3: 52K chars, source: CV3.pdf                         │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 2: TEXT CHUNKING
┌───────────────────────────────────────────────────────────────┐
│ Input: 3 documents (133K total chars)                         │
│                                                               │
│ Process: RecursiveCharacterTextSplitter                       │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Parameters:                                            │  │
│ │ • chunk_size: 1000 chars                               │  │
│ │ • chunk_overlap: 200 chars                             │  │
│ │ • separators: [\n\n, \n, space, char]                  │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Example Splitting:                                           │
│ Document: "Paragraph 1 content....\n\nParagraph 2..."      │
│                                                               │
│ Result:                                                      │
│ Chunk 1: [0-1000]     "Paragraph 1 content... [overlap]"   │
│ Chunk 2: [800-1800]   "[overlap] ...Paragraph 2 content" │
│ Chunk 3: [1600-2600]  "[overlap] ...Paragraph 3 content" │
│                                                               │
│ Output: 66 Chunks with metadata                              │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 3: EMBEDDING GENERATION
┌───────────────────────────────────────────────────────────────┐
│ Input: 66 text chunks                                         │
│                                                               │
│ Model: Google AI - embedding-001                             │
│ API: Batch processing with rate limiting                     │
│                                                               │
│ Process:                                                      │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Chunk 1: "Python, Machine Learning skills..."         │  │
│ │    ↓ [Google AI API]                                   │  │
│ │ Embedding: [0.234, -0.156, 0.891, ..., 0.421]         │  │
│ │ (768 dimensions)                                       │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Output: 66 vectors × 768 dimensions                          │
│ Storage: ~4KB per vector                                     │
│ Total: ~264KB for 66 embeddings                              │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 4: VECTOR STORE CREATION & INDEXING
┌───────────────────────────────────────────────────────────────┐
│ Input: 66 vectors + metadata                                  │
│                                                               │
│ Technology: FAISS (Facebook AI Similarity Search)            │
│                                                               │
│ Process:                                                      │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Vectors + Metadata                                     │  │
│ │    ↓                                                    │  │
│ │ Build FAISS Index                                      │  │
│ │    ↓                                                    │  │
│ │ Create Flat Index (L2 distance)                        │  │
│ │    ↓                                                    │  │
│ │ Save Index                                             │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Output Files:                                                │
│ cv_vector_store/                                             │
│ ├─ index.faiss (binary vector index)   ~264KB               │
│ └─ index.pkl (metadata & refs)         ~10KB                │
│                                                               │
│ Total Storage: ~280KB                                        │
└───────────────────────────────────────────────────────────────┘
                            ↓
            ✓ INITIALIZATION COMPLETE


QUERY PHASE (Each User Question)
═════════════════════════════════════════════════════════════════════════════

Step 5: QUERY EMBEDDING
┌───────────────────────────────────────────────────────────────┐
│ Input: User Query                                             │
│ "What programming skills are mentioned?"                     │
│                                                               │
│ Process:                                                      │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Query Text                                             │  │
│ │    ↓ [Google AI - same embeddings model]               │  │
│ │ Query Embedding: [0.156, -0.234, 0.567, ..., 0.789]   │  │
│ │ (768 dimensions)                                       │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Time: ~200-500ms                                             │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 6: VECTOR SIMILARITY SEARCH
┌───────────────────────────────────────────────────────────────┐
│ Input: Query embedding (768D vector)                          │
│ Store: FAISS index with 66 vectors                           │
│                                                               │
│ Process:                                                      │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Query Vector                                           │  │
│ │    ↓ [FAISS Similarity Search]                         │  │
│ │ Calculate distances to all 66 vectors                  │  │
│ │    ↓                                                    │  │
│ │ Sort by similarity (L2 distance)                       │  │
│ │    ↓                                                    │  │
│ │ Return Top 4 Results                                   │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Results:                                                      │
│ 1. Chunk 15: "Python, ML skills..." (similarity: 0.92)      │
│ 2. Chunk 23: "Data Analysis, SQL..." (similarity: 0.88)     │
│ 3. Chunk 31: "Cloud, AWS..." (similarity: 0.84)             │
│ 4. Chunk 45: "DevOps, Kubernetes..." (similarity: 0.81)     │
│                                                               │
│ Time: ~5-20ms                                                │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 7: CONTEXT FORMATTING
┌───────────────────────────────────────────────────────────────┐
│ Input: 4 retrieved chunks with metadata                       │
│                                                               │
│ Process:                                                      │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ For each chunk:                                        │  │
│ │ • Extract content                                      │  │
│ │ • Get source (filename)                                │  │
│ │ • Format with citations                                │  │
│ │ • Combine into context string                          │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Output Format:                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Source: CV1.pdf                                        │  │
│ │ Content: Python, Machine Learning, TensorFlow...      │  │
│ │                                                        │  │
│ │ Source: CV2.docx                                       │  │
│ │ Content: Data Analysis, SQL, Apache Spark...          │  │
│ │                                                        │  │
│ │ Source: CV3.pdf                                        │  │
│ │ Content: Cloud Computing, AWS, Kubernetes...          │  │
│ │                                                        │  │
│ │ Source: CV1.pdf                                        │  │
│ │ Content: DevOps, Docker, Jenkins...                   │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Time: ~10-50ms                                               │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 8: LLM GENERATION (Gemini Pro)
┌───────────────────────────────────────────────────────────────┐
│ Input Package:                                                │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ System Prompt (COSTAR Framework):                      │  │
│ │ "You are a professional CV Analyst...                  │  │
│ │  Use COSTAR framework...                               │  │
│ │  Always cite sources..."                               │  │
│ │                                                        │  │
│ │ Retrieved Context (4KB):                               │  │
│ │ "[Source: CV1.pdf]                                     │  │
│ │  Python, Machine Learning, TensorFlow...              │  │
│ │  [Source: CV2.docx]                                    │  │
│ │  Data Analysis, SQL, Apache Spark..."                 │  │
│ │                                                        │  │
│ │ User Query:                                            │  │
│ │ "What programming skills are mentioned?"              │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Model: Google Gemini Pro                                     │
│ Temperature: 0.7 (balanced)                                  │
│ Max Tokens: 2048                                             │
│                                                               │
│ Processing:                                                  │
│ System Prompt + Context + Query (Total: ~5KB)              │
│    ↓ [LLM Processing]                                       │
│ Generate Response (3-8 seconds)                             │
│                                                               │
│ Output Response:                                             │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ Based on the analyzed CVs, the main programming       │  │
│ │ skills mentioned are:                                 │  │
│ │                                                        │  │
│ │ • Python (mentioned in CV1.pdf)                        │  │
│ │ • Machine Learning/TensorFlow (mentioned in CV1.pdf)   │  │
│ │ • Data Analysis (mentioned in CV2.docx)                │  │
│ │ • SQL (mentioned in CV2.docx)                          │  │
│ │ • Cloud Computing - AWS (mentioned in CV3.pdf)         │  │
│ │ • DevOps tools - Docker, Jenkins (mentioned in        │  │
│ │   CV1.pdf)                                             │  │
│ │ • Apache Spark (mentioned in CV2.docx)                 │  │
│ │ • Kubernetes (mentioned in CV3.pdf)                    │  │
│ │                                                        │  │
│ │ These skills represent a strong foundation in full-    │  │
│ │ stack development with emphasis on data engineering    │  │
│ │ and cloud infrastructure.                              │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ Time: ~3-8 seconds                                           │
└───────────────────────────────────────────────────────────────┘
                            ↓


Step 9: OUTPUT DELIVERY
┌───────────────────────────────────────────────────────────────┐
│ Final Response Presented to User                              │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ ✓ Answer with source citations                        │  │
│ │ ✓ Contextual understanding demonstrated                │  │
│ │ ✓ Evidence-based information                           │  │
│ │ ✓ Professional formatting                              │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ User sees formatted answer                                   │
│ Can ask follow-up questions                                  │
│ System ready for next query                                  │
└───────────────────────────────────────────────────────────────┘
                            ↓
                    ✓ QUERY COMPLETE
                   Total Time: 3.5-9 sec


ARCHITECTURE SUMMARY
═════════════════════════════════════════════════════════════════════════════

Data Flow:
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   CVs    │──▶│MarkItDn  │──▶│ Chunking │──▶│ Google   │──▶│  FAISS   │
│(PDF,     │   │(Convert) │   │(LangChn) │   │   AI     │   │ (Store)  │
│ DOCX)    │   │          │   │          │   │(Embed)   │   │          │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                                                    │
                                                                    │
                                    Query ──────────────────────────┤
                                      │                             │
                                      ▼                             ▼
                                  ┌─────────┐              ┌──────────────┐
                                  │ Google  │              │ FAISS Search │
                                  │   AI    │──────────────▶│   (Find Top  │
                                  │Embedding│              │    4 Match)  │
                                  └─────────┘              └──────────────┘
                                                                    │
                                                                    │
                                  ┌─────────┐              ┌──────────────┐
                                  │ Context │◀─────────────│ Retrieved    │
                                  │Format.  │              │  Chunks      │
                                  └────┬────┘              └──────────────┘
                                       │
                                       ▼
                                  ┌─────────────────────┐
                                  │  Google Gemini Pro  │
                                  │   (LLM Generation)  │
                                  └────────┬────────────┘
                                           │
                                           ▼
                                  ┌─────────────────────┐
                                  │ Response with       │
                                  │ Source Citations    │
                                  └─────────────────────┘


PERFORMANCE PROFILE
═════════════════════════════════════════════════════════════════════════════

First Run (Cold Start):
┌─────────────────────────────┐
│ Document Loading   5-10 sec  │ ▓▓
│ Text Splitting     2-3 sec   │ ▓
│ Embedding Gen      30-60 sec │ ▓▓▓▓▓▓▓▓▓▓▓
│ Vector Indexing    2-5 sec   │ ▓▓
│ ─────────────────────────────┤
│ Total             40-80 sec  │
└─────────────────────────────┘

Typical Query (Warm Start):
┌─────────────────────────────┐
│ Query Embedding    0.2-0.5s  │ ▓
│ Vector Search      0.01-0.02 │
│ Context Format     0.01-0.05 │
│ LLM Generation     3-8 sec   │ ▓▓▓▓▓▓▓
│ ─────────────────────────────┤
│ Total              3.5-9 sec  │
└─────────────────────────────┘


TECHNOLOGY STACK VISUALIZATION
═════════════════════════════════════════════════════════════════════════════

                    ┌──────────────────────────┐
                    │   User Interface Layer   │
                    │ (interactive_rag.py)     │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  LangChain Agents       │
                    │ (RAG Agent Core)        │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼─────────┐   ┌──────────▼──────────┐   ┌────────▼─────────┐
│  MarkItDown     │   │  RecursiveCharTxtSp │   │  Google AI       │
│  (Convert PDF,  │   │  (Semantic Chunking)│   │  (Embeddings)    │
│   DOCX to TXT)  │   │  (LangChain)        │   │  (768-D vectors) │
└─────────────────┘   └────────────────────┘   └──────────────────┘
                                                         │
                    ┌────────────────────────────────────┼
                    │                                    │
           ┌────────▼──────────┐            ┌───────────▼──────────┐
           │  FAISS            │            │ Gemini Pro (LLM)     │
           │  Vector Store     │            │ (Generate Answers)   │
           │  (Similarity Search)           │ (Context-Aware)      │
           └───────────────────┘            └──────────────────────┘


DATA STRUCTURE EXAMPLE
═════════════════════════════════════════════════════════════════════════════

Original PDF (CV1.pdf):
┌─────────────────────────────────────────┐
│ John Doe                                │
│ Senior Software Engineer                │
│                                         │
│ Skills: Python, Java, AWS, Docker       │
│ Experience: 8 years in full-stack dev   │
│ Projects: Led migration to microservices│
└─────────────────────────────────────────┘

After MarkItDown + Chunking:
┌─────────────────────────────────────────┐
│ Chunk 1 (Index 0):                      │
│ "# John Doe\n\nSenior Software..."      │
│ Source: CV1.pdf                         │
│ Metadata: {type: 'pdf', index: 0}       │
│ Embedding: [768 floats]                 │
│                                         │
│ Chunk 2 (Index 800):                    │
│ "...Engineer\n\nSkills: Python, Java.." │
│ Source: CV1.pdf                         │
│ Metadata: {type: 'pdf', index: 800}     │
│ Embedding: [768 floats]                 │
└─────────────────────────────────────────┘

In FAISS Store:
┌─────────────────────────────────────────┐
│ Vector Index:                           │
│ Chunk1_vec ──▶ [0.234, -0.156, ...]    │
│ Chunk2_vec ──▶ [0.567, 0.891, ...]    │
│ ...                                     │
│ Chunk66_vec ──▶ [-0.421, 0.789, ...]   │
│                                         │
│ Lookup Tables:                          │
│ vec_id → source: 'CV1.pdf'              │
│ vec_id → content: 'John Doe...'         │
└─────────────────────────────────────────┘


SCALABILITY PROGRESSION
═════════════════════════════════════════════════════════════════════════════

Workload           Processing Time    Memory Usage    Vector Store Size
─────────────────────────────────────────────────────────────────────────
10 CVs (~500KB)         ~5-10 sec       ~100MB         ~20MB
50 CVs (~2.5MB)         ~25-50 sec      ~300MB         ~100MB
100 CVs (~5MB)          ~50-100 sec     ~500MB         ~200MB
500 CVs (~25MB)         ~250-500 sec    ~1.5GB         ~1GB
1000 CVs (~50MB)        ~500-1000 sec   ~3GB           ~2GB

Bottleneck Analysis:
• Embedding Generation: API latency (can be parallelized)
• Vector Storage: Memory bound (can use disk-based indices)
• Retrieval: Fast (FAISS is optimized)
• LLM Generation: Fixed per query (~3-8 sec)


═════════════════════════════════════════════════════════════════════════════

This visualization shows the complete journey from your CV documents to
intelligent answers, highlighting each stage of the RAG process and how
the different technologies work together seamlessly.

═════════════════════════════════════════════════════════════════════════════
