from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from phase_3.pipeline import MutualFundRAG
import uvicorn
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Mutual Fund RAG API")

# Initialize RAG Pipeline
try:
    rag = MutualFundRAG()
except Exception as e:
    print(f"Error initializing RAG: {e}")
    rag = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/")
def read_root():
    return FileResponse("phase_5/static/index.html")

# Mount static files (must be after root route to prioritize index.html)
app.mount("/static", StaticFiles(directory="phase_5/static"), name="static")

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if rag is None:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized. Check API keys and vector store.")
    
    try:
        result = rag.ask(request.message)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
