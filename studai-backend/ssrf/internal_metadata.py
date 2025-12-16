from fastapi import FastAPI
app = FastAPI()

@app.get("/meta")
def meta():
    return {"token": "lab-metadata-token", "instance": "demo-instance"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("internal_metadata:app", host="127.0.0.1", port=8082, log_level="info")
