import os
import requests
from dotenv import load_dotenv

load_dotenv(verbose=True)


class Churchsuite:

    BASE_URL = "https://api.churchsuite.co.uk/v1"
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Account": os.getenv("CHURCHSUITE_ACCOUNT_NAME").encode("utf-8"),
        "X-Application": os.getenv("CHURCHSUITE_APP_NAME").encode("utf-8"),
        "X-Auth": os.getenv("CHURCHSUITE_API_KEY").encode("utf-8"),
    }

    def make_request(self, method, path, data=None):
        kwargs = {"headers": self.DEFAULT_HEADERS}
        if data:
            kwargs["data"] = data
        response = requests.request(method, f"{self.BASE_URL}{path}", **kwargs)
        if response.ok:
            return response.json()

    def get(self, path):
        return self.make_request("GET", path)

    def post(self, path, data):
        return self.make_request("POST", path, data=data)

    def get_event_signups(self, event_id):
        data = self.get(f"/calendar/event/{event_id}/signups?per_page=200")
        return data["signups"]


churchsuite = Churchsuite()
