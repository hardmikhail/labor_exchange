from interfaces.i_repository import IRepositoryAsync


class ResponseService:
    def __init__(self, response_repository: IRepositoryAsync):
        self.response_repository = response_repository
