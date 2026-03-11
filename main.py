import os
import pyodbc
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import socket

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")

    if not server or not database:
        raise RuntimeError("Variáveis DB_SERVER e DB_NAME não configuradas.")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        "Authentication=ActiveDirectoryManagedIdentity"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    return pyodbc.connect(conn_str)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Pessoas")
        rows = cursor.fetchall()
        db.close()

        pessoas = [{"id": r[0], "nome": r[1], "idade": r[2]} for r in rows]

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "pessoas": pessoas, "mensagem": None}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pessoas-form")
def create_people_form(
    id: int = Form(...),
    nome: str = Form(...),
    idade: int = Form(...)
):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Pessoas (id, nome, idade) VALUES (?, ?, ?)",
            (id, nome, idade)
        )
        db.commit()
        db.close()

        return RedirectResponse(url="/", status_code=303)
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

        return [{"id": r[0], "nome": r[1], "idade": r[2]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/debug-env")
def debug_env():
    return {
        "DB_SERVER": os.getenv("DB_SERVER"),
        "DB_NAME": os.getenv("DB_NAME"),
        "WEBSITE_HOSTNAME": os.getenv("WEBSITE_HOSTNAME"),
    }
@app.get("/debug-sql")
def debug_sql():
    server = os.getenv("DB_SERVER")
    try:
        with socket.create_connection((server, 1433), timeout=10):
            return {"ok": True, "server": server, "port": 1433}
    except Exception as e:
        return {"ok": False, "server": server, "port": 1433, "error": str(e)}

@app.get("/debug-odbc")
def debug_odbc():
    return {
        "drivers": pyodbc.drivers()
    }