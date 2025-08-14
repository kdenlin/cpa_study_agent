#!/usr/bin/env python3
"""
Test script for PDF ingestion - run this locally to debug issues before deploying
"""

import os
import sys
import traceback

def test_environment():
    """Test if all required packages are available"""
    print("Testing environment...")
    
    required_packages = [
        'pdfplumber',
        'chromadb', 
        'sentence_transformers',
        'tqdm',
        'torch'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {missing_packages}")
        print("Please install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    print("All required packages are available!")
    return True

def test_paths():
    """Test if required paths exist"""
    print("\nTesting paths...")
    
    # Get project root
    project_root = os.path.abspath(os.path.dirname(__file__))
    
    # Test textbooks folder
    textbooks_path = os.path.join(project_root, "textbooks")
    data_textbooks_path = os.path.join(project_root, "data", "textbooks")
    
    print(f"Project root: {project_root}")
    print(f"Textbooks folder: {textbooks_path}")
    print(f"Data textbooks folder: {data_textbooks_path}")
    
    if os.path.exists(textbooks_path):
        print(f"✓ Textbooks folder exists: {textbooks_path}")
        files = os.listdir(textbooks_path)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        print(f"  Found {len(pdf_files)} PDF files: {pdf_files}")
        return textbooks_path, pdf_files
    elif os.path.exists(data_textbooks_path):
        print(f"✓ Data textbooks folder exists: {data_textbooks_path}")
        files = os.listdir(data_textbooks_path)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        print(f"  Found {len(pdf_files)} PDF files: {pdf_files}")
        return data_textbooks_path, pdf_files
    else:
        print("✗ No textbooks folder found!")
        print("Please create a 'textbooks' folder in the project root and add PDF files")
        return None, []

def test_chromadb():
    """Test ChromaDB setup"""
    print("\nTesting ChromaDB...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        project_root = os.path.abspath(os.path.dirname(__file__))
        persist_dir = os.path.join(project_root, "app", "db", "chroma_db_test")
        
        print(f"ChromaDB path: {persist_dir}")
        
        # Create directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Test client creation
        client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir
        ))
        print("✓ ChromaDB client created successfully")
        
        # Test collection creation
        collection = client.get_or_create_collection("test_collection")
        print("✓ Collection created successfully")
        
        # Test adding a simple document
        collection.add(
            documents=["This is a test document"],
            metadatas=[{"test": "metadata"}],
            ids=["test_id"]
        )
        print("✓ Document added successfully")
        
        # Test querying
        results = collection.query(query_texts=["test document"], n_results=1)
        print("✓ Query successful")
        
        # Clean up test collection
        client.delete_collection("test_collection")
        print("✓ Test collection cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ ChromaDB test failed: {e}")
        traceback.print_exc()
        return False

def test_embeddings():
    """Test embedding model"""
    print("\nTesting embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Test model loading
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embedding model loaded successfully")
        
        # Test embedding generation
        test_text = "This is a test sentence for embedding."
        embedding = embedder.encode(test_text)
        print(f"✓ Embedding generated successfully (shape: {embedding.shape})")
        
        return True
        
    except Exception as e:
        print(f"✗ Embedding test failed: {e}")
        traceback.print_exc()
        return False

def test_pdf_processing():
    """Test PDF processing with a small sample"""
    print("\nTesting PDF processing...")
    
    project_root = os.path.abspath(os.path.dirname(__file__))
    textbooks_path = os.path.join(project_root, "textbooks")
    data_textbooks_path = os.path.join(project_root, "data", "textbooks")
    
    # Find the first PDF file
    pdf_path = None
    if os.path.exists(textbooks_path):
        files = os.listdir(textbooks_path)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            pdf_path = os.path.join(textbooks_path, pdf_files[0])
    elif os.path.exists(data_textbooks_path):
        files = os.listdir(data_textbooks_path)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        if pdf_files:
            pdf_path = os.path.join(data_textbooks_path, pdf_files[0])
    
    if not pdf_path:
        print("✗ No PDF files found for testing")
        return False
    
    try:
        import pdfplumber
        
        print(f"Testing with: {pdf_path}")
        
        with pdfplumber.open(pdf_path) as pdf:
            # Test first page only
            if len(pdf.pages) > 0:
                page = pdf.pages[0]
                text = page.extract_text()
                print(f"✓ PDF opened successfully")
                print(f"  First page text length: {len(text) if text else 0} characters")
                
                if text and len(text.strip()) > 50:
                    print("✓ Text extraction successful")
                    return True
                else:
                    print("✗ Text extraction failed or text too short")
                    return False
            else:
                print("✗ PDF has no pages")
                return False
                
    except Exception as e:
        print(f"✗ PDF processing test failed: {e}")
        traceback.print_exc()
        return False

def run_full_test():
    """Run all tests"""
    print("=" * 50)
    print("CPA Study Agent - Ingestion Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Paths", test_paths),
        ("ChromaDB", test_chromadb),
        ("Embeddings", test_embeddings),
        ("PDF Processing", test_pdf_processing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your environment is ready for deployment.")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1) 