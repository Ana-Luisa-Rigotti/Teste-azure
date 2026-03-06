import os
import pymssql
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates #integrar com o front

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
            "INSERT INTO Pessoas (id, nome, idade) VALUES (%s, %s, %s)",
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