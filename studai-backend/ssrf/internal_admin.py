from fastapi import FastAPI
app = FastAPI()

@app.get("/config")
def config():
    return {"admin_mode": True, "apiKey": "admin-lab-key"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("internal_admin:app", host="127.0.0.1", port=9001, log_level="info")
