from fastapi import FastAPI
from src.api import chat, uploads, embedding
from src.config.settings import env
from src.model import Base, engine


def setup_app(app: FastAPI):
    # DB
    Base.metadata.create_all(engine)

    # Routes
    app.include_router(uploads.upload_router)
    app.include_router(chat.chat_router)
    app.include_router(embedding.embedding_router)


app = FastAPI(root_path="/api/v1")
setup_app(app)


if __name__ == '__main__':
    import uvicorn
    from src.config.settings import env

    uvicorn.run("main:app", host=env.app_host, reload=True, workers=1)
