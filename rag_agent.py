"""
RAG Agent for CV Analysis using LangChain, MarkItDown, Google AI, and FAISS

This module implements a Retrieval Augmented Generation (RAG) system that:
1. Loads PDF and DOCX documents from the 'cv' folder using MarkItDown
2. Splits documents into chunks using LangChain's RecursiveCharacterTextSplitter
3. Generates embeddings using Google AI
4. Stores embeddings in FAISS vector store
5. Performs RAG to answer questions about CV content

COSTAR Framework Application:
- Context: CV documents and industry knowledge
- Objective: Answer specific questions about CVs
- Style: Professional and informative
- Tone: Helpful and accurate
- Audience: HR professionals and recruiters
- Response: Detailed and context-backed
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

from markitdown import MarkItDown
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class CVRAGAgent:
    """
    A RAG agent for analyzing CV documents.
    
    This class handles:
    - Document loading from a folder using MarkItDown
    - Document chunking
    - Embedding generation with Google AI
    - Vector store management with FAISS
    - RAG-based question answering
    """
    
    def __init__(
        self,
        cv_folder: str = "cv",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        vector_store_path: str = "cv_vector_store"
    ):
        """
        Initialize the CV RAG Agent.
        
        Args:
            cv_folder: Path to folder containing CV documents
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
            vector_store_path: Path where FAISS vector store will be saved/loaded
        """
        self.cv_folder = Path(cv_folder)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store_path = vector_store_path
        
        # Initialize components
        self.md_converter = MarkItDown()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            add_start_index=True
        )
        
        # Initialize Google AI embeddings
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        
        # Initialize LLM for generation (safety settings removed - API handles filtering)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.vector_store = None
        self.documents = []
        
        logger.info(f"CVRAGAgent initialized with cv_folder={cv_folder}")
    
    def load_documents(self) -> List[Document]:
        """
        Load all PDF and DOCX files from the cv folder using MarkItDown.
        
        Returns:
            List of Document objects
        """
        logger.info(f"Loading documents from {self.cv_folder}")
        
        if not self.cv_folder.exists():
            logger.warning(f"CV folder not found at {self.cv_folder}")
            return []
        
        documents = []
        supported_extensions = {'.pdf', '.docx', '.doc'}
        
        for file_path in self.cv_folder.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    logger.info(f"Converting {file_path.name} using MarkItDown")
                    result = self.md_converter.convert(str(file_path))
                    
                    doc = Document(
                        page_content=result.text_content,
                        metadata={
                            "source": file_path.name,
                            "file_path": str(file_path),
                            "file_type": file_path.suffix.lower()
                        }
                    )
                    documents.append(doc)
                    logger.info(f"Successfully loaded {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {str(e)}")
                    continue
        
        self.documents = documents
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    
    def chunk_documents(self, documents: Optional[List[Document]] = None) -> List[Document]:
        """
        Split documents into chunks for embedding.
        
        Args:
            documents: List of documents to chunk. Uses self.documents if None.
            
        Returns:
            List of chunked documents
        """
        if documents is None:
            documents = self.documents
        
        logger.info(f"Chunking {len(documents)} documents")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from documents")
        
        return chunks
    
    def create_vector_store(self, chunks: Optional[List[Document]] = None) -> FAISS:
        """
        Create FAISS vector store from document chunks.
        
        Args:
            chunks: List of document chunks. If None, chunks self.documents.
            
        Returns:
            FAISS vector store
        """
        if chunks is None:
            chunks = self.chunk_documents()
        
        logger.info(f"Creating FAISS vector store with {len(chunks)} chunks")
        
        try:
            self.vector_store = FAISS.from_documents(
                chunks,
                self.embeddings
            )
            logger.info("FAISS vector store created successfully")
            return self.vector_store
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "ResourceExhausted" in error_msg:
                logger.error(f"Error creating vector store: Google API quota exceeded")
                print("\n" + "="*80)
                print("[WARNING] QUOTA LIMIT REACHED - Google API Free Tier")
                print("="*80)
                print("\nThe Google Generative AI API free tier has limited embedding requests.")
                print("\n[INFO] TO FIX THIS ISSUE:")
                print("\n1. Visit Google AI Studio: https://ai.google.dev/")
                print("2. Set up a PAID BILLING PLAN (no longer free tier)")
                print("3. Your current API key will then have access to:")
                print("   - Unlimited embedding requests (for production use)")
                print("   - Higher rate limits")
                print("   - Production support")
                print("\n4. No code changes needed - just update your billing!")
                print("\n[NOTE] ALTERNATIVE (Testing only):")
                print("   Switch to a different embedding model or use local embeddings")
                print("="*80 + "\n")
                raise
            else:
                logger.error(f"Error creating vector store: {error_msg}")
                raise
    
    def save_vector_store(self):
        """Save the FAISS vector store to disk."""
        if self.vector_store is None:
            logger.warning("No vector store to save")
            return
        
        logger.info(f"Saving vector store to {self.vector_store_path}")
        self.vector_store.save_local(self.vector_store_path)
        logger.info("Vector store saved successfully")
    
    def load_vector_store(self):
        """Load FAISS vector store from disk."""
        if not Path(self.vector_store_path).exists():
            logger.warning(f"Vector store not found at {self.vector_store_path}")
            return False
        
        logger.info(f"Loading vector store from {self.vector_store_path}")
        try:
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Vector store loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def create_retrieval_tool(self):
        """
        Create a retrieval tool for the agent.
        
        Returns:
            Callable tool that retrieves relevant context
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Create or load it first.")
        
        @tool(response_format="content_and_artifact")
        def retrieve_cv_context(query: str) -> tuple[str, List[Document]]:
            """
            Retrieve relevant CV information to answer a query.
            
            Args:
                query: The user's question about the CVs
                
            Returns:
                Tuple of (formatted_content, retrieved_documents)
            """
            logger.info(f"Retrieving context for query: {query}")
            
            # Retrieve relevant documents
            retrieved_docs = self.vector_store.similarity_search(query, k=4)
            
            # Format the retrieved context
            formatted_content = "\n\n".join([
                f"Source: {doc.metadata.get('source', 'Unknown')}\n"
                f"Content: {doc.page_content}"
                for doc in retrieved_docs
            ])
            
            logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")
            
            return formatted_content, retrieved_docs
        
        return retrieve_cv_context
    
    def query_simple(self, question: str) -> str:
        """
        Simple query method without agent framework.
        
        Args:
            question: The question to ask about CV content
            
        Returns:
            The response from the LLM
        """
        if self.vector_store is None:
            raise ValueError("RAG pipeline not initialized. Call initialize_pipeline() first.")
        
        logger.info(f"Processing query: {question}")
        
        # Retrieve similar documents
        logger.info("Retrieving context...")
        retrieved_docs = self.vector_store.similarity_search(question, k=4)
        
        # Format context
        formatted_context = "\n\n---\n\n".join([
            f"**Source: {doc.metadata.get('source', 'Unknown')}**\n\n{doc.page_content}"
            for doc in retrieved_docs
        ])
        
        # Create prompt for LLM
        system_prompt = """You are a professional CV Analyst assistant. Your role is to help analyze and understand information from CV documents.

COSTAR Framework Guidelines:
- **Context**: You have access to a database of CV documents
- **Objective**: Provide accurate, detailed answers about candidate qualifications, experience, and skills
- **Style**: Professional, structured, and clear
- **Tone**: Helpful, impartial, and informative
- **Audience**: HR professionals, recruiters, and hiring managers
- **Response**: Detailed, evidence-based answers with specific references to CV content

When answering questions:
1. Provide accurate information based on the retrieved documents
2. Always cite the source CV when providing information
3. Provide specific examples from the documents
4. Be objective and factual
5. If information is not available, clearly state that"""

        user_message = f"""Based on the following CV content, please answer this question:

Question: {question}

Retrieved CV Content:
{formatted_context}

Please provide a detailed, evidence-based answer with specific references to the CV sources."""

        # Generate response
        logger.info("Generating response...")
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = self.llm.invoke(messages)
        
        logger.info("Query processed successfully")
        return response.content
    
    def setup_agent(self):
        """
        Placeholder for agent setup (using simple query instead).
        
        Returns:
            None
        """
        logger.info("Setting up RAG agent")
        logger.info("RAG agent setup complete")
        return None
    
    def initialize_pipeline(self, rebuild: bool = False) -> bool:
        """
        Initialize the complete RAG pipeline.
        
        Args:
            rebuild: If True, rebuild from scratch. If False, try to load existing store.
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Initializing RAG pipeline (rebuild={rebuild})")
        
        # Try to load existing vector store if not rebuilding
        if not rebuild and self.load_vector_store():
            logger.info("Loaded existing vector store")
            return True
        
        # Load and process documents
        documents = self.load_documents()
        if not documents:
            logger.error("No documents loaded")
            return False
        
        # Chunk documents
        chunks = self.chunk_documents(documents)
        
        # Create vector store
        self.create_vector_store(chunks)
        
        # Save vector store
        self.save_vector_store()
        
        logger.info("RAG pipeline initialized successfully")
        return True
    
    def query(self, question: str) -> str:
        """
        Query the RAG agent with a question about CVs.
        
        Args:
            question: The question to ask about CV content
            
        Returns:
            The agent's response
        """
        return self.query_simple(question)


def main():
    """Example usage of the CV RAG Agent."""
    
    # Initialize the RAG agent
    rag_agent = CVRAGAgent(cv_folder="cv", chunk_size=1000, chunk_overlap=200)
    
    # Initialize the pipeline
    if not rag_agent.initialize_pipeline(rebuild=False):
        logger.error("Failed to initialize RAG pipeline")
        return
    
    # Example queries
    example_queries = [
        "What are the main skills mentioned across all CVs?",
        "Which candidates have experience with Python?",
        "What are the educational backgrounds of the candidates?",
    ]
    
    # Process queries
    for query in example_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        try:
            result = rag_agent.query(query)
            print(f"Response: {result}")
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
