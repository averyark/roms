from ..account.user import User
from ..components import feedback

class Customer(User):
    def __init__(self, data, sessionId):
        #super().__init__(data, sessionId)
        pass

    def review(reviewStar: int, reivewDescription: str):
        feedback.review()
