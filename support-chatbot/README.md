# 🤖 DeepDev Support Chatbot

A beginner-friendly AI chatbot built step by step using **Streamlit + LangChain + OpenAI**.

The goal of this project is to start with a simple conversational chatbot and gradually add advanced AI features:

- ✅ Basic chatbot conversation
- 🔜 Web search tools
- 🔜 LangChain tools
- 🔜 Middleware
- 🔜 RAG (Retrieval Augmented Generation)
- 🔜 Vector databases
- 🔜 Conversation memory
- 🔜 Agents
- 🔜 Production deployment

  # 📌 Project Roadmap

## Day 1: Basic Chatbot ✅

Current features:

- Streamlit UI
- OpenAI LLM integration
- LangChain message handling
- Conversation history using Streamlit session state


## Day 2: Add Database, Role based login and langchain chain

### LangChain Prompt Templates & LCEL Chain
- Added `ChatPromptTemplate` for structured prompts.
- Added:
  - System message for assistant behaviour.
  - `MessagesPlaceholder` for maintaining chat history.
  - Human message template for user input.
- Implemented LCEL chain
  
### Python Package Structure
Converted the project into a Python package.
- pyproject.toml
- support_chatbot/
│
├── init.py
├── supportApp.py
├── db_init.py
└── auth.py

### SQLite Database Initialization
- ecommerce.db
- ecommerce_setup.sql
- db_init.py
### Authentication Module
-auth.py

## Day 3: Multi context spport(In-Memory)

Flow:
  Login
    │
    ▼
Start New Conversation
   │
   ▼
UUID Generated
   │
   ▼
messages = [AIMessage(...)]
   │
   ▼
conversations[UUID] = messages
   │
   ▼
Sidebar lists UUIDs
   │
   ▼
Select UUID
   │
   ▼
load_conversation(UUID)
   │
   ▼
Chat History Restored

##Day 4: Doc loader to VectorDB(chroma), RAG using chunks,embeddings & Agent for select tools-LangGraph

#LangGraph agent flow
User
 |
 | prompt
 v
CompiledStateGraph (agent)
 |
 | decides
 |
 +---- simple greeting
 |        |
 |        v
 |      LLM response
 |
 +---- policy question
          |
          v
     search_policies tool
          |
          v
     ChromaDB retrieval
          |
          v
        LLM answer

