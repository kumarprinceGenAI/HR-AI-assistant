from langchain_community.document_loaders import PyMuPDFLoader


def load_pdf(file_path: str):
    """
    Load PDF using LangChain PyMuPDFLoader
    Returns list of Document objects
    """
    loader = PyMuPDFLoader(file_path)

    documents = loader.load()

    return documents