from fastapi import FastAPI
from app.routers import items, imports, reports, picklists, logs

app = FastAPI()
app.include_router(items.router)
app.include_router(imports.router)
app.include_router(reports.router) #, prefix="/reports", tags=["reports"])
app.include_router(picklists.router)
app.include_router(logs.router)

@app.get("/")
def read_root():
    return {"status": "OK"}

