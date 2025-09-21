from fastapi import FastAPI

app = FastAPI(title="Pokedex API", description="Hello World - Initial Setup")

@app.get("/")
def read_root():
    return {"message": "Hello World from Pokedex API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)