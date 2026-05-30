from fastapi import FastAPI

from app.modules.auth.router import router as auth_router

app = FastAPI(title="AI WhatsApp Chatbot E-Commerce API")
app.include_router(auth_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello FastAPI"}
