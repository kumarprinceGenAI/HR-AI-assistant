import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.nodes import retriever_node, llm_node, validation_node, api_node, escalate_node, GraphState

logger = logging.getLogger(__name__)

def route_query(state: GraphState):
    query = state["query"]
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from config.settings import settings
    
    llm = ChatGoogleGenerativeAI(
        model=settings.PRIMARY_MODEL,
        api_key=settings.GOOGLE_API_KEY,
        temperature=0
    )
    
    prompt = f"""
Analyze the following user question: "{query}"

You are a strict triaging router for an enterprise HR system. You must output exactly ONE word from the following choices based on intent:

1. ESCALATE: If the question contains severely sensitive topics (e.g., "harassment", "assault", "sue", "lawyer", "quit", "manager abuse", "illegal") OR explicitly asks to "talk to a human" or "speak to a representative".
2. API: If the question asks for personal employee data (e.g., "my PTO", "my salary", "who am I", "my profile", "my benefits", "health plan", "my equipment", "what laptop", "performance rating").
3. RAG: If the question asks about general company policies, standard guidelines, benefits summaries, or generic rules.

Response:
"""
    response = llm.invoke(prompt)
    decision = response.content.strip().upper()
    
    logger.info(f"Semantic Router decision: {decision}")
    
    if "ESCALATE" in decision:
        return "escalate"
    elif "API" in decision:
        return "api"
        
    return "retrieve"

def build_graph(vector_store):
    builder = StateGraph(GraphState)
    memory = MemorySaver()

    builder.add_node("retrieve", lambda state: retriever_node(state, vector_store))
    builder.add_node("validate", validation_node)
    builder.add_node("llm", llm_node)
    builder.add_node("api", api_node)
    builder.add_node("escalate", escalate_node)

    # 3-way route semantic flow
    builder.set_conditional_entry_point(
        route_query,
        {
            "retrieve": "retrieve",
            "api": "api",
            "escalate": "escalate"
        }
    )

    builder.add_edge("retrieve", "validate")

    def route_retry(state):
        retry = state.get("retry", False)
        logger.info(f"Retry flag: {retry}")
        if retry:
            return "retrieve"
        return "llm"

    builder.add_conditional_edges("validate", route_retry)
    
    builder.add_edge("llm", END)
    builder.add_edge("api", END)
    builder.add_edge("escalate", END)

    graph = builder.compile(checkpointer=memory)

    return graph