from ..account.user import User
from ..components import feedback

class Manager(User):
    def __init__(self, data, sessionId):
        #super().__init__(data, sessionId)
        self.functions = [
            "request_edit_user_account",
            "request_order_details",
            "request_view_feedbacks"
        ]
        pass

    # Client requested event
    def request_edit_user_account(self, requestKind: str, *arg):
        if requestKind == "EditUserCredentials":
            # Do something
            pass
        elif requestKind == "EditFirstName":
            # Do something3e
            pass
        elif requestKind == "EditLastName":
            # Do something
            pass
        elif requestKind == "EditEmail":
            # Do something
            pass

    def request_order_details(self, ):
        pass

    def request_view_feedbacks(self, dish: str):
        feedback.view_dishes()
