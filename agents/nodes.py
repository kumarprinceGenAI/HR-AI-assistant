import logging
from typing import TypedDict, List, Dict, Annotated
import operator
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from qdrant_client.http import models

from config.settings import settings

logger = logging.getLogger(__name__)

def add_messages(left: list, right: list):
    """Reducer for messages to accumulate history."""
    return left + right

class GraphState(TypedDict):
    chat_history: Annotated[List[Dict[str, str]], add_messages]
    query: str
    username: str
    user_role: str
    documents: List[Document]
    context: str
    answer: str
    retry_count: int
    retry: bool
    is_escalation: bool

def retriever_node(state: GraphState, vector_store):
    query = state["query"]
    user_role = state.get("user_role", "employee")
    retry_count = state.get("retry_count", 0)

    # Better dynamic k (no cap)
    k = 3 + (retry_count * 3)
    logger.info(f"Query: {query} (Role: {user_role}, k={k})")

    # Qdrant strict filter using RBAC
    rbac_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.allowed_roles",
                match=models.MatchValue(value=user_role)
            )
        ]
    )

    docs = vector_store.similarity_search(query, k=k, filter=rbac_filter)
    logger.info(f"Retrieved {len(docs)} documents securely passing '{user_role}' access limits")

    context = ""
    filtered_docs = []

    for i, doc in enumerate(docs):
        section = doc.metadata.get("section", "Unknown")
        policy_id = doc.metadata.get("policy_id", "N/A")

        filtered_docs.append(doc)
        context += f"\n### POLICY: {section} ({policy_id})\n{doc.page_content}\n"

    logger.info(f"Filtered to {len(filtered_docs)} relevant documents")

    return {
        "documents": filtered_docs,
        "context": context
    }

def validation_node(state: GraphState):
    logger.info("Starting validation...")
    retry_count = state.get("retry_count", 0)

    # HARD STOP
    if retry_count >= 2:
        logger.warning("Max retries reached -> forcing proceed")
        return {"retry": False, "retry_count": retry_count}

    llm = ChatGoogleGenerativeAI(
        model=settings.PRIMARY_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )

    query = state["query"]
    context = state.get("context", "")
    user_role = state.get("user_role", "employee")

    prompt = f"""
Question: {query}
User Role Access: {user_role}

Context:
{context}

Is the provided context enough to answer the question securely? Answer YES or NO only.
If there is NO context because of secure access limits, answer YES so the flow can terminate without trying to fetch sensitive docs again.
"""
    response = llm.invoke(prompt)
    decision = response.content.strip().upper()

    if "NO" in decision:
        logger.info("RETRY triggered")
        return {"retry": True, "retry_count": retry_count + 1}

    logger.info("PROCEED triggered")
    return {"retry": False, "retry_count": retry_count}

def llm_node(state: GraphState):
    logger.info("Generating final answer...")

    llm = ChatGoogleGenerativeAI(
        model=settings.PRIMARY_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.3
    )

    query = state["query"]
    context = state["context"]
    chat_history = state.get("chat_history", [])

    history_str = ""
    for msg in chat_history:
        history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

    prompt = f"""
You are a highly secure Enterprise HR assistant. Answer ONLY using the provided context.

If the context is empty, respond precisely with: "You do not have the required access role to view this information or it does not exist."

Your answer MUST:
- Be a single professional sentence or paragraph.
- Include policy name and policy ID in format: (HR-POL-XXX) when applicable.

Context provided explicitly authorized for this user:
{context}

Conversation History:
{history_str}

User Question:
{query}

HR Assistant Answer:
"""
    response = llm.invoke(prompt)
    answer = response.content.strip()

    logger.info("Answer generated successfully")

    return {
        "answer": answer,
        "chat_history": [
            {"role": "user", "content": query},
            {"role": "assistant", "content": answer}
        ]
    }

def api_node(state: GraphState):
    logger.info("Routing to Agentic Tools DB Path...")

    from langgraph.prebuilt import create_react_agent
    from agents.tools import HR_TOOLS

    llm = ChatGoogleGenerativeAI(
        model=settings.PRIMARY_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=0.1
    )

    api_agent = create_react_agent(llm, tools=HR_TOOLS)
    
    query = state["query"]
    username = state.get("username", "unknown")
    chat_history = state.get("chat_history", [])

    history_str = ""
    for msg in chat_history:
        history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

    # Securely append the underlying verified username to the AI prompt context
    prompt = f"""
The authenticated user asking this question is '{username}'. Please strictly use this username if querying tools for personal HR data.

Conversation History:
{history_str}

Question: {query}
"""
    
    result = api_agent.invoke({"messages": [("user", prompt)]})
    
    last_msg = result["messages"][-1]
    final_answer = ""
    if isinstance(last_msg.content, list):
        for block in last_msg.content:
            if isinstance(block, dict) and "text" in block:
                final_answer += block["text"]
            elif isinstance(block, str):
                final_answer += block
    else:
        final_answer = str(last_msg.content)
        
    if not final_answer.strip():
        final_answer = "Data retrieved successfully via internal tools."
        
    logger.info("Tool execution successfully generated answer.")
    
    return {
        "answer": final_answer,
        "chat_history": [
            {"role": "user", "content": query},
            {"role": "assistant", "content": final_answer}
        ]
    }

def escalate_node(state: GraphState):
    logger.warning("Routing to HUMAN ESCALATION path. AI text generation suspended.")
    
    from data.tickets import create_ticket
    query = state["query"]
    username = state.get("username", "unknown")
    
    ticket_id = create_ticket(username, query)
    
    # Pre-canned safe response 
    final_answer = f"I understand this is a sensitive matter. I have bypassed my standard processing and safely escalated your issue directly to a human HR representative for review. Your reference number is **{ticket_id}**. Someone will contact you shortly."
    
    return {
        "answer": final_answer,
        "is_escalation": True,
        "chat_history": [
            {"role": "user", "content": query},
            {"role": "assistant", "content": final_answer}
        ]
    }