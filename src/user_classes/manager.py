from ..account.user import User

class Manager(User):
    def __init__(self, data, sessionId):
        super().__init__(data, sessionId)

    # Client requested event
    def request_edit_user_account(requestKind: str, *arg):
        if requestKind == "EditUserCredentials":
            # Do something
            pass
        elif requestKind == "EditFirstName":
            # Do something
            pass
        elif requestKind == "EditLastName":
            # Do something
            pass
        elif requestKind == "EditEmail":
            # Do something
            pass

    def request_order_details():
        pass
