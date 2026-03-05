from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
<<<<<<< HEAD
    return {"ok": True, "msg": "Deploy GitHub -> Azure funcionando 😌"}
=======
    return {"status": "funcionando"}
>>>>>>> 5e405a1ff0c6ac239705c8fe378b09fdb0066a13
