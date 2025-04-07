class UserAlreadyExistsError(Exception):
    """Пользователь уже существует в системе"""


class UserNotFoundError(Exception):
    """Пользователь не найден"""


class JobNotFoundError(Exception):
    """Вакансия не найдена"""


class ResponseAlreadyExistsError(Exception):
    """Отклик уже существует в системе"""


class ResponseCreationError(Exception):
    """Ошибка создания отклика"""


class ResponseNotFoundError(Exception):
    """Отклик не найден"""
