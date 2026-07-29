#agent that chooses tools

from langchain.agents import create_agent
from support_chatbot.rag_tool import search_policies
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

#compiled staegraph
def create_support_agent():
    """
    Create the customer support agent.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
    )
    system_prompt = """
    You are an AI customer support assistant for an e-commerce company.

    Use the search_policies tool ONLY when the user asks about:
    - return policy
    - shipping policy
    - refund policy
    - cancellation policy
    - warranty
    - FAQs covered in the company policy documents
    Answer using the information returned by the tool.

    Do not use the tool for:
    - greetings
    - casual conversation
    - simple questions that do not require company policies

    If the tool does not provide enough information, say you could not
    find the relevant company policy instead of making one up.
    """
    return create_agent(
        model=llm,
        tools=[search_policies],
        system_prompt=system_prompt,
    )

def get_agent():
    """
    Return a cached support agent.
    """
    global _agent
    if _agent is None:
        _agent = create_support_agent()
    return _agent
