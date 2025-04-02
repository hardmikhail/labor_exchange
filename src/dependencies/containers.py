from dependency_injector import containers, providers

from interfaces.i_sqlalchemy import ISQLAlchemy
from repositories import UserRepository
from services import UserService


class RepositoriesContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["web.routers", "dependencies"])

    db = providers.AbstractFactory(ISQLAlchemy)

    user_repository = providers.Factory(
        UserRepository,
        session=db.provided.get_db,
    )

    user_service = providers.Factory(UserService, user_repository=user_repository)
