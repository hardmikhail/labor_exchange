from dependency_injector import containers, providers

from interfaces.i_sqlalchemy import ISQLAlchemy
from repositories import JobRepository, ResponseRepository, UserRepository
from services import JobService, ResponseService, UserService


class RepositoriesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["services", "dependencies"])

    db = providers.AbstractFactory(ISQLAlchemy)

    user_repository = providers.Factory(
        UserRepository,
        session=db.provided.get_db,
    )

    job_repository = providers.Factory(
        JobRepository,
        session=db.provided.get_db,
    )

    response_repository = providers.Factory(
        ResponseRepository,
        session=db.provided.get_db,
    )


class ServicesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["web.routers"])
    repositories_container = providers.Container(RepositoriesContainer)

    user_service = providers.Factory(
        UserService,
        user_repository=repositories_container.user_repository,
    )

    job_service = providers.Factory(
        JobService,
        job_repository=repositories_container.job_repository,
    )

    response_service = providers.Factory(
        ResponseService,
        response_repository=repositories_container.response_repository,
    )
