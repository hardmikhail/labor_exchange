from repositories.response_repository import ResponseRepository


class ResponseService:
    def __init__(self, response_repository: ResponseRepository):
        self.response_repository = response_repository
