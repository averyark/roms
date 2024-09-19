from ..account.user import User

class Customer(User):
    def __init__(self, data, sessionId):
        super().__init__(data, sessionId)
