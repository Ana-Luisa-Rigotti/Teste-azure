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

@app.post("/pessoas")
def create_people(id: int, nome: str, idade: int):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
        "INSERT INTO Pessoas (id, nome, idade) VALUES (?, ?, ?)",
        (id, nome, idade))
        db.commit()
        db.close()
        return {"message": "Pessoa cadastrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pessoas")
def list_people():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Pessoas")
        rows = cursor.fetchall()
        db.close()

        return [{"id": r[0], "nome": r[1], "idade": r[3]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))