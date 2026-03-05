from db import create_db_and_tables
from fastapi import FastAPI
from routers import accounts, transactions

app = FastAPI()
app.include_router(accounts.router)
app.include_router(transactions.router)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def index():
    return {"message": "Hello, World!"}
