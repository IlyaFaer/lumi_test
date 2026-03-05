from fastapi import FastAPI
from routers import accounts, transactions

app = FastAPI()
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.get("/")
def index():
    return {"message": "Hello, World!"}
