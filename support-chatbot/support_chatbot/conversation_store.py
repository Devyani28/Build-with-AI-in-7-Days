import json
import sqlite3
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

#create conversation.db
def ensure_conv_store():
    root = Path(__file__).resolve().parents[1]
    db_path = root / "conversations.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                messages TEXT NOT NULL
            )
        """)
        conn.commit()
        # print("Conversation DB:", db_path)
    return db_path
# ensure_conv_store()

#list of messages → JSON
def serialize_messages(messages):
    data = []
    for message in messages:
        data.append({
            "role": "human" if isinstance(message, HumanMessage) else "ai",
            "content": message.content
        })
    return json.dumps(data)

#JSON string → list of HumanMessage / AIMessage
def deserialize_messages(data):
    messages = []
    for item in json.loads(data):
        if item["role"] == "human":
            messages.append(
                HumanMessage(content=item["content"])
            )
        else:
            messages.append(
                AIMessage(content=item["content"])
            )
    return messages


def save_conversation(conv_id, user_email, messages): #chat_round, start_conversation
    db_path = ensure_conv_store()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO conversations
            (id, user_email, messages)
            VALUES (?, ?, ?)
            """,
            (
                conv_id,
                user_email,
                serialize_messages(messages)
            )
        )
        conn.commit()

def load_conversations(user_email):
    db_path = ensure_conv_store()
    conversations = {}
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, messages
            FROM conversations
            WHERE user_email = ?
            """,
            (user_email,)
        ).fetchall()
    for conv_id, data in rows:
        conversations[conv_id] = deserialize_messages(data)
    return conversations