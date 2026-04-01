import logging
from ingestion.pipeline import process_pdf
from retrieval.vector_store import create_vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    file_path = "data/docs_pdf/employee_handbook_enterprise_v3.pdf"
    
    logger.info(f"Starting ingestion process for {file_path}")
    
    try:
        # Step 1: Prepare documents
        documents = process_pdf(file_path)
        logger.info(f"Processed {len(documents)} document chunks.")
        
        # Step 2: Vector store
        logger.info("Creating Qdrant vector store...")
        create_vector_store(documents)
        
        logger.info("Vector store created and saved successfully to disk.")
    except FileNotFoundError:
        logger.error(f"Could not find PDF file at {file_path}. Please ensure it exists.")
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")

if __name__ == "__main__":
    main()
