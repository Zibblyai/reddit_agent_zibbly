from fastapi import FastAPI, Request
import uvicorn
from reddit-agent import run_reddit_agent  # assuming this is your agent function

app = FastAPI()

@app.post("/run")
async def run_agent(request: Request):
    body = await request.json()
    query = body.get("query", "")
    result = run_reddit_agent(query)
    return {"response": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
