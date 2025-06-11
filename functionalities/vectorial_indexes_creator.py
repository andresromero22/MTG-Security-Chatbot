from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os

# Load API key
with open("./resources/api_key.txt", "r") as f:
    openai_api_key = f.read().strip()

embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

# Load documents from PDFs
pdf_dir = "./manuals"
documents = []
print("📚 Loading PDFs...")

for filename in os.listdir(pdf_dir):
    if filename.endswith(".pdf"):
        print(f"→ Loading {filename}")
        loader = PyPDFLoader(os.path.join(pdf_dir, filename))
        docs = loader.load()
        print(f"  Loaded {len(docs)} pages.")
        documents.extend(docs)

# Load quick_reference.txt
print("\n📚 Loading quick_reference.txt...")
quick_ref_loader = TextLoader("./resources/quick_reference.txt")
quick_ref_docs = quick_ref_loader.load()
print(f"→ Loaded {len(quick_ref_docs)} quick reference document(s).")
documents.extend(quick_ref_docs)

# Split documents into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(documents)
print(f"\n✂️ Total chunks after splitting: {len(chunks)}")

# Create FAISS index
print("\n🛠️ Creating FAISS index...")
vectorstore = FAISS.from_documents(chunks, embedding)

# Save index
vectorstore.save_local("./rag_index")
print("\n✅ Vector index created and saved in ./rag_index")
