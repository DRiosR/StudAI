from fastapi import FastAPI
app = FastAPI()

@app.get("/secret")
def secret():
    return {"secret": "lab-secret-123"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("internal_service:app", host="127.0.0.1", port=8080, log_level="info")
