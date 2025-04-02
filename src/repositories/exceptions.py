class RepositoryError(Exception):
    """Ошибка репозитория"""


class UniqueError(RepositoryError):
    """Ошибка уникальности"""


class EntityNotFoundError(RepositoryError):
    """Сущность не найдена"""
