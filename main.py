# main.py
from fastapi import FastAPI
from reddit_agent import main as run_reddit_agent

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ready"}

@app.post("/run")
def run():
    run_reddit_agent()
    return {"status": "Reddit agent ran"}
