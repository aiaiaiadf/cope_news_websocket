from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI in Docker!"}

if __name__ == "__main__":
    import uvicorn
    # 绑定到所有接口（包括宿主机网络）
    uvicorn.run(app, host="0.0.0.0", port=8000)
