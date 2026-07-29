from pathlib import Path
from langchain.tools import tool
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
#vector DB
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

# Global declared Singleton cache- lazy load
_vector_store = None

#loads files and builds the vector store
def load_policy_documents() -> list[Document]:
    """
    Load all policy documents from the policies folder.
    """
    root = Path(__file__).resolve().parents[1]
    policies_dir = root / "policies"
    documents = []
    for file_path in policies_dir.glob("*.txt"):
        loader = TextLoader(
            str(file_path),
            encoding="utf-8"
        )
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = file_path.name
        documents.extend(docs)
    return documents
#test: uv run python -c "from support_chatbot.rag_tool import load_policy_documents; print(len(load_policy_documents()))"


#chunk doc
def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split policy documents into overlapping chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)



#load or save into chroma db
def get_vector_store():
    """
    Create or load the persisted Chroma vector store.
    """
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    root = Path(__file__).resolve().parents[1]
    persist_dir = root / "chroma_db"
    embeddings = OpenAIEmbeddings( #need openapi key
        model="text-embedding-3-small"
    )

    if persist_dir.exists() and any(persist_dir.iterdir()):
        print("Loaded existing ChromaDB")
        _vector_store = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings,
        )
        return _vector_store

    print("Creating new ChromaDB...")
    documents = load_policy_documents()
    chunks = split_documents(documents)
    _vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    print("ChromaDB created.")

    return _vector_store
#load/test doc in chromaDB: $ uv run python -c "from support_chatbot.rag_tool import get_vector_store; get_vector_store(); print('done')"


@tool
def search_policies(query: str) -> str:
    """
    Search company policy and FAQ documents only.
    Do NOT use this tool for user orders, returns,
    payments or account-specific information.
    """
    vector_store = get_vector_store()
    docs = vector_store.similarity_search(
        query,
        k=4, #top k chunks
    )
    if not docs:
        return "No relevant policy found."
    results = []
    for doc in docs:
        source = doc.metadata.get(
            "source",
            "Unknown"
        )
        results.append(
            f"Source: {source}\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(results)

#load vectors on app start
def initialize_vector_store():
    """
    Initialize the vector store during application startup.
    """
    get_vector_store()


__all__ = [
    "search_policies",
    "initialize_vector_store",
]
