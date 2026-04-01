from retrieval.retriever import retrieve_documents


def build_context(documents):
    context = ""

    for doc in documents:
        section = doc.metadata.get("section", "Unknown")
        policy_id = doc.metadata.get("policy_id", "N/A")

        context += f"""
            [Section: {section} | Policy ID: {policy_id}]
            {doc.page_content}

            """

    return context


def query_pipeline(vector_store, query: str):
    """
    Full query pipeline (without LLM for now)
    """

    # Step 1: Retrieve
    docs = retrieve_documents(vector_store, query)

    # Step 2: Build context
    context = build_context(docs)

    return {
        "query": query,
        "context": context,
        "documents": docs
    }