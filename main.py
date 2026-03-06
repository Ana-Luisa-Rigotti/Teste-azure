import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text

app = FastAPI()

engine = None

@app.on_event("startup")
def startup():
    global engine
    conn_str = os.getenv("SQL_CONNECTION_STRING")
    if not conn_str:
        raise RuntimeError("SQL_CONNECTION_STRING não configurada.")
    engine = create_engine(conn_str, pool_pre_ping=True)

@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
        return {"db_ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))