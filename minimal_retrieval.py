import chromadb
import os

persist_dir = os.path.abspath("app/db/chroma_db_test")
os.makedirs(persist_dir, exist_ok=True)
print("ChromaDB absolute path:", persist_dir)

client = chromadb.PersistentClient(path=persist_dir)
collection = client.get_or_create_collection("test_collection")
collection.add(
    ids=["test1"],
    documents=["This is a test document."],
    metadatas=[{"source": "test"}]
)
print("Count:", collection.count())
print("Files in ChromaDB directory:", os.listdir(persist_dir))