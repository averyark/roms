# @fileName: example-client.py
# @creation_date: 22/09/2024
# @authors: averyark

from requests import api
from pydantic import BaseModel
import requests.auth

url = "http://127.0.0.1:8000"

session_token = None

# Collection of APIs
class USE_APIS:
    ACCOUNT_LOGIN = f"{url}/account/login"
    ACCOUNT_SIGNUP = f"{url}/account/signup"
    ACCOUNT_EDIT_PASSWORD = f"{url}/account/edit/credentials/"

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


def get_new_session_token(user: str, credentials: str):
    response = api.get(
        url=USE_APIS.ACCOUNT_LOGIN,
        params={
            "email": user,
            "password": credentials
        }
    )
    response_json = response.json()

    if response.status_code == 200:
        return response_json.get("access_token")
    else:
        err_detail = response_json.get("detail")
        print(f"Login failed. Status code: {response.status_code} Detail: {err_detail}")

def edit_others_password(user_id: str, new_credentials: str):
    response = api.post(
        url=USE_APIS.ACCOUNT_EDIT_PASSWORD,
        params={
            "user_id": user_id,
            "new_credentials": new_credentials
        },
        auth=BearerAuth(session_token)
    )
    response_json = response.json()

    print(f"Status code: {response.status_code} Response body: {response_json}")


session_token = get_new_session_token("customer1@gmail.com", "somepass12")

# This will fail because user "customer1@gmail.com" lacks Manager permission which is required for the edit other credentials api
edit_others_password(1, "newpass@123")
