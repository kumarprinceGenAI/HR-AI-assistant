from ingestion.pipeline import process_pdf
from retrieval.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store
)

file_path = "data/docs_pdf/employee_handbook_enterprise_v3.pdf"

# Step 1: Process documents
documents = process_pdf(file_path)

# Step 2: Create vector store
vector_store = create_vector_store(documents)

# Step 3: Save
save_vector_store(vector_store)

print("Index saved.\n")

# Step 4: Load
vector_store = load_vector_store()

print("Index loaded.\n")

# Step 5: Search
query = "leave policy"

results = vector_store.similarity_search(query, k=3)

print("----- RESULTS -----\n")

for res in results:
    print("TEXT:\n", res.page_content)
    print("METADATA:\n", res.metadata)
    print("\n----------------\n")