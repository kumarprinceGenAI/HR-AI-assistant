import logging
import uvicorn
import os
import uuid
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager

from config.settings import settings
from retrieval.vector_store import load_vector_store
from agents.graph import build_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

ml_models = {}

# MOCK IDENTITY DATABASE
USERS_DB = {
    "alice": {"password": "password", "role": "employee", "name": "Alice (Junior)"},
    "bob": {"password": "password", "role": "manager", "name": "Bob (Manager)"},
    "charlie": {"password": "password", "role": "executive", "name": "Charlie (VP)"}
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Qdrant vector store on startup...")
    try:
        vector_store = load_vector_store()
        graph = build_graph(vector_store)
        ml_models["graph"] = graph
        logger.info("Graph with Memory and RBAC initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize vector store or graph: {e}")
        logger.warning("Make sure to run 'python ingest.py' first if Qdrant is missing!")
    yield
    ml_models.clear()

app = FastAPI(title="HR AI Assistant API", lifespan=lifespan)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_ui():
    return FileResponse("static/index.html")

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    user = USERS_DB.get(request.username.lower())
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    payload = {
        "sub": request.username.lower(),
        "role": user["role"],
        "name": user["name"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "role": user["role"], "name": user["name"]}

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer ") or authorization == "Bearer null":
        # Fallback to Guest access gracefully
        logger.info("Proceeding as unauthenticated Guest.")
        return {"sub": "guest", "role": "guest", "name": "Guest (Unauthenticated)"}
        
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    query: str
    answer: str
    session_id: str
    is_escalation: bool = False

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    graph = ml_models.get("graph")
    
    if not graph:
        raise HTTPException(status_code=503, detail="AI Graph missing database. Run python ingest.py.")
        
    session_id = request.session_id or str(uuid.uuid4())
    user_role = current_user.get("role", "employee")
        
    try:
        logger.info(f"Received query: {request.query} [Session: {session_id}, Role: {user_role}]")
        
        config = {"configurable": {"thread_id": session_id}}
        
        result = graph.invoke({
            "query": request.query,
            "username": current_user.get("sub", "unknown"),
            "retry_count": 0,
            "user_role": user_role
        }, config=config)
        
        return ChatResponse(
            query=request.query,
            answer=result["answer"],
            session_id=session_id,
            is_escalation=result.get("is_escalation", False)
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="I apologize, but I encountered an unexpected system error while processing your request. Please try again later.")

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)