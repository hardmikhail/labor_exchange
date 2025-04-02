class UserAlreadyExistsError(Exception):
    """Пользователь уже существует в системе"""


class UserNotFoundError(Exception):
    """Пользователь не найден"""
