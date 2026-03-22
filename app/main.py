# from db import create_db_and_tables
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routers import accounts, transactions
from services.accounts import AccountNotFoundException


app = FastAPI()
app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")


# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


@app.exception_handler(AccountNotFoundException)
async def account_not_found_handler(_, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Account with id {exc.value} not found"},
    )
