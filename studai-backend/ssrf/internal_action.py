from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Action(BaseModel):
    op: str

@app.post("/action")
def action(a: Action):
    # DO NOT actually perform actions — this just simulates an action endpoint
    return {"status": "would perform", "op": a.op}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("internal_action:app", host="127.0.0.1", port=8083, log_level="info")
