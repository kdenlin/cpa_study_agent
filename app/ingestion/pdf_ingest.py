import pdfplumber
import re
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import gc
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the project root (one level up from this file's directory)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
persist_dir = os.path.join(project_root, "app", "db", "chroma_db_test")
os.makedirs(persist_dir, exist_ok=True)
folder_path = os.path.join(project_root, "data", "textbooks")

# Also check the root textbooks folder (for Hugging Face Spaces)
textbooks_root = os.path.join(project_root, "textbooks")
if os.path.exists(textbooks_root):
    folder_path = textbooks_root

print("ChromaDB absolute path:", persist_dir)
print("Textbooks folder absolute path:", folder_path)

def setup_chroma_client():
    """Set up ChromaDB client with error handling"""
    try:
        chroma_client = chromadb.PersistentClient(path=persist_dir)
        return chroma_client
    except Exception as e:
        print(f"Error setting up ChromaDB client: {e}")
        return None

def setup_embedding_model():
    """Set up embedding model with error handling"""
    try:
        # Use a smaller model for Hugging Face Spaces
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        return embedder
    except Exception as e:
        print(f"Error setting up embedding model: {e}")
        return None

def get_embedding(text, embedder):
    """Get embedding with error handling"""
    try:
        return embedder.encode(text).tolist()
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

def extract_chunks_from_pdf(pdf_path, max_chunk_size=500):
    """Extract chunks from PDF with memory optimization"""
    chunks = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    text = page.extract_text()
                    if not text or len(text.strip()) < 50:
                        continue
                    
                    # Split into smaller chunks to reduce memory usage
                    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                    
                    for para in paragraphs:
                        if len(para) < 30:  # Skip very short paragraphs
                            continue
                            
                        # Further split long paragraphs
                        if len(para) > max_chunk_size:
                            # Split by sentences
                            sentences = re.split(r'[.!?]+', para)
                            current_chunk = ""
                            
                            for sentence in sentences:
                                if len(current_chunk) + len(sentence) < max_chunk_size:
                                    current_chunk += sentence + ". "
                                else:
                                    if current_chunk.strip():
                                        chunks.append({
                                            "chunk_text": current_chunk.strip(),
                                            "page": page_num,
                                            "section": None
                                        })
                                    current_chunk = sentence + ". "
                            
                            # Add remaining chunk
                            if current_chunk.strip():
                                chunks.append({
                                    "chunk_text": current_chunk.strip(),
                                    "page": page_num,
                                    "section": None
                                })
                        else:
                            section_match = re.match(r'^[A-Z][A-Z\s\-:]+$', para)
                            section = para if section_match else None
                            chunks.append({
                                "chunk_text": para,
                                "page": page_num,
                                "section": section
                            })
                            
                except Exception as e:
                    print(f"Error processing page {page_num} in {pdf_path}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return []
    
    return chunks

def ingest_pdfs_to_chromadb():
    """Main function to ingest PDFs with improved error handling and memory management"""
    
    # Setup ChromaDB
    chroma_client = setup_chroma_client()
    if not chroma_client:
        print("Failed to setup ChromaDB client")
        return False
    
    # Setup embedding model
    embedder = setup_embedding_model()
    if not embedder:
        print("Failed to setup embedding model")
        return False
    
    # Get or create collection
    try:
        collection = chroma_client.get_or_create_collection("textbook_chunks")
        print("Using ChromaDB directory:", persist_dir)
    except Exception as e:
        print(f"Error creating/getting collection: {e}")
        return False
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Textbooks folder not found: {folder_path}")
        return False
    
    # Get list of PDF files
    try:
        files = os.listdir(folder_path)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
    except Exception as e:
        print(f"Error listing files in {folder_path}: {e}")
        return False
    
    if not pdf_files:
        print("No PDF files found")
        return False
    
    total_chunks_processed = 0
    total_chunks_added = 0
    
    # Process files one by one to manage memory
    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        print(f"\nProcessing: {filename}")
        print("-" * 40)
        
        try:
            # Extract chunks
            chunks = extract_chunks_from_pdf(pdf_path)
            print(f"Extracted {len(chunks)} chunks from {filename}")
            
            if not chunks:
                print(f"No chunks extracted from {filename}, skipping...")
                continue
            
            # Process chunks in smaller batches
            batch_size = 5  # Smaller batch size for Hugging Face Spaces
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                batch_ids = []
                batch_embeddings = []
                batch_metadatas = []
                batch_documents = []
                
                for j, chunk in enumerate(batch):
                    chunk_id = f"{filename}_p{chunk['page']}_c{i+j}"
                    
                    # Get embedding
                    embedding = get_embedding(chunk["chunk_text"], embedder)
                    if embedding is None:
                        print(f"Skipping chunk {chunk_id} due to embedding error")
                        continue
                    
                    batch_ids.append(chunk_id)
                    batch_embeddings.append(embedding)
                    batch_metadatas.append({
                        "filename": filename,
                        "page": chunk["page"],
                        "section": chunk["section"] if chunk["section"] is not None else ""
                    })
                    batch_documents.append(chunk["chunk_text"])
                
                # Add batch to ChromaDB
                if batch_ids:
                    try:
                        collection.add(
                            ids=batch_ids,
                            embeddings=batch_embeddings,
                            metadatas=batch_metadatas,
                            documents=batch_documents
                        )
                        total_chunks_added += len(batch_ids)
                        print(f"Added batch of {len(batch_ids)} chunks from {filename}")
                    except Exception as e:
                        print(f"Error adding batch to ChromaDB: {e}")
                
                total_chunks_processed += len(batch)
                
                # Force garbage collection to free memory
                gc.collect()
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.1)
            
            print(f"Completed {filename}: {len(chunks)} chunks processed, {total_chunks_added} added to database")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    print(f"\nIngestion complete!")
    print(f"Total chunks processed: {total_chunks_processed}")
    print(f"Total chunks added to ChromaDB: {total_chunks_added}")
    print(f"Final collection count: {collection.count()}")
    print("ChromaDB persisted to disk.")
    
    return True

if __name__ == "__main__":
    success = ingest_pdfs_to_chromadb()
    if success:
        print("PDF ingestion completed successfully!")
    else:
        print("PDF ingestion failed!")
