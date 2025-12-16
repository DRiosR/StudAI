from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/go")
def go():
    # redirects to the internal service secret - demo only
    return RedirectResponse(url="http://127.0.0.1:8080/secret", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("redirector:app", host="127.0.0.1", port=8085, log_level="info")
