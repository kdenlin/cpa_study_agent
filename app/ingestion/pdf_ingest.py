import pdfplumber
import re
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Get the project root (one level up from this file's directory)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
persist_dir = os.path.join(project_root, "app", "db", "chroma_db_test")
os.makedirs(persist_dir, exist_ok=True)
folder_path = os.path.join(project_root, "data", "textbooks")

print("ChromaDB absolute path:", persist_dir)
print("Textbooks folder absolute path:", folder_path)

chroma_client = chromadb.PersistentClient(path=persist_dir)
collection = chroma_client.get_or_create_collection("textbook_chunks")
print("Using ChromaDB directory:", persist_dir)
# Initialize SentenceTransformer model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    return embedder.encode(text).tolist()

def extract_chunks_from_pdf(pdf_path):
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            for para in paragraphs:
                section_match = re.match(r'^[A-Z][A-Z\s\-:]+$', para)
                section = para if section_match else None
                chunk = {
                    "chunk_text": para,
                    "page": page_num,
                    "section": section
                }
                chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"\nProcessing: {filename}\n" + "-"*40)
            chunks = extract_chunks_from_pdf(pdf_path)
            print(f"Extracted {len(chunks)} chunks from {filename}")
            for i, c in enumerate(tqdm(chunks, desc=f"Embedding {filename}")):
                chunk_id = f"{filename}_p{c['page']}_c{i}"
                embedding = get_embedding(c["chunk_text"])
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    metadatas=[{
    			"filename": filename,
    			"page": c["page"],
    			"section": c["section"] if c["section"] is not None else ""
		  	}],
                    documents=[c["chunk_text"]]
                )
                print(f"Added chunk {chunk_id} from {filename} page {c['page']}")
    print("Collection count after ingestion:", collection.count())
    print("All chunks embedded and stored in ChromaDB!")
    print("ChromaDB persisted to disk.")
