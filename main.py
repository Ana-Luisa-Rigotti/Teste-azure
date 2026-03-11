import os
import struct
import pyodbc
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SQL_COPT_SS_ACCESS_TOKEN = 1256
TOKEN_SCOPE = "https://database.windows.net/.default"


def get_db():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    website_hostname = os.getenv("WEBSITE_HOSTNAME")

    if not server or not database:
        raise RuntimeError("Variáveis DB_SERVER e DB_NAME não configuradas.")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
    )

    # Se estiver rodando no Azure App Service, usa Managed Identity
    if website_hostname:
        conn_str += "Authentication=ActiveDirectoryMsi;"
        return pyodbc.connect(conn_str)

    # Se estiver rodando localmente ou no Docker, usa token da conta Azure logada
    credential = DefaultAzureCredential()
    access_token = credential.get_token(TOKEN_SCOPE).token
    token_bytes = access_token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)

    return pyodbc.connect(
        conn_str,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct}
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