from ..account.user import User
from ..components import feedback

def review(self: 'User', reviewStar: int, reivewDescription: str):
        feedback.review()
