from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import GOOGLE_API_KEY, PRIMARY_MODEL

llm = ChatGoogleGenerativeAI(
    model=PRIMARY_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

response = llm.invoke("Explain leave policy in 1 sentence")

print(response.content)