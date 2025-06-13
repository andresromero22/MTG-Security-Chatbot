"""Utility functions for creating the FAISS vector index."""

import os
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()


def create_vector_index(pdf_dir: str = "./manuals", quick_ref: str = "./resources/quick_reference.txt", index_dir: str = "./rag_index") -> None:
    """Create a FAISS vector index from PDF manuals and a reference text.

    Parameters
    ----------
    pdf_dir : str, optional
        Directory containing PDF manuals.
    quick_ref : str, optional
        Path to a text file with additional reference material.
    index_dir : str, optional
        Directory where the FAISS index will be saved.
    """
    # Load API key
    openai_api_key = os.getenv("OPEN_AI_KEY")
    if not openai_api_key:
        raise RuntimeError("OPEN_AI_KEY environment variable not set")

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Load documents from PDFs
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
    quick_ref_loader = TextLoader(quick_ref)
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
    vectorstore.save_local(index_dir)
    print(f"\n✅ Vector index created and saved in {index_dir}")
