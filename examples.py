"""
Example usage and testing script for the CV RAG Agent

This script demonstrates various ways to use the RAG agent for analyzing CVs.
"""

import sys
from pathlib import Path
from rag_agent import CVRAGAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Example 1: Basic usage with default settings"""
    print("\n" + "="*80)
    print("Example 1: Basic Usage")
    print("="*80 + "\n")
    
    try:
        # Initialize agent
        agent = CVRAGAgent()
        
        # Initialize pipeline
        if not agent.initialize_pipeline():
            print("Failed to initialize pipeline")
            return
        
        # Ask a question
        question = "What are the main technical skills mentioned in the CVs?"
        print(f"Question: {question}\n")
        
        result = agent.query(question)
        print(f"Answer: {result}\n")
        
    except Exception as e:
        logger.error(f"Error in basic example: {str(e)}", exc_info=True)


def example_document_inspection():
    """Example 2: Inspect loaded documents"""
    print("\n" + "="*80)
    print("Example 2: Document Inspection")
    print("="*80 + "\n")
    
    try:
        agent = CVRAGAgent()
        
        # Load documents
        documents = agent.load_documents()
        
        print(f"Total documents loaded: {len(documents)}\n")
        
        for i, doc in enumerate(documents, 1):
            print(f"Document {i}:")
            print(f"  Name: {doc.metadata.get('source', 'Unknown')}")
            print(f"  Type: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"  Content length: {len(doc.page_content)} characters")
            print(f"  Preview: {doc.page_content[:200]}...\n")
        
    except Exception as e:
        logger.error(f"Error in inspection example: {str(e)}", exc_info=True)


def example_chunking_analysis():
    """Example 3: Analyze text chunking"""
    print("\n" + "="*80)
    print("Example 3: Chunking Analysis")
    print("="*80 + "\n")
    
    try:
        agent = CVRAGAgent(chunk_size=800, chunk_overlap=150)
        
        # Load and chunk documents
        documents = agent.load_documents()
        chunks = agent.chunk_documents(documents)
        
        print(f"Original documents: {len(documents)}")
        print(f"Resulting chunks: {len(chunks)}\n")
        
        print("Chunk statistics:")
        sizes = [len(chunk.page_content) for chunk in chunks]
        print(f"  Average chunk size: {sum(sizes) // len(sizes)} characters")
        print(f"  Min chunk size: {min(sizes)} characters")
        print(f"  Max chunk size: {max(sizes)} characters\n")
        
        print("Sample chunks:")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"\nChunk {i} (from {chunk.metadata.get('source', 'Unknown')}):")
            print(f"Content: {chunk.page_content[:150]}...")
        
    except Exception as e:
        logger.error(f"Error in chunking example: {str(e)}", exc_info=True)


def example_rebuild_vector_store():
    """Example 4: Rebuild vector store"""
    print("\n" + "="*80)
    print("Example 4: Rebuild Vector Store")
    print("="*80 + "\n")
    
    try:
        agent = CVRAGAgent()
        
        print("Initializing pipeline with rebuild=True...")
        if agent.initialize_pipeline(rebuild=True):
            print("✓ Vector store rebuilt successfully\n")
            
            if agent.vector_store:
                print(f"✓ Vector store contains embeddings for documents")
        
    except Exception as e:
        logger.error(f"Error in rebuild example: {str(e)}", exc_info=True)


def example_multiple_queries():
    """Example 5: Process multiple related queries"""
    print("\n" + "="*80)
    print("Example 5: Multiple Related Queries")
    print("="*80 + "\n")
    
    queries = [
        "What programming languages are mentioned?",
        "Which candidates have experience with machine learning?",
        "What are the educational qualifications mentioned?",
        "List any certifications or special achievements",
    ]
    
    try:
        agent = CVRAGAgent()
        
        if not agent.initialize_pipeline():
            print("Failed to initialize pipeline")
            return
        
        print(f"Processing {len(queries)} queries...\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'─'*80}")
            print(f"Query {i}: {query}")
            print('─'*80)
            
            try:
                result = agent.query(query)
                print(f"Answer: {result}\n")
            except Exception as e:
                print(f"Error: {str(e)}\n")
                logger.error(f"Error processing query {i}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in multiple queries example: {str(e)}", exc_info=True)


def example_error_handling():
    """Example 6: Error handling scenarios"""
    print("\n" + "="*80)
    print("Example 6: Error Handling")
    print("="*80 + "\n")
    
    # Scenario 1: Query before initialization
    print("Scenario 1: Query before initialization")
    try:
        agent = CVRAGAgent()
        agent.query("What skills are mentioned?")
    except ValueError as e:
        print(f"✓ Caught expected error: {str(e)}\n")
    
    # Scenario 2: Missing CV folder
    print("Scenario 2: Non-existent CV folder")
    try:
        agent = CVRAGAgent(cv_folder="nonexistent_folder")
        docs = agent.load_documents()
        print(f"✓ No documents loaded (expected): {len(docs)} documents\n")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    
    # Scenario 3: Invalid query
    print("Scenario 3: Empty query")
    try:
        agent = CVRAGAgent()
        if agent.initialize_pipeline():
            result = agent.query("")
            print(f"Result with empty query: {result}\n")
    except Exception as e:
        logger.error(f"Error with empty query: {str(e)}\n")


def example_custom_configuration():
    """Example 7: Custom configuration"""
    print("\n" + "="*80)
    print("Example 7: Custom Configuration")
    print("="*80 + "\n")
    
    try:
        # Create agent with custom parameters
        agent = CVRAGAgent(
            cv_folder="cv",
            chunk_size=1500,      # Larger chunks
            chunk_overlap=300,    # More overlap
            vector_store_path="custom_vector_store"
        )
        
        print("Custom configuration:")
        print(f"  CV Folder: {agent.cv_folder}")
        print(f"  Chunk Size: {agent.chunk_size} characters")
        print(f"  Chunk Overlap: {agent.chunk_overlap} characters")
        print(f"  Vector Store Path: {agent.vector_store_path}\n")
        
        print("Initializing with custom settings...")
        if agent.initialize_pipeline(rebuild=False):
            print("✓ Pipeline initialized with custom settings")
        
    except Exception as e:
        logger.error(f"Error in custom configuration example: {str(e)}", exc_info=True)


def main():
    """Run all examples"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*15 + "CV RAG Agent - Example Usage & Tests" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Document Inspection", example_document_inspection),
        ("Chunking Analysis", example_chunking_analysis),
        ("Rebuild Vector Store", example_rebuild_vector_store),
        ("Multiple Queries", example_multiple_queries),
        ("Error Handling", example_error_handling),
        ("Custom Configuration", example_custom_configuration),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  {len(examples) + 1}. Run all examples")
    print(f"  {len(examples) + 2}. Exit")
    
    while True:
        try:
            choice = input("\nSelect example to run (1-9): ").strip()
            
            if choice == str(len(examples) + 2):
                print("\nExiting examples. Goodbye!")
                break
            elif choice == str(len(examples) + 1):
                for name, func in examples:
                    print(f"\n✓ Running: {name}")
                    try:
                        func()
                    except Exception as e:
                        logger.error(f"Failed to run {name}: {str(e)}")
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(examples):
                name, func = examples[int(choice) - 1]
                print(f"\n✓ Running: {name}")
                func()
            else:
                print("Invalid selection. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nExiting examples. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
