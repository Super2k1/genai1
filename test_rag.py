#!/usr/bin/env python
"""
Quick test to verify CV RAG Agent is working correctly
"""

import os
from pathlib import Path
from rag_agent import CVRAGAgent

def test_import():
    """Test that all modules can be imported"""
    print("✓ Testing imports...")
    try:
        from rag_agent import CVRAGAgent
        from interactive_rag import InteractiveCVRAG
        print("✓ All imports successful\n")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}\n")
        return False

def test_agent_creation():
    """Test that CVRAGAgent can be created"""
    print("✓ Testing CVRAGAgent creation...")
    try:
        agent = CVRAGAgent()
        print("✓ CVRAGAgent created successfully\n")
        return True
    except Exception as e:
        print(f"✗ Agent creation failed: {e}\n")
        return False

def test_environment():
    """Test that environment is properly configured"""
    print("✓ Testing environment configuration...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✓ GOOGLE_API_KEY found (length: {len(api_key)})\n")
        return True
    else:
        print("✗ GOOGLE_API_KEY not found in environment\n")
        return False

def test_cv_folder():
    """Test that cv folder exists"""
    print("✓ Testing cv folder...")
    cv_folder = Path("cv")
    
    if cv_folder.exists():
        cv_files = list(cv_folder.glob("*"))
        if cv_files:
            print(f"✓ cv folder found with {len(cv_files)} file(s):")
            for f in cv_files:
                print(f"  - {f.name}")
            print()
            return True
        else:
            print("⚠ cv folder exists but is empty (add PDF/DOCX files)\n")
            return False
    else:
        print("⚠ cv folder not found (will be created on first use)\n")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("CV RAG Agent - Quick Test Suite")
    print("="*70 + "\n")
    
    tests = [
        ("Module Imports", test_import),
        ("Agent Creation", test_agent_creation),
        ("Environment", test_environment),
        ("CV Folder", test_cv_folder),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Test: {name}")
        print("-" * 70)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test failed with error: {e}\n")
            results.append((name, False))
    
    # Summary
    print("="*70)
    print("Test Summary")
    print("="*70 + "\n")
    
    for name, result in results:
        status = "✓ PASS" if result else "⚠ WARNING"
        print(f"{status}: {name}")
    
    all_passed = all(r for _, r in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ All tests passed! RAG Agent is ready to use.")
        print("\nNext steps:")
        print("1. Add your PDF/DOCX files to the cv/ folder")
        print("2. Run: python interactive_rag.py")
        print("3. Select option 1 and start asking questions!")
    else:
        print("⚠ Some tests had warnings. Check the output above.")
        print("\nTo fix issues:")
        print("1. Ensure .env file has GOOGLE_API_KEY")
        print("2. Create cv/ folder and add CV files")
        print("3. All dependencies installed: pip install -r requiments.txt")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
