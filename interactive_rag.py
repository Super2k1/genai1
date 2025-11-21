"""
Interactive CLI for CV RAG Agent

Provides a user-friendly command-line interface for interacting with the RAG system.
"""

import sys
import os
from pathlib import Path
from rag_agent import CVRAGAgent
import logging

# Fix Windows terminal encoding issues
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractiveCVRAG:
    """Interactive interface for the CV RAG Agent."""
    
    def __init__(self):
        self.agent = None
        self.initialized = False
    
    def initialize(self, rebuild: bool = False):
        """Initialize the RAG agent."""
        print("\n" + "="*80)
        print("Initializing CV RAG Agent...")
        print("="*80 + "\n")
        
        self.agent = CVRAGAgent(cv_folder="cv", chunk_size=1000, chunk_overlap=200)
        
        if self.agent.initialize_pipeline(rebuild=rebuild):
            self.initialized = True
            print("\n[OK] RAG Agent initialized successfully!")
            print(f"[OK] Loaded {len(self.agent.documents)} CV documents")
            
            if self.agent.vector_store:
                print(f"[OK] Vector store created with embeddings")
        else:
            print("\n[ERROR] Failed to initialize RAG Agent")
            self.initialized = False
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*80)
        print("CV RAG Agent - Main Menu")
        print("="*80)
        print("1. Ask a question about CVs")
        print("2. Reinitialize with new documents")
        print("3. View loaded documents")
        print("4. Example queries")
        print("5. Exit")
        print("="*80)
    
    def ask_question(self):
        """Handle user question."""
        if not self.initialized:
            print("Agent not initialized. Please initialize first.")
            return
        
        question = input("\nEnter your question about CVs: ").strip()
        if not question:
            print("Question cannot be empty.")
            return
        
        print("\n" + "-"*80)
        print("Processing your question...")
        print("-"*80 + "\n")
        
        try:
            result = self.agent.query(question)
            print("\nResponse:")
            print("-"*80)
            
            # Extract the final response
            if isinstance(result, dict):
                if 'output' in result:
                    print(result['output'])
                else:
                    print(result)
            else:
                print(result)
            
            print("-"*80)
        except Exception as e:
            print(f"\n[ERROR] Error: {str(e)}")
            logger.error(f"Query error: {str(e)}", exc_info=True)
    
    def view_documents(self):
        """Display loaded documents."""
        if not self.initialized or not self.agent.documents:
            print("No documents loaded.")
            return
        
        print("\n" + "="*80)
        print("Loaded Documents")
        print("="*80 + "\n")
        
        for i, doc in enumerate(self.agent.documents, 1):
            print(f"{i}. {doc.metadata.get('source', 'Unknown')}")
            print(f"   Type: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"   Content length: {len(doc.page_content)} characters")
            print()
    
    def show_examples(self):
        """Display example queries."""
        examples = [
            "What are the main technical skills mentioned in the CVs?",
            "Which candidates have experience with data science or machine learning?",
            "What programming languages are mentioned?",
            "Summarize the educational background of candidates",
            "What are the most common job titles or roles mentioned?",
            "Which candidates have international experience?",
            "What certifications or special achievements are mentioned?",
        ]
        
        print("\n" + "="*80)
        print("Example Queries")
        print("="*80 + "\n")
        
        for i, example in enumerate(examples, 1):
            print(f"{i}. {example}")
        
        print("\n" + "="*80)
    
    def run(self):
        """Run the interactive CLI."""
        print("\n" + "="*80)
        print(" "*20 + "Welcome to CV RAG Agent")
        print("="*80)
        
        # Initialize on startup
        self.initialize(rebuild=False)
        
        if not self.initialized:
            print("\nInitialization failed. Exiting.")
            return
        
        # Main loop
        while True:
            self.display_menu()
            choice = input("\nSelect an option (1-5): ").strip()
            
            if choice == '1':
                self.ask_question()
            elif choice == '2':
                rebuild = input("\nRebuild from scratch? (y/n): ").strip().lower() == 'y'
                self.initialize(rebuild=rebuild)
            elif choice == '3':
                self.view_documents()
            elif choice == '4':
                self.show_examples()
            elif choice == '5':
                print("\n[OK] Thank you for using CV RAG Agent. Goodbye!")
                break
            else:
                print("\n[ERROR] Invalid option. Please try again.")


def main():
    """Entry point for the interactive CLI."""
    try:
        app = InteractiveCVRAG()
        app.run()
    except KeyboardInterrupt:
        print("\n\n[OK] Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {str(e)}")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
