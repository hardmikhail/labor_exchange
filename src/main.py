import uvicorn
from dependency_injector import providers
from fastapi import FastAPI

from config import DBSettings
from config.common import env_file_path
from dependencies.containers import RepositoriesContainer, ServicesContainer
from storage.sqlalchemy.client import SqlAlchemyAsync
from web.routers import auth_router, job_router, response_router, user_router


def create_app():
    repo_container = RepositoriesContainer()
    settings = DBSettings(_env_file=env_file_path)

    # выбор синхронных / асинхронных реализаций
    repo_container.db.override(
        providers.Factory(
            SqlAlchemyAsync,
            pg_settings=settings,
        ),
    )
    services_container = ServicesContainer()
    services_container.init_resources()
    services_container.repositories_container.override(repo_container)

    # инициализация приложения
    app = FastAPI()
    app.container = services_container

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(job_router)
    app.include_router(response_router)

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
