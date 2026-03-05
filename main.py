from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():

    return {"ok": True, "msg": "Deploy GitHub -> Azure funcionando 😌"}

