import os
import pymssql
from fastapi import FastAPI, HTTPException

app = FastAPI()

def get_db():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([server, database, user, password]):
        raise RuntimeError("Variáveis DB_* não configuradas no Azure.")

    return pymssql.connect(
        server=server,
        user=user,
        password=password,
        database=database
    )

@app.get("/")
def home():
    return {"message": "API funcionando"}

@app.post("/news")
def create_news(title: str):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO news (title) VALUES (%s)", (title,))
        db.commit()
        db.close()
        return {"message": "Notícia salva"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news")
def list_news():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, title FROM news")
        rows = cursor.fetchall()
        db.close()

        return [{"id": r[0], "title": r[1]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))