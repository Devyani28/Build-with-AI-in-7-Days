#User-specific questions ("my orders", "order status") must come from ecommerce.db via LangChain's SQL toolkit — not from RAG or hallucination.
from pathlib import Path

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

def get_database():
    """
    Load ecommerce SQLite database.
    """
    root = Path(__file__).resolve().parents[1]
    db_path = root / "ecommerce.db"
    return SQLDatabase.from_uri(
        f"sqlite:///{db_path}"
    )


def get_sql_tools():
    """
    Create SQL tools for ecommerce queries.
    """
    db = get_database()
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )
    toolkit = SQLDatabaseToolkit(
        db=db,
        llm=llm,
    )
    return toolkit.get_tools()

##test: uv run python -c "from support_chatbot.sql_tools import get_sql_tools; print([t.name for t in get_sql_tools()])"