from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import items, imports, reports, picklists, logs, auth

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # <-- autorise Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(items.router)
app.include_router(imports.router)
app.include_router(reports.router) #, prefix="/reports", tags=["reports"])
app.include_router(picklists.router)
app.include_router(logs.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"status": "OK"}

